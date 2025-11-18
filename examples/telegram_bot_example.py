"""
Example of running the RESP Telegram bot.

Setup:
1. Create a bot with @BotFather on Telegram
2. Get your bot token
3. Set environment variables:
   export TELEGRAM_BOT_TOKEN='your-bot-token'
   export OPENAI_API_KEY='your-openai-key'  # For paper scoring
4. Run this script

Usage:
    python examples/telegram_bot_example.py

For production deployment with webhook:
    python examples/telegram_bot_example.py --webhook https://your-domain.com --port 8443
"""

import os
import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from resp.telegram_bot import RespTelegramBot, BotConfig


def run_polling():
    """Run bot with polling (development mode)."""
    print("🤖 Starting RESP Telegram Bot (polling mode)")
    print("=" * 60)

    # Check required environment variables
    if not os.getenv('TELEGRAM_BOT_TOKEN'):
        print("❌ Error: TELEGRAM_BOT_TOKEN environment variable not set")
        print("\nTo get a token:")
        print("1. Message @BotFather on Telegram")
        print("2. Send /newbot and follow instructions")
        print("3. Copy the token and export it:")
        print("   export TELEGRAM_BOT_TOKEN='your-token-here'")
        sys.exit(1)

    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Warning: OPENAI_API_KEY not set")
        print("Paper scoring will not work without an API key.")
        print("Export your key: export OPENAI_API_KEY='your-key'")
        print()

    # Create bot with config from environment
    config = BotConfig.from_env()

    print(f"📁 Data directory: {config.data_dir}")
    print(f"⏰ Default digest time: {config.default_digest_time} UTC")
    print(f"📊 Default threshold: {config.default_threshold}/10")
    print(f"📄 Max papers per digest: {config.max_papers_per_digest}")
    print()

    # Create and run bot
    bot = RespTelegramBot(config)

    print("✅ Bot is running! Send /start to your bot on Telegram")
    print("Press Ctrl+C to stop")
    print()

    try:
        bot.run()
    except KeyboardInterrupt:
        print("\n\n🛑 Bot stopped")
        bot.stop()


def run_webhook(webhook_url: str, port: int):
    """Run bot with webhook (production mode)."""
    import asyncio

    print("🤖 Starting RESP Telegram Bot (webhook mode)")
    print("=" * 60)

    config = BotConfig.from_env()

    print(f"🌐 Webhook URL: {webhook_url}")
    print(f"🔌 Port: {port}")
    print(f"📁 Data directory: {config.data_dir}")
    print()

    bot = RespTelegramBot(config)

    print("✅ Bot is running with webhook")
    print("Press Ctrl+C to stop")
    print()

    try:
        asyncio.run(bot.start_webhook(webhook_url, port))
    except KeyboardInterrupt:
        print("\n\n🛑 Bot stopped")
        bot.stop()


def main():
    """Main entry point with CLI arguments."""
    parser = argparse.ArgumentParser(
        description='Run RESP Telegram Bot',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Development mode (polling)
  python telegram_bot_example.py

  # Production mode (webhook)
  python telegram_bot_example.py --webhook https://example.com/bot --port 8443

Environment Variables:
  TELEGRAM_BOT_TOKEN    Bot token from @BotFather (required)
  OPENAI_API_KEY        OpenAI API key for scoring (required)
  RESP_BOT_DATA_DIR     Data directory (default: ~/.resp/telegram)
  RESP_BOT_DIGEST_TIME  Default digest time (default: 08:00)
  RESP_BOT_THRESHOLD    Relevance threshold (default: 6.5)
  RESP_BOT_MAX_PAPERS   Max papers per digest (default: 10)
        """
    )

    parser.add_argument(
        '--webhook',
        type=str,
        help='Webhook URL for production deployment'
    )

    parser.add_argument(
        '--port',
        type=int,
        default=8443,
        help='Port for webhook (default: 8443)'
    )

    args = parser.parse_args()

    if args.webhook:
        run_webhook(args.webhook, args.port)
    else:
        run_polling()


if __name__ == '__main__':
    main()
