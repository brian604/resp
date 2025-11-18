"""
Main RESP Telegram bot implementation.
"""

import logging
from typing import Optional

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters
)

from resp.telegram_bot.config import BotConfig
from resp.telegram_bot.handlers import RespHandlers
from resp.telegram_bot.scheduler import DigestScheduler
from resp.telegram_bot import messages


# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class RespTelegramBot:
    """
    RESP Telegram Bot for interactive paper discovery.

    Features:
    - Research profile management via conversation
    - On-demand personalized digest generation
    - Scheduled daily/weekly digests
    - Semantic paper search
    - Customizable relevance thresholds
    """

    def __init__(self, config: Optional[BotConfig] = None):
        """
        Initialize RESP Telegram bot.

        Args:
            config: Bot configuration (uses env vars if None)
        """
        self.config = config or BotConfig.from_env()
        self.handlers = RespHandlers(self.config)
        self.scheduler = DigestScheduler(self.config)
        self.application: Optional[Application] = None

    def _setup_handlers(self):
        """Set up command and message handlers."""
        app = self.application

        # Basic commands
        app.add_handler(CommandHandler('start', self.handlers.start))
        app.add_handler(CommandHandler('help', self.handlers.help_command))

        # Profile management
        app.add_handler(self.handlers.get_profile_conversation_handler())
        app.add_handler(CommandHandler('viewprofile', self.handlers.viewprofile))

        # Digest and search
        app.add_handler(CommandHandler('digest', self.handlers.digest))
        app.add_handler(CommandHandler('daily', self.handlers.digest))  # Alias

        # Settings
        app.add_handler(CommandHandler('threshold', self.handlers.threshold))
        app.add_handler(CommandHandler('stats', self.handlers.stats))

        # Schedule commands
        app.add_handler(CommandHandler('schedule', self._schedule_command))
        app.add_handler(CommandHandler('unschedule', self._unschedule_command))

        # Template shortcuts
        app.add_handler(CommandHandler('ml', self._ml_template))
        app.add_handler(CommandHandler('nlp', self._nlp_template))
        app.add_handler(CommandHandler('cv', self._cv_template))

        # Error handler
        app.add_error_handler(self._error_handler)

        logger.info("Handlers registered successfully")

    async def _schedule_command(self, update, context):
        """Handle /schedule command."""
        user_id = update.effective_user.id

        if not context.args:
            # Show current schedule
            schedule_info = self.scheduler.get_user_schedule(self.application, user_id)

            if schedule_info['scheduled']:
                await update.message.reply_text(
                    f"⏰ **Current Schedule**\n\n"
                    f"Daily digest at: {schedule_info['time']} UTC\n"
                    f"Next run: {schedule_info['next_run']}\n\n"
                    f"Use /unschedule to cancel.",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(
                    "⏰ **Schedule Daily Digest**\n\n"
                    "No digest scheduled.\n\n"
                    "Usage: /schedule HH:MM\n"
                    "Example: /schedule 08:00\n\n"
                    "Time is in UTC (24-hour format).",
                    parse_mode='Markdown'
                )
            return

        # Set schedule
        try:
            digest_time = context.args[0]
            self.scheduler.schedule_user_digest(self.application, user_id, digest_time)

            settings = self.handlers._get_user_settings(user_id)
            settings['schedule_time'] = digest_time
            self.handlers._save_user_settings(user_id, settings)

            schedule_info = self.scheduler.get_user_schedule(self.application, user_id)

            await update.message.reply_text(
                messages.SCHEDULE_SET.format(
                    time=digest_time,
                    timezone='UTC',
                    next_run=schedule_info['next_run']
                ),
                parse_mode='Markdown'
            )

        except ValueError as e:
            await update.message.reply_text(
                f"❌ Invalid time format: {e}\n\n"
                f"Use HH:MM format (24-hour)\n"
                f"Example: /schedule 08:00"
            )

    async def _unschedule_command(self, update, context):
        """Handle /unschedule command."""
        user_id = update.effective_user.id

        self.scheduler.unschedule_user_digest(self.application, user_id)

        settings = self.handlers._get_user_settings(user_id)
        settings['schedule_time'] = None
        self.handlers._save_user_settings(user_id, settings)

        await update.message.reply_text(
            messages.SCHEDULE_CANCELLED,
            parse_mode='Markdown'
        )

    async def _ml_template(self, update, context):
        """Quick command to load ML template."""
        user_id = update.effective_user.id
        from resp.personalization import ResearchProfile

        profile = ResearchProfile.from_template('ml')
        self.handlers._save_user_profile(user_id, profile)

        resp = self.handlers._get_resp(user_id)
        resp.set_research_profile(profile)

        await update.message.reply_text(
            messages.PROFILE_TEMPLATE_LOADED.format(template_name='Machine Learning'),
            parse_mode='Markdown'
        )

    async def _nlp_template(self, update, context):
        """Quick command to load NLP template."""
        user_id = update.effective_user.id
        from resp.personalization import ResearchProfile

        profile = ResearchProfile.from_template('nlp')
        self.handlers._save_user_profile(user_id, profile)

        resp = self.handlers._get_resp(user_id)
        resp.set_research_profile(profile)

        await update.message.reply_text(
            messages.PROFILE_TEMPLATE_LOADED.format(template_name='Natural Language Processing'),
            parse_mode='Markdown'
        )

    async def _cv_template(self, update, context):
        """Quick command to load CV template."""
        user_id = update.effective_user.id
        from resp.personalization import ResearchProfile

        profile = ResearchProfile.from_template('cv')
        self.handlers._save_user_profile(user_id, profile)

        resp = self.handlers._get_resp(user_id)
        resp.set_research_profile(profile)

        await update.message.reply_text(
            messages.PROFILE_TEMPLATE_LOADED.format(template_name='Computer Vision'),
            parse_mode='Markdown'
        )

    async def _error_handler(self, update, context):
        """Handle errors."""
        logger.error(f"Update {update} caused error {context.error}", exc_info=context.error)

        if update and update.effective_message:
            await update.effective_message.reply_text(
                messages.ERROR_GENERIC.format(error_message=str(context.error)),
                parse_mode='Markdown'
            )

    def build(self) -> Application:
        """
        Build the bot application.

        Returns:
            Configured Application instance
        """
        # Create application
        self.application = (
            Application.builder()
            .token(self.config.bot_token)
            .build()
        )

        # Setup handlers
        self._setup_handlers()

        logger.info("Bot application built successfully")
        return self.application

    def run(self):
        """
        Run the bot (blocking).

        Starts the bot and begins polling for updates.
        """
        if not self.application:
            self.build()

        logger.info("Starting RESP Telegram Bot...")
        logger.info(f"Data directory: {self.config.data_dir}")

        # Start polling
        self.application.run_polling(
            allowed_updates=['message', 'callback_query']
        )

    async def start_webhook(self, webhook_url: str, port: int = 8443):
        """
        Start bot with webhook (for production deployment).

        Args:
            webhook_url: Public webhook URL
            port: Port to listen on
        """
        if not self.application:
            self.build()

        logger.info(f"Starting webhook on {webhook_url}:{port}")

        await self.application.bot.set_webhook(url=webhook_url)
        await self.application.start()
        await self.application.updater.start_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=self.config.bot_token
        )

    def stop(self):
        """Stop the bot."""
        if self.application:
            self.application.stop()
            logger.info("Bot stopped")


def main():
    """Main entry point for running the bot."""
    try:
        # Load config from environment
        config = BotConfig.from_env()

        # Create and run bot
        bot = RespTelegramBot(config)
        bot.run()

    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise


if __name__ == '__main__':
    main()
