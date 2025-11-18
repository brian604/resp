"""
Job scheduler for automated digest delivery.
"""

import logging
from datetime import time, datetime
from typing import Dict, Any

from telegram import Bot
from telegram.ext import ContextTypes

from resp import Resp
from resp.telegram_bot.config import BotConfig
from resp.telegram_bot import messages


logger = logging.getLogger(__name__)


class DigestScheduler:
    """Manages scheduled digest delivery for users."""

    def __init__(self, config: BotConfig):
        """
        Initialize scheduler.

        Args:
            config: Bot configuration
        """
        self.config = config

    @staticmethod
    async def send_scheduled_digest(context: ContextTypes.DEFAULT_TYPE):
        """
        Job callback to send scheduled digest.

        Args:
            context: Job context with user_id in job.data
        """
        job = context.job
        user_id = job.data['user_id']
        bot: Bot = context.bot

        try:
            # Load user profile and settings
            from resp.telegram_bot.handlers import RespHandlers
            handlers = RespHandlers(job.data['config'])

            profile = handlers._get_user_profile(user_id)
            settings = handlers._get_user_settings(user_id)

            if not profile:
                logger.warning(f"No profile found for user {user_id}, skipping digest")
                return

            # Create Resp instance
            resp = Resp()
            resp.set_research_profile(profile)

            # Fetch and rank papers
            papers = resp.fetch_daily_papers(days_back=1, max_papers=100)

            if papers.empty:
                await bot.send_message(
                    chat_id=user_id,
                    text="📭 No new papers today matching your interests.",
                    parse_mode='Markdown'
                )
                return

            threshold = settings.get('threshold', 6.5)
            max_papers = settings.get('max_papers', 10)

            ranked = resp.rank_by_relevance(papers, threshold=threshold)

            if ranked.empty:
                await bot.send_message(
                    chat_id=user_id,
                    text=messages.DIGEST_EMPTY,
                    parse_mode='Markdown'
                )
                return

            ranked = ranked.head(max_papers)

            # Generate digest
            digest_text = messages.DIGEST_HEADER.format(
                date=datetime.now().strftime('%Y-%m-%d'),
                total=len(ranked),
                threshold=threshold
            )

            # Add papers
            current_message = digest_text
            messages_to_send = []

            for idx, (_, paper) in enumerate(ranked.iterrows(), 1):
                paper_card = messages.format_paper_card(idx, paper.to_dict())

                if len(current_message) + len(paper_card) > 4000:
                    messages_to_send.append(current_message)
                    current_message = paper_card
                else:
                    current_message += paper_card

            messages_to_send.append(current_message)

            # Add footer
            scorer_stats = resp._relevance_scorer.get_stats() if hasattr(resp, '_relevance_scorer') else {}
            footer = messages.DIGEST_FOOTER.format(
                cost=scorer_stats.get('estimated_cost_usd', 0),
                tokens=scorer_stats.get('total_tokens', 0),
                model=scorer_stats.get('model', 'gpt-3.5-turbo')
            )
            messages_to_send[-1] += footer

            # Send messages
            for msg in messages_to_send:
                await bot.send_message(
                    chat_id=user_id,
                    text=msg,
                    parse_mode='Markdown',
                    disable_web_page_preview=True
                )

            # Update stats
            settings['total_digests'] = settings.get('total_digests', 0) + 1
            settings['papers_scored'] = settings.get('papers_scored', 0) + len(papers)
            settings['total_cost'] = settings.get('total_cost', 0.0) + scorer_stats.get('estimated_cost_usd', 0)
            settings['last_digest'] = datetime.now().isoformat()
            handlers._save_user_settings(user_id, settings)

            logger.info(f"Sent scheduled digest to user {user_id}: {len(ranked)} papers")

        except Exception as e:
            logger.error(f"Error sending scheduled digest to user {user_id}: {e}", exc_info=True)
            try:
                await bot.send_message(
                    chat_id=user_id,
                    text=messages.ERROR_GENERIC.format(error_message=str(e)),
                    parse_mode='Markdown'
                )
            except Exception:
                pass  # Don't fail if we can't send error message

    def schedule_user_digest(
        self,
        application,
        user_id: int,
        digest_time: str
    ):
        """
        Schedule daily digest for a user.

        Args:
            application: Application instance
            user_id: Telegram user ID
            digest_time: Time in HH:MM format (24-hour)
        """
        # Parse time
        try:
            hours, minutes = map(int, digest_time.split(':'))
            schedule_time = time(hour=hours, minute=minutes, second=0)
        except ValueError:
            raise ValueError(f"Invalid time format: {digest_time}")

        # Remove existing job if any
        job_name = f"digest_{user_id}"
        current_jobs = application.job_queue.get_jobs_by_name(job_name)
        for job in current_jobs:
            job.schedule_removal()

        # Schedule new job
        application.job_queue.run_daily(
            callback=self.send_scheduled_digest,
            time=schedule_time,
            data={
                'user_id': user_id,
                'config': self.config
            },
            name=job_name,
            chat_id=user_id
        )

        logger.info(f"Scheduled daily digest for user {user_id} at {digest_time}")

    def unschedule_user_digest(self, application, user_id: int):
        """
        Cancel scheduled digest for a user.

        Args:
            application: Application instance
            user_id: Telegram user ID
        """
        job_name = f"digest_{user_id}"
        current_jobs = application.job_queue.get_jobs_by_name(job_name)

        for job in current_jobs:
            job.schedule_removal()

        logger.info(f"Unscheduled digest for user {user_id}")

    def get_user_schedule(self, application, user_id: int) -> Dict[str, Any]:
        """
        Get schedule information for a user.

        Args:
            application: Application instance
            user_id: Telegram user ID

        Returns:
            Schedule info dict
        """
        job_name = f"digest_{user_id}"
        jobs = application.job_queue.get_jobs_by_name(job_name)

        if not jobs:
            return {
                'scheduled': False,
                'time': None,
                'next_run': None
            }

        job = jobs[0]
        return {
            'scheduled': True,
            'time': job.trigger.time.strftime('%H:%M'),
            'next_run': job.next_t.strftime('%Y-%m-%d %H:%M:%S') if job.next_t else None
        }
