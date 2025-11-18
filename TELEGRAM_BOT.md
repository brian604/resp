# RESP Telegram Bot

Interactive paper discovery and digest delivery via Telegram.

## Features

- 🤖 **Conversational Setup**: Create research profiles through natural conversation
- 📰 **On-Demand Digests**: Get personalized paper recommendations anytime
- ⏰ **Scheduled Delivery**: Receive daily digests at your preferred time
- 🔍 **Smart Ranking**: LLM-based relevance scoring (1-10 scale)
- 📊 **Usage Tracking**: Monitor API costs and paper discovery stats
- 🎯 **Customizable**: Adjust thresholds, categories, and preferences

## Quick Start

### 1. Create Your Bot

1. Open Telegram and message [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the instructions
3. Copy your bot token (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Set Up Environment

```bash
# Required: Bot token and OpenAI API key
export TELEGRAM_BOT_TOKEN='your-bot-token'
export OPENAI_API_KEY='your-openai-api-key'

# Optional configuration
export RESP_BOT_DATA_DIR='~/.resp/telegram'  # Data storage location
export RESP_BOT_DIGEST_TIME='08:00'          # Default digest time (UTC)
export RESP_BOT_THRESHOLD='6.5'              # Relevance threshold (1-10)
export RESP_BOT_MAX_PAPERS='10'              # Max papers per digest
```

### 3. Install Dependencies

```bash
pip install -e ".[telegram]"
```

### 4. Run the Bot

```bash
python examples/telegram_bot_example.py
```

### 5. Start Using

1. Find your bot on Telegram
2. Send `/start` to begin
3. Use `/profile` to set up your research interests
4. Use `/digest` to get your first personalized digest!

## Bot Commands

### Profile Management

| Command | Description |
|---------|-------------|
| `/profile` | Create or edit research profile (conversational) |
| `/viewprofile` | View your current profile |
| `/ml` | Quick load: Machine Learning template |
| `/nlp` | Quick load: Natural Language Processing template |
| `/cv` | Quick load: Computer Vision template |

### Paper Discovery

| Command | Description |
|---------|-------------|
| `/digest` | Generate personalized digest |
| `/daily` | Alias for `/digest` |
| `/search <query>` | Search papers semantically (coming soon) |

### Configuration

| Command | Description |
|---------|-------------|
| `/threshold <value>` | Set relevance threshold (1.0-10.0) |
| `/schedule <HH:MM>` | Schedule daily digest (UTC time) |
| `/unschedule` | Cancel scheduled digests |
| `/stats` | View usage statistics |

### Help

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and quick start |
| `/help` | Show all commands |
| `/cancel` | Cancel current operation |

## Usage Examples

### Example 1: Quick Start with Template

```
You: /start
Bot: [Welcome message with quick start guide]

You: /ml
Bot: ✅ Template Loaded: Machine Learning
     [Template details]

You: /digest
Bot: 🔄 Generating Personalized Digest...
     [30-60 seconds later]
     📰 Your Personalized Digest
     Found 5 papers matching your interests (threshold: 6.5/10)

     1. [8.5/10] Efficient Fine-Tuning of Large Language Models...
        💡 Why relevant: Directly addresses model efficiency...
        [Paper details]
```

### Example 2: Custom Profile Creation

```
You: /profile
Bot: Let's set up your research profile! 📝
     Choose from templates or create custom:
     /ml - Machine Learning
     /nlp - Natural Language Processing
     /cv - Computer Vision
     /custom - Create custom profile

You: /custom
Bot: What should I call this profile?

You: Reinforcement Learning Researcher
Bot: Which arXiv categories are you interested in?
     Enter comma-separated (e.g., cs.LG, cs.AI, stat.ML)

You: cs.LG, cs.AI
Bot: What are your main research topics?
     Enter each topic on a new line.

You: Deep reinforcement learning for robotics
     Multi-agent RL systems
     Sample-efficient RL methods
Bot: Any secondary topics? (or "skip")

You: skip
Bot: Any exclusions? (or "skip")

You: Pure game-playing applications
Bot: ✅ Profile Saved!
     [Next steps]
```

### Example 3: Scheduling Daily Digest

```
You: /schedule 08:00
Bot: ⏰ Digest Scheduled
     You'll receive daily digests at 08:00 UTC.
     Next digest: 2025-11-19 08:00:00

[Next day at 08:00 UTC]
Bot: 📰 Your Personalized Digest
     [Automatically delivered papers]
```

### Example 4: Adjusting Threshold

```
You: /digest
Bot: Found 15 papers matching your interests (threshold: 6.5/10)
     [Papers listed]

You: /threshold 8.0
Bot: ✅ Threshold Updated
     New relevance threshold: 8.0/10
     Higher = More selective (7-10: top papers only)

You: /digest
Bot: Found 3 papers matching your interests (threshold: 8.0/10)
     [Only highly relevant papers]
```

## Configuration

### Environment Variables

All configuration can be set via environment variables:

```bash
# Required
TELEGRAM_BOT_TOKEN='123456:ABC...'  # From @BotFather
OPENAI_API_KEY='sk-...'             # For LLM scoring

# Optional
RESP_BOT_DATA_DIR='~/.resp/telegram'  # Where to store user data
RESP_BOT_DIGEST_TIME='08:00'          # Default time for digests (HH:MM UTC)
RESP_BOT_THRESHOLD='6.5'              # Default relevance threshold (1-10)
RESP_BOT_MAX_PAPERS='10'              # Maximum papers per digest
RESP_BOT_WEB_PREVIEW='false'          # Enable link previews
```

### Programmatic Configuration

```python
from resp.telegram_bot import RespTelegramBot, BotConfig

# From environment
config = BotConfig.from_env()

# Or explicit configuration
config = BotConfig(
    bot_token='your-token',
    data_dir='~/.resp/telegram',
    default_digest_time='08:00',
    default_threshold=7.0,
    max_papers_per_digest=15
)

# Create and run bot
bot = RespTelegramBot(config)
bot.run()
```

### From Config File

```python
# Save config
config = BotConfig(bot_token='token', ...)
config.to_file('bot_config.json')

# Load config
config = BotConfig.from_file('bot_config.json')
bot = RespTelegramBot(config)
```

## Data Storage

The bot stores user data locally in the configured data directory (default: `~/.resp/telegram/`):

```
~/.resp/telegram/
├── 123456789/              # User ID
│   ├── profile.yaml        # Research profile
│   ├── settings.json       # Bot settings
│   └── cache/              # Scoring cache
└── 987654321/              # Another user
    └── ...
```

### User Privacy

- All data is stored locally on the server
- Each user has an isolated directory
- No data is shared between users
- Profile and settings can be deleted anytime

## Deployment

### Development (Polling)

Easiest for testing and small-scale use:

```bash
python examples/telegram_bot_example.py
```

The bot polls Telegram servers for updates. No public URL needed.

### Production (Webhook)

Recommended for production deployments:

```bash
python examples/telegram_bot_example.py \
    --webhook https://your-domain.com/bot \
    --port 8443
```

Requirements:
- Public HTTPS URL
- SSL certificate
- Port 443, 80, 88, or 8443

### Docker Deployment

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . .

RUN pip install -e ".[telegram]"

ENV TELEGRAM_BOT_TOKEN=""
ENV OPENAI_API_KEY=""

CMD ["python", "examples/telegram_bot_example.py"]
```

```bash
docker build -t resp-bot .
docker run -e TELEGRAM_BOT_TOKEN='...' -e OPENAI_API_KEY='...' resp-bot
```

### Systemd Service

```ini
# /etc/systemd/system/resp-bot.service
[Unit]
Description=RESP Telegram Bot
After=network.target

[Service]
Type=simple
User=resp
WorkingDirectory=/opt/resp
Environment="TELEGRAM_BOT_TOKEN=your-token"
Environment="OPENAI_API_KEY=your-key"
ExecStart=/usr/bin/python3 examples/telegram_bot_example.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable resp-bot
sudo systemctl start resp-bot
sudo systemctl status resp-bot
```

## Cost Management

The bot uses OpenAI API for paper relevance scoring. Costs are typically low:

- **Model**: gpt-3.5-turbo (default)
- **Cost per paper**: ~$0.001-0.002
- **Typical digest (10 papers)**: ~$0.01-0.02
- **Monthly (daily digests)**: ~$0.30-0.60

### Reducing Costs

1. **Caching**: Enabled by default, reuses scores for same papers
2. **Higher threshold**: Fewer papers scored = lower cost
3. **Smaller max_papers**: Limit papers per digest
4. **Less frequent**: Weekly instead of daily digests

### Monitoring Costs

```
You: /stats
Bot: 📊 Your RESP Statistics

     Usage:
     • Total digests: 45
     • Papers scored: 523
     • API cost: $8.67
     • Last digest: 2025-11-18 08:00
```

## Troubleshooting

### Bot Not Responding

1. Check bot is running: `ps aux | grep telegram_bot`
2. Check logs for errors
3. Verify `TELEGRAM_BOT_TOKEN` is correct
4. Test token: `curl https://api.telegram.org/bot<TOKEN>/getMe`

### "API Key Missing" Error

Set OpenAI API key:
```bash
export OPENAI_API_KEY='sk-...'
```

### "No Papers Found"

- Lower threshold: `/threshold 5.0`
- Expand arXiv categories in profile
- Check if papers were published recently
- Try different time range (bot looks at last 7 days)

### Scheduled Digests Not Arriving

- Check schedule: `/schedule` (without arguments)
- Verify timezone (uses UTC)
- Check bot logs for errors
- Ensure bot process is running continuously

### Rate Limiting

If you see rate limit errors:
- Wait a few minutes
- Reduce `max_papers` setting
- Avoid running multiple digests simultaneously

## Advanced Usage

### Multiple Bots

Run different bots for different purposes:

```bash
# Research bot
export TELEGRAM_BOT_TOKEN='token1'
export RESP_BOT_DATA_DIR='~/.resp/research_bot'
python examples/telegram_bot_example.py &

# Teaching bot
export TELEGRAM_BOT_TOKEN='token2'
export RESP_BOT_DATA_DIR='~/.resp/teaching_bot'
python examples/telegram_bot_example.py &
```

### Custom LLM Backend

Use OpenAI-compatible APIs:

```python
from resp.telegram_bot import RespTelegramBot, BotConfig
import os

# Point to local LLM or alternative provider
os.environ['OPENAI_API_KEY'] = 'dummy-key'

config = BotConfig.from_env()
bot = RespTelegramBot(config)

# The scorer will use OPENAI_BASE_URL if set
os.environ['OPENAI_BASE_URL'] = 'http://localhost:8000/v1'

bot.run()
```

### Backup User Data

```bash
# Backup all user data
tar -czf resp-backup-$(date +%Y%m%d).tar.gz ~/.resp/telegram/

# Restore
tar -xzf resp-backup-20251118.tar.gz -C ~/
```

## API Reference

See module documentation:
- `resp.telegram_bot.bot.RespTelegramBot` - Main bot class
- `resp.telegram_bot.config.BotConfig` - Configuration management
- `resp.telegram_bot.handlers.RespHandlers` - Command handlers
- `resp.telegram_bot.scheduler.DigestScheduler` - Job scheduling

## Contributing

Contributions welcome! Areas for improvement:

- [ ] Semantic search command implementation
- [ ] Inline query support for quick searches
- [ ] Rich digest formatting (HTML, images)
- [ ] Multi-language support
- [ ] Analytics dashboard
- [ ] Export to PDF/email

## License

Same as RESP - open source and free to use.

## Support

- 📖 [Main RESP Documentation](README.md)
- 🐛 [Report Issues](https://github.com/yourusername/resp/issues)
- 💬 [Discussions](https://github.com/yourusername/resp/discussions)
