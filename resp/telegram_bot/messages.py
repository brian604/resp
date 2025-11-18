"""
Message templates for RESP Telegram bot.
"""

# Welcome and help messages
WELCOME_MESSAGE = """
🔬 **Welcome to RESP - Research Paper Discovery Bot!**

I help you discover relevant research papers personalized to your interests.

**What I can do:**
• 📋 Manage your research profile
• 📰 Generate personalized paper digests
• 🔍 Search papers with semantic matching
• ⏰ Schedule daily/weekly digests
• 📊 Rank papers by relevance

**Quick Start:**
1. Use /profile to set up your research interests
2. Use /digest to get your first personalized digest
3. Use /settings to customize preferences

Type /help to see all commands.
"""

HELP_MESSAGE = """
**Available Commands:**

*Profile Management:*
/profile - Create or edit your research profile
/viewprofile - View your current profile
/template - Load a profile template (ML, NLP, CV)

*Paper Discovery:*
/digest - Generate personalized digest
/search <query> - Search papers semantically
/daily - Get today's papers from your interests

*Settings:*
/settings - Configure bot preferences
/schedule - Set up automated digests
/threshold - Set relevance threshold

*Other:*
/stats - View your usage statistics
/help - Show this help message
/cancel - Cancel current operation

**Tips:**
• Set a higher threshold (7-8) for highly focused results
• Use /schedule to get daily digests automatically
• Your profile is saved and reused for all searches
"""

# Profile management
PROFILE_START = """
Let's set up your research profile! 📝

This helps me understand your research interests and recommend relevant papers.

**What's your research area?**

Choose from templates or create custom:
/ml - Machine Learning researcher
/nlp - Natural Language Processing
/cv - Computer Vision
/custom - Create custom profile

Or /cancel to abort.
"""

PROFILE_CUSTOM_NAME = """
**Creating Custom Profile**

What should I call this profile?
(e.g., "Reinforcement Learning Researcher")
"""

PROFILE_CUSTOM_CATEGORIES = """
**ArXiv Categories**

Which arXiv categories are you interested in?
Enter comma-separated (e.g., cs.LG, cs.AI, stat.ML)

Common categories:
• cs.LG - Machine Learning
• cs.AI - Artificial Intelligence
• cs.CL - Computation and Language (NLP)
• cs.CV - Computer Vision
• stat.ML - Statistics ML

Full list: https://arxiv.org/category_taxonomy
"""

PROFILE_CUSTOM_PRIMARY = """
**Primary Research Interests**

What are your main research topics? (3-5 topics recommended)
Enter each topic on a new line.

Example:
```
Transfer learning for low-resource settings
Model compression and efficient architectures
Explainable AI methods
```
"""

PROFILE_CUSTOM_SECONDARY = """
**Secondary Interests** (Optional)

Any secondary topics you'd like to track?
Enter each topic on a new line, or type "skip" to continue.

Example:
```
Federated learning
AutoML techniques
```
"""

PROFILE_CUSTOM_EXCLUSIONS = """
**Exclusions** (Optional)

Any topics you want to filter out?
Enter each exclusion on a new line, or type "skip" to finish.

Example:
```
Pure theoretical papers
Medical-only applications
```
"""

PROFILE_SAVED = """
✅ **Profile Saved!**

Your research profile has been saved and will be used for all future searches and digests.

**Next Steps:**
• /digest - Generate your first personalized digest
• /viewprofile - Review your profile
• /settings - Configure preferences

Ready to discover papers? Use /digest now!
"""

PROFILE_TEMPLATE_LOADED = """
✅ **Template Loaded: {template_name}**

I've loaded the {template_name} researcher profile template.

You can:
• /digest - Start getting personalized papers
• /profile - Customize this template further
• /viewprofile - See what's in the profile
"""

# Digest generation
DIGEST_GENERATING = """
🔄 **Generating Personalized Digest...**

Fetching recent papers from arXiv...
This may take 30-60 seconds.
"""

DIGEST_SCORING = """
📊 **Scoring Papers...**

Analyzing {count} papers against your interests...
Using LLM to rank by relevance...
"""

DIGEST_EMPTY = """
📭 **No Papers Found**

I couldn't find papers matching your criteria.

**Try:**
• Lowering your threshold: /threshold 5.0
• Expanding your arXiv categories
• Checking back later for new papers
"""

DIGEST_HEADER = """
📰 **Your Personalized Digest**
*{date}*

Found {total} papers matching your interests (threshold: {threshold}/10)

---
"""

DIGEST_PAPER = """
**{rank}. {title}**
📊 Relevance: {score}/10
📅 Published: {published}
👥 Authors: {authors}

💡 *Why relevant:* {reasoning}

🔗 [Read Paper]({url})
📄 [PDF]({pdf_url})

---
"""

DIGEST_FOOTER = """
**💰 Cost:** ${cost:.4f} ({tokens} tokens)
**⚙️ Model:** {model}

Use /search to find more papers, or /settings to adjust preferences.
"""

# Search
SEARCH_PROMPT = """
🔍 **Semantic Paper Search**

What would you like to search for?
(e.g., "vision transformers for medical imaging")

Or /cancel to abort.
"""

SEARCH_RESULTS_HEADER = """
🔍 **Search Results:** "{query}"

Found {count} relevant papers:

---
"""

# Settings
SETTINGS_MENU = """
⚙️ **Bot Settings**

Current configuration:
• Relevance threshold: {threshold}/10
• Max papers per digest: {max_papers}
• Scheduled digests: {schedule_status}
• Web previews: {web_preview}

**Modify:**
/threshold <value> - Set relevance threshold (1-10)
/maxpapers <num> - Max papers per digest
/schedule <time> - Schedule daily digest (HH:MM)
/unschedule - Cancel scheduled digests

Current profile: {profile_name}
"""

THRESHOLD_SET = """
✅ **Threshold Updated**

New relevance threshold: {threshold}/10

• Higher = More selective (7-10: top papers only)
• Lower = More inclusive (4-6: broader results)

Use /digest to see results with new threshold.
"""

SCHEDULE_SET = """
⏰ **Digest Scheduled**

You'll receive daily digests at {time} UTC.

• Timezone: {timezone}
• Next digest: {next_run}

Use /unschedule to cancel anytime.
"""

SCHEDULE_CANCELLED = """
🔕 **Scheduled Digests Cancelled**

You won't receive automatic digests anymore.
Use /digest to generate on-demand.
"""

# Stats
STATS_MESSAGE = """
📊 **Your RESP Statistics**

**Profile:**
• Name: {profile_name}
• Categories: {categories}
• Created: {created_date}

**Usage:**
• Total digests: {total_digests}
• Papers scored: {papers_scored}
• API cost: ${total_cost:.2f}
• Last digest: {last_digest}

**Settings:**
• Threshold: {threshold}/10
• Scheduled: {schedule_status}
"""

# Errors
ERROR_NO_PROFILE = """
❌ **No Profile Found**

You need to set up a research profile first.
Use /profile to get started!
"""

ERROR_RATE_LIMIT = """
⏳ **Rate Limited**

Please wait a moment before trying again.
(Avoiding API overuse)
"""

ERROR_API_KEY = """
❌ **API Key Missing**

OpenAI API key required for scoring papers.
Administrator needs to set OPENAI_API_KEY.
"""

ERROR_GENERIC = """
❌ **Error Occurred**

{error_message}

If this persists, contact the bot administrator.
"""

CANCEL_MESSAGE = """
❌ **Operation Cancelled**

Anything else I can help with? Type /help for commands.
"""


def format_paper_card(rank: int, paper: dict) -> str:
    """
    Format a paper as a message card.

    Args:
        rank: Paper ranking
        paper: Paper dictionary

    Returns:
        Formatted message string
    """
    title = paper.get('title', 'Untitled')
    score = paper.get('relevance_score', 0)
    reasoning = paper.get('relevance_reasoning', 'No reasoning available')
    published = paper.get('published', 'Unknown date')
    authors = paper.get('authors', 'Unknown authors')
    url = paper.get('url', '#')
    pdf_url = paper.get('pdf_url', url)

    # Truncate long fields
    if len(authors) > 100:
        authors = authors[:97] + '...'
    if len(reasoning) > 200:
        reasoning = reasoning[:197] + '...'

    return DIGEST_PAPER.format(
        rank=rank,
        title=title,
        score=score,
        reasoning=reasoning,
        published=published,
        authors=authors,
        url=url,
        pdf_url=pdf_url
    )
