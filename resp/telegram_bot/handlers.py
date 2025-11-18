"""
Command and conversation handlers for RESP Telegram bot.
"""

import os
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters
)

from resp import Resp
from resp.personalization import ResearchProfile
from resp.telegram_bot import messages
from resp.telegram_bot.config import BotConfig


# Conversation states
(
    PROFILE_CHOICE,
    PROFILE_NAME,
    PROFILE_CATEGORIES,
    PROFILE_PRIMARY,
    PROFILE_SECONDARY,
    PROFILE_EXCLUSIONS,
    SEARCH_QUERY,
) = range(7)


class RespHandlers:
    """Handler functions for RESP Telegram bot."""

    def __init__(self, config: BotConfig):
        """
        Initialize handlers.

        Args:
            config: Bot configuration
        """
        self.config = config
        self.resp_instances: Dict[int, Resp] = {}

    def _get_resp(self, user_id: int) -> Resp:
        """
        Get or create Resp instance for user.

        Args:
            user_id: Telegram user ID

        Returns:
            Resp instance
        """
        if user_id not in self.resp_instances:
            self.resp_instances[user_id] = Resp()
        return self.resp_instances[user_id]

    def _get_user_profile(self, user_id: int) -> ResearchProfile:
        """
        Load user's research profile.

        Args:
            user_id: Telegram user ID

        Returns:
            ResearchProfile instance or None
        """
        profile_path = self.config.get_user_profile_path(user_id)
        if profile_path.exists():
            return ResearchProfile.from_yaml(str(profile_path))
        return None

    def _save_user_profile(self, user_id: int, profile: ResearchProfile):
        """
        Save user's research profile.

        Args:
            user_id: Telegram user ID
            profile: ResearchProfile to save
        """
        profile_path = self.config.get_user_profile_path(user_id)
        profile.to_yaml(str(profile_path))

    def _get_user_settings(self, user_id: int) -> Dict[str, Any]:
        """
        Load user's bot settings.

        Args:
            user_id: Telegram user ID

        Returns:
            Settings dictionary
        """
        settings_path = self.config.get_user_settings_path(user_id)
        if settings_path.exists():
            import json
            with open(settings_path, 'r') as f:
                return json.load(f)
        return {
            'threshold': self.config.default_threshold,
            'max_papers': self.config.max_papers_per_digest,
            'schedule_time': None,
            'total_digests': 0,
            'papers_scored': 0,
            'total_cost': 0.0,
            'created_at': datetime.now().isoformat()
        }

    def _save_user_settings(self, user_id: int, settings: Dict[str, Any]):
        """
        Save user's bot settings.

        Args:
            user_id: Telegram user ID
            settings: Settings dictionary
        """
        settings_path = self.config.get_user_settings_path(user_id)
        import json
        with open(settings_path, 'w') as f:
            json.dump(settings, f, indent=2)

    # Command handlers

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        await update.message.reply_text(
            messages.WELCOME_MESSAGE,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        await update.message.reply_text(
            messages.HELP_MESSAGE,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )

    async def viewprofile(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /viewprofile command."""
        user_id = update.effective_user.id
        profile = self._get_user_profile(user_id)

        if not profile:
            await update.message.reply_text(messages.ERROR_NO_PROFILE)
            return

        # Format profile info
        profile_text = f"""
📋 **Your Research Profile**

**Name:** {profile.name}
**Email:** {profile.email or 'Not set'}

**ArXiv Categories:**
{', '.join(profile.arxiv_categories)}

**Primary Interests:**
{chr(10).join('• ' + interest for interest in profile.primary_interests)}

**Secondary Interests:**
{chr(10).join('• ' + interest for interest in profile.secondary_interests) if profile.secondary_interests else 'None'}

**Exclusions:**
{chr(10).join('• ' + exclusion for exclusion in profile.exclusions) if profile.exclusions else 'None'}

Use /profile to edit or /digest to get papers.
"""
        await update.message.reply_text(profile_text, parse_mode='Markdown')

    async def stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command."""
        user_id = update.effective_user.id
        profile = self._get_user_profile(user_id)
        settings = self._get_user_settings(user_id)

        if not profile:
            await update.message.reply_text(messages.ERROR_NO_PROFILE)
            return

        stats_text = messages.STATS_MESSAGE.format(
            profile_name=profile.name,
            categories=', '.join(profile.arxiv_categories),
            created_date=settings.get('created_at', 'Unknown')[:10],
            total_digests=settings.get('total_digests', 0),
            papers_scored=settings.get('papers_scored', 0),
            total_cost=settings.get('total_cost', 0.0),
            last_digest=settings.get('last_digest', 'Never'),
            threshold=settings.get('threshold', self.config.default_threshold),
            schedule_status='Enabled' if settings.get('schedule_time') else 'Disabled'
        )

        await update.message.reply_text(stats_text, parse_mode='Markdown')

    async def digest(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /digest command - generate personalized paper digest."""
        user_id = update.effective_user.id
        profile = self._get_user_profile(user_id)
        settings = self._get_user_settings(user_id)

        if not profile:
            await update.message.reply_text(messages.ERROR_NO_PROFILE)
            return

        # Check for API key
        if not os.getenv('OPENAI_API_KEY'):
            await update.message.reply_text(messages.ERROR_API_KEY)
            return

        # Send status message
        status_msg = await update.message.reply_text(messages.DIGEST_GENERATING)

        try:
            # Get Resp instance and set profile
            resp = self._get_resp(user_id)
            resp.set_research_profile(profile)

            # Fetch papers
            papers = resp.fetch_daily_papers(days_back=7, max_papers=100)

            if papers.empty:
                await status_msg.edit_text(messages.DIGEST_EMPTY)
                return

            # Update status
            await status_msg.edit_text(
                messages.DIGEST_SCORING.format(count=len(papers))
            )

            # Rank papers
            threshold = settings.get('threshold', self.config.default_threshold)
            max_papers = settings.get('max_papers', self.config.max_papers_per_digest)

            ranked = resp.rank_by_relevance(papers, threshold=threshold)

            if ranked.empty:
                await status_msg.edit_text(messages.DIGEST_EMPTY)
                return

            # Limit to max papers
            ranked = ranked.head(max_papers)

            # Generate digest message
            digest_text = messages.DIGEST_HEADER.format(
                date=datetime.now().strftime('%Y-%m-%d'),
                total=len(ranked),
                threshold=threshold
            )

            # Add paper cards (split if too long)
            current_message = digest_text
            messages_to_send = []

            for idx, (_, paper) in enumerate(ranked.iterrows(), 1):
                paper_card = messages.format_paper_card(idx, paper.to_dict())

                # Telegram message limit is 4096 chars
                if len(current_message) + len(paper_card) > 4000:
                    messages_to_send.append(current_message)
                    current_message = paper_card
                else:
                    current_message += paper_card

            messages_to_send.append(current_message)

            # Add footer to last message
            scorer_stats = resp._relevance_scorer.get_stats() if hasattr(resp, '_relevance_scorer') else {}
            footer = messages.DIGEST_FOOTER.format(
                cost=scorer_stats.get('estimated_cost_usd', 0),
                tokens=scorer_stats.get('total_tokens', 0),
                model=scorer_stats.get('model', 'gpt-3.5-turbo')
            )
            messages_to_send[-1] += footer

            # Delete status message
            await status_msg.delete()

            # Send all messages
            for msg in messages_to_send:
                await update.message.reply_text(
                    msg,
                    parse_mode='Markdown',
                    disable_web_page_preview=not self.config.enable_web_preview
                )

            # Update settings
            settings['total_digests'] = settings.get('total_digests', 0) + 1
            settings['papers_scored'] = settings.get('papers_scored', 0) + len(papers)
            settings['total_cost'] = settings.get('total_cost', 0.0) + scorer_stats.get('estimated_cost_usd', 0)
            settings['last_digest'] = datetime.now().isoformat()
            self._save_user_settings(user_id, settings)

        except Exception as e:
            await status_msg.edit_text(
                messages.ERROR_GENERIC.format(error_message=str(e))
            )

    async def threshold(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /threshold command."""
        user_id = update.effective_user.id
        settings = self._get_user_settings(user_id)

        if not context.args:
            current = settings.get('threshold', self.config.default_threshold)
            await update.message.reply_text(
                f"Current threshold: {current}/10\n\n"
                f"Usage: /threshold <value>\n"
                f"Example: /threshold 7.5"
            )
            return

        try:
            threshold = float(context.args[0])
            if not 1.0 <= threshold <= 10.0:
                raise ValueError("Threshold must be between 1.0 and 10.0")

            settings['threshold'] = threshold
            self._save_user_settings(user_id, settings)

            await update.message.reply_text(
                messages.THRESHOLD_SET.format(threshold=threshold),
                parse_mode='Markdown'
            )

        except ValueError as e:
            await update.message.reply_text(f"❌ Invalid threshold: {e}")

    # Profile conversation handler

    async def profile_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start profile creation conversation."""
        await update.message.reply_text(messages.PROFILE_START)
        return PROFILE_CHOICE

    async def profile_template(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle template selection."""
        user_id = update.effective_user.id
        command = update.message.text.strip().lower()

        template_map = {
            '/ml': 'ml',
            '/nlp': 'nlp',
            '/cv': 'cv'
        }

        if command not in template_map:
            await update.message.reply_text("Please choose /ml, /nlp, /cv, or /custom")
            return PROFILE_CHOICE

        template = template_map[command]

        try:
            profile = ResearchProfile.from_template(template)
            self._save_user_profile(user_id, profile)

            # Set in Resp instance
            resp = self._get_resp(user_id)
            resp.set_research_profile(profile)

            await update.message.reply_text(
                messages.PROFILE_TEMPLATE_LOADED.format(template_name=template.upper()),
                parse_mode='Markdown'
            )

            return ConversationHandler.END

        except Exception as e:
            await update.message.reply_text(
                messages.ERROR_GENERIC.format(error_message=str(e))
            )
            return ConversationHandler.END

    async def profile_custom_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start custom profile creation."""
        await update.message.reply_text(messages.PROFILE_CUSTOM_NAME)
        return PROFILE_NAME

    async def profile_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle profile name input."""
        context.user_data['profile_name'] = update.message.text
        await update.message.reply_text(
            messages.PROFILE_CUSTOM_CATEGORIES,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
        return PROFILE_CATEGORIES

    async def profile_categories(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle categories input."""
        categories = [cat.strip() for cat in update.message.text.split(',')]
        context.user_data['categories'] = categories
        await update.message.reply_text(
            messages.PROFILE_CUSTOM_PRIMARY,
            parse_mode='Markdown'
        )
        return PROFILE_PRIMARY

    async def profile_primary(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle primary interests input."""
        interests = [line.strip() for line in update.message.text.split('\n') if line.strip()]
        context.user_data['primary_interests'] = interests
        await update.message.reply_text(
            messages.PROFILE_CUSTOM_SECONDARY,
            parse_mode='Markdown'
        )
        return PROFILE_SECONDARY

    async def profile_secondary(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle secondary interests input."""
        text = update.message.text.strip().lower()
        if text == 'skip':
            context.user_data['secondary_interests'] = []
        else:
            interests = [line.strip() for line in update.message.text.split('\n') if line.strip()]
            context.user_data['secondary_interests'] = interests

        await update.message.reply_text(
            messages.PROFILE_CUSTOM_EXCLUSIONS,
            parse_mode='Markdown'
        )
        return PROFILE_EXCLUSIONS

    async def profile_exclusions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle exclusions input and save profile."""
        user_id = update.effective_user.id
        text = update.message.text.strip().lower()

        if text == 'skip':
            context.user_data['exclusions'] = []
        else:
            exclusions = [line.strip() for line in update.message.text.split('\n') if line.strip()]
            context.user_data['exclusions'] = exclusions

        # Create profile
        try:
            profile = ResearchProfile(
                name=context.user_data['profile_name'],
                email=None,
                arxiv_categories=context.user_data['categories'],
                primary_interests=context.user_data['primary_interests'],
                secondary_interests=context.user_data.get('secondary_interests', []),
                exclusions=context.user_data.get('exclusions', [])
            )

            # Validate
            errors = profile.validate()
            if errors:
                error_msg = "❌ Profile validation failed:\n" + "\n".join(f"• {err}" for err in errors)
                await update.message.reply_text(error_msg)
                return ConversationHandler.END

            # Save
            self._save_user_profile(user_id, profile)

            # Set in Resp instance
            resp = self._get_resp(user_id)
            resp.set_research_profile(profile)

            await update.message.reply_text(
                messages.PROFILE_SAVED,
                parse_mode='Markdown'
            )

            # Clear user data
            context.user_data.clear()

            return ConversationHandler.END

        except Exception as e:
            await update.message.reply_text(
                messages.ERROR_GENERIC.format(error_message=str(e))
            )
            return ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel current conversation."""
        context.user_data.clear()
        await update.message.reply_text(messages.CANCEL_MESSAGE, parse_mode='Markdown')
        return ConversationHandler.END

    def get_profile_conversation_handler(self) -> ConversationHandler:
        """
        Get conversation handler for profile creation.

        Returns:
            ConversationHandler instance
        """
        return ConversationHandler(
            entry_points=[CommandHandler('profile', self.profile_start)],
            states={
                PROFILE_CHOICE: [
                    CommandHandler('ml', self.profile_template),
                    CommandHandler('nlp', self.profile_template),
                    CommandHandler('cv', self.profile_template),
                    CommandHandler('custom', self.profile_custom_start),
                ],
                PROFILE_NAME: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.profile_name)
                ],
                PROFILE_CATEGORIES: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.profile_categories)
                ],
                PROFILE_PRIMARY: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.profile_primary)
                ],
                PROFILE_SECONDARY: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.profile_secondary)
                ],
                PROFILE_EXCLUSIONS: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.profile_exclusions)
                ],
            },
            fallbacks=[CommandHandler('cancel', self.cancel)]
        )
