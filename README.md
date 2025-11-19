<h2 align="center">RESP: Research Papers Search, Summarization & Personalization</h2>
<h4 align="center">Your AI-Powered Research Assistant for Academic Papers</h4>

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![GitHub commit](https://img.shields.io/github/last-commit/monk1337/resp)](https://github.com/monk1337/resp/commits/main)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)
[![Open All Collab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/188cWcZrBRVGAF3Dp_5uswmLgbBNKSioB?usp=sharing)

## Features

### 🔍 Paper Search
- Fetch papers from multiple academic sources based on keywords or titles
- Support for 9+ sources including Google Scholar, arXiv, ACL, PMLR, Semantic Scholar, and more
- Direct arXiv API integration with abstract extraction
- Get citations and related papers from Google Scholar
- Find connected papers using similarity graphs (ConnectedPapers.com)

### 🤖 AI Summarization
- **OpenAI API Support**: Use GPT models for high-quality summarization
- **OpenAI-Compatible APIs**: Support for DeepSeek, Groq, and other compatible services
- **Local Models**: Run summarization locally using Transformers or llama.cpp
- **Structured Summaries**: Generate concise summaries, key points, and TL;DRs
- **Batch Processing**: Summarize multiple papers efficiently

### 🎯 Semantic Search
- **Semantic Re-ranking**: Improve keyword search results with semantic similarity
- **Vector Database**: Build searchable index with FAISS for fast similarity search
- **Multiple Embeddings**: Support for SentenceTransformers and OpenAI embeddings
- **Hybrid Search**: Combine keyword and semantic search for best results
- **Specialized Models**: Use scientific paper embeddings (SPECTER, etc.)
- **Persistent Storage**: Save and load vector indices

### ⭐ Personalized Discovery (NEW!)
- **LLM-Based Relevance Scoring**: Rank papers 1-10 based on your research interests
- **Natural Language Profiles**: Define interests in plain English, not just keywords
- **Research Templates**: Pre-built profiles for ML, NLP, CV, and more
- **Smart Filtering**: Specify exclusions and priorities
- **Cost-Optimized**: Intelligent caching to minimize API costs
- **Daily Digests**: Automatically discover relevant new papers

### 🤖 Telegram Bot (NEW!)
- **Interactive Setup**: Create research profiles through conversational interface
- **On-Demand Digests**: Get personalized paper recommendations via Telegram
- **Scheduled Delivery**: Receive daily digests at your preferred time
- **Rich Formatting**: Papers with relevance scores and reasoning
- **Easy Commands**: Simple `/digest`, `/profile`, `/search` commands
- **Usage Tracking**: Monitor API costs and discovery stats
- **📖 [Full Documentation](TELEGRAM_BOT.md)**

## Installation

### Basic Installation
```shell
git clone https://github.com/monk1337/resp
cd resp
uv pip install -r requirements.txt && uv pip install -e .
```

### Optional Features

```shell
# For AI Summarization (OpenAI and compatible APIs)
uv pip install -e ".[summarization]"

# For local summarization models (transformers)
uv pip install -e ".[local]"

# For semantic search and re-ranking
uv pip install -e ".[semantic]"

# For Telegram bot (includes summarization)
uv pip install -e ".[telegram]"

# Install everything
uv pip install -e ".[all]"
```

## Quick Start

### Basic Paper Search

```python
from resp import Resp

# Initialize (SerpAPI key optional for some features)
resp = Resp(api_key='your_serp_api_key')

# Search different sources
acl_papers = resp.acl('transformers', max_pages=5)
arxiv_papers = resp.arxiv_direct('attention mechanism', max_pages=3)
semantic_papers = resp.semantic_scholar('neural networks')

# Get all related papers
related = resp.all_related_papers('Attention Is All You Need')
```

### AI-Powered Summarization

#### Using OpenAI API
```python
from resp import Resp

# Initialize with OpenAI summarizer
resp = Resp(summarizer='openai')

# Or set your API key in environment
# export OPENAI_API_KEY='your-api-key'

# Search and summarize papers
papers = resp.arxiv_direct('large language models', max_pages=2, summarize=True)

# Papers now include: summary, key_points, tldr
for _, paper in papers.iterrows():
    print(f"Title: {paper['title']}")
    print(f"Summary: {paper['summary']}")
    print(f"TL;DR: {paper['tldr']}")
    print("---")
```

#### Using OpenAI-Compatible APIs (e.g., DeepSeek)
```python
from resp import Resp
from resp.config import Config

# Configure for DeepSeek or other compatible service
config = Config()
config.set('summarizer.openai.base_url', 'https://api.deepseek.com/v1')
config.set('summarizer.openai.model', 'deepseek-chat')
config.set_api_key('openai', 'your-deepseek-api-key')
config.save_config()

# Initialize with custom config
resp = Resp(config=config, summarizer='openai')

# Now use as normal
papers = resp.arxiv_direct('computer vision', summarize=True)
```

#### Using Local Models
```python
from resp import Resp
from resp.config import Config

# Configure local model
config = Config()
config.set('summarizer.local.model_type', 'transformers')
config.set('summarizer.local.model_name', 'facebook/bart-large-cnn')
config.set('summarizer.local.device', 'cpu')  # or 'cuda'
config.save_config()

# Initialize with local summarizer
resp = Resp(config=config, summarizer='local')

# Search and summarize
papers = resp.arxiv_direct('machine learning', max_pages=1, summarize=True)
```

#### Manual Summarization
```python
from resp import Resp

resp = Resp()

# First search for papers
papers = resp.arxiv_direct('deep learning', max_pages=2)

# Then enable summarization
resp.set_summarizer('openai')

# Summarize the papers
summarized_papers = resp.summarize_papers(papers)
```

### Semantic Search

#### Semantic Re-ranking
```python
from resp import Resp

# Initialize with semantic search enabled
resp = Resp(enable_semantic_search=True)

# Search for papers
query = "attention mechanisms in transformers"
papers = resp.arxiv_direct(query, max_pages=2)

# Re-rank by semantic similarity
reranked = resp.semantic_rerank(query, papers, top_k=10)

# Papers are now sorted by semantic relevance
for i, paper in reranked.iterrows():
    print(f"{paper['title']} - Score: {paper['semantic_score']:.4f}")
```

#### Vector Database Search
```python
from resp import Resp

resp = Resp()

# Initialize vector store
resp.init_vector_store(
    embedder_model="multi-qa-MiniLM-L6-cos-v1",
    index_type="flat"  # or 'hnsw' for larger datasets
)

# Collect and index papers
papers = resp.arxiv_direct("machine learning", max_pages=5)
resp.build_vector_index(papers)

# Search by semantic similarity (no keyword matching needed!)
results = resp.semantic_search("neural network optimization", k=10)

# Save index for later
resp.save_vector_index("my_paper_index")

# Load index later
resp.load_vector_index("my_paper_index")
```

#### Hybrid Search (Best of Both Worlds)
```python
from resp import Resp
from resp.semantic_search import SemanticReranker, SentenceTransformerEmbedder

# Create reranker with hybrid scoring
embedder = SentenceTransformerEmbedder()
reranker = SemanticReranker(
    embedder=embedder,
    hybrid_alpha=0.7  # 70% semantic, 30% original ranking
)

resp = Resp()
papers = resp.arxiv_direct("deep learning", max_pages=2)

# Re-rank with hybrid scoring
papers_list = papers.to_dict('records')
hybrid_results = reranker.rerank("neural networks", papers_list, top_k=10)
```

### Personalized Discovery

#### Using Research Profiles
```python
from resp import Resp

# Initialize RESP
resp = Resp()

# Use a built-in template (ml, nlp, cv)
resp.set_research_profile("ml")

# Or load your custom profile
# resp.set_research_profile("my_research_interests.yaml")

# Search for papers
papers = resp.arxiv_direct("machine learning", max_pages=2)

# Rank by relevance to your interests (1-10 scale)
ranked = resp.rank_by_relevance(papers, threshold=6.0)

# View results
for i, paper in ranked.iterrows():
    score = paper['relevance_score']
    reasoning = paper['relevance_reasoning']
    print(f"[{score:.1f}/10] {paper['title']}")
    print(f"Why relevant: {reasoning}\n")
```

#### Creating Custom Profiles
```python
from resp.personalization import ResearchProfile

# Define your research interests in natural language
profile = ResearchProfile(
    name="My Research Profile",
    email="researcher@example.com",
    arxiv_categories=["cs.LG", "cs.AI", "cs.CL"],

    primary_interests=[
        "Large language models and their applications",
        "Efficient fine-tuning methods like LoRA and QLoRA",
        "Multi-modal learning combining vision and language"
    ],

    secondary_interests=[
        "Model interpretability and explainability",
        "Reinforcement learning from human feedback"
    ],

    exclusions=[
        "Pure theoretical papers without experiments",
        "Papers focused only on medical imaging"
    ]
)

# Save for reuse
profile.to_yaml("my_interests.yaml")

# Use it
resp = Resp()
resp.set_research_profile(profile)
papers = resp.fetch_daily_papers()  # Get today's papers
ranked = resp.rank_by_relevance(papers)
```

#### Daily Digest Workflow
```python
from resp import Resp

resp = Resp()
resp.set_research_profile("nlp")

# Fetch today's papers from your research areas
papers = resp.fetch_daily_papers(days_back=1, max_papers=50)

# Rank by relevance
ranked = resp.rank_by_relevance(papers, threshold=7.0)

# Save digest
ranked.to_csv("daily_digest.csv")

print(f"Found {len(ranked)} highly relevant papers today!")
```

### Telegram Bot

Get personalized paper digests delivered directly to Telegram!

#### Setup

```bash
# 1. Install with Telegram support
uv pip install -e ".[telegram]"

# 2. Create bot with @BotFather on Telegram and get token

# 3. Set environment variables
export TELEGRAM_BOT_TOKEN='your-bot-token'
export OPENAI_API_KEY='your-openai-key'

# 4. Run the bot
python examples/telegram_bot_example.py
```

#### Using the Bot

```
1. Find your bot on Telegram
2. Send /start
3. Send /ml (or /nlp, /cv) to load a profile template
4. Send /digest to get personalized papers!

Other commands:
/profile - Create custom research profile
/schedule 08:00 - Get daily digests at 8 AM UTC
/threshold 7.5 - Set relevance threshold
/stats - View usage statistics
```

**📖 [Full Telegram Bot Documentation](TELEGRAM_BOT.md)** - Complete guide with examples, deployment options, and troubleshooting.

## Supported Paper Sources

| Source | Method | Requires SerpAPI |
|--------|--------|------------------|
| [Google Scholar](https://scholar.google.com/) | `google_scholar()` | Yes |
| [arXiv](https://arxiv.org/) | `arxiv_direct()` | No |
| [ACL Anthology](https://aclanthology.org/) | `acl()` | Yes |
| [PMLR](https://proceedings.mlr.press/) | `pmlr()` | Yes |
| [Semantic Scholar](https://www.semanticscholar.org/) | `semantic_scholar()` | Yes |
| [NeurIPS](https://nips.cc/) | `nips()` | Yes |
| [IJCAI](https://www.ijcai.org/) | `ijcai()` | Yes |
| [OpenReview](https://openreview.net/) | `openreview()` | Yes |
| [The CVF](https://openaccess.thecvf.com/) | `cvf()` | Yes |

## Configuration

RESP uses a configuration system to manage API keys and settings. Configuration is stored in `~/.resp/config.json`.

### Setting API Keys

```python
from resp.config import Config

config = Config()

# Set API keys
config.set_api_key('serp_api', 'your-serp-api-key')
config.set_api_key('openai', 'your-openai-api-key')
config.save_config()
```

Or use environment variables:
```bash
export SERP_API_KEY='your-serp-api-key'
export OPENAI_API_KEY='your-openai-api-key'
```

### Customizing Summarization

```python
from resp.config import Config

config = Config()

# Configure OpenAI summarizer
config.set('summarizer.openai.model', 'gpt-4')
config.set('summarizer.openai.temperature', 0.3)
config.set('summarizer.openai.max_tokens', 500)

# Configure local summarizer
config.set('summarizer.local.model_name', 'google/flan-t5-base')
config.set('summarizer.local.device', 'cuda')

config.save_config()
```

## Advanced Usage

### Using Different Summarizers

```python
from resp.summarizers import OpenAISummarizer, LocalSummarizer

# Direct use of OpenAI summarizer
summarizer = OpenAISummarizer(
    api_key='your-key',
    model='gpt-3.5-turbo',
    temperature=0.3
)

# Summarize a single paper
summary = summarizer.summarize_paper(
    title="Attention Is All You Need",
    abstract="The dominant sequence transduction models..."
)

print(summary['summary'])
print(summary['key_points'])
print(summary['tldr'])

# Direct use of local summarizer
local_summarizer = LocalSummarizer(
    model_type='transformers',
    model_name='facebook/bart-large-cnn',
    device='cpu'
)

summary = local_summarizer.summarize_paper(
    title="BERT: Pre-training of Deep Bidirectional Transformers",
    abstract="We introduce a new language representation model..."
)
```

### Using llama.cpp for Local Inference

```python
from resp.summarizers import LocalSummarizer

# Use GGUF models with llama.cpp (more efficient for CPU)
summarizer = LocalSummarizer(
    model_type='llama_cpp',
    model_path='/path/to/model.gguf',
    n_ctx=2048,
    n_threads=4
)

summary = summarizer.summarize("Your paper abstract here...")
```

### Direct arXiv API Access

```python
from resp.apis.arxiv_api import Arxiv

arxiv = Arxiv()

# Use official arXiv API (includes abstracts, authors, dates, categories)
papers = arxiv.arxiv(
    keyword='transformer models',
    max_pages=3,
    use_api=True  # Use official API
)

# Or use web scraping
papers = arxiv.arxiv(
    keyword='neural networks',
    max_pages=2,
    use_api=False  # Use web scraping
)
```

## Model Support

### OpenAI-Compatible Services

RESP works with any OpenAI-compatible API by setting a custom `base_url`:

- **OpenAI**: Default (no base_url needed)
- **DeepSeek**: `https://api.deepseek.com/v1`
- **Groq**: `https://api.groq.com/openai/v1`
- **LocalAI**: Your local URL
- **vLLM**: Your deployment URL
- **Any other OpenAI-compatible service**

### Local Model Examples

**Transformers models** (require `uv pip install transformers torch`):
- `facebook/bart-large-cnn` - Good general summarizer
- `google/flan-t5-base` - Instruction-tuned model
- `philschmid/flan-t5-base-samsum` - Conversation summarization
- Any Seq2Seq model on Hugging Face

**llama.cpp models** (require `uv pip install llama-cpp-python`):
- Any GGUF format model
- Llama, Mistral, Phi, etc.

### Semantic Search Embedding Models

**SentenceTransformers models** (require `uv pip install sentence-transformers`):
- `multi-qa-MiniLM-L6-cos-v1` - Optimized for question-answer/retrieval (384 dim) **[Recommended]**
- `all-MiniLM-L6-v2` - Fast, lightweight, general purpose (384 dim)
- `all-mpnet-base-v2` - Higher quality, slower (768 dim)
- `allenai-specter` - Specialized for scientific papers (768 dim)
- `sentence-transformers/gtr-t5-base` - Good for academic papers
- Any model from [Hugging Face MTEB leaderboard](https://huggingface.co/spaces/mteb/leaderboard)

**OpenAI embeddings** (via API):
- `text-embedding-3-small` - 1536 dim, cost-effective
- `text-embedding-3-large` - 3072 dim, highest quality
- `text-embedding-ada-002` - 1536 dim, previous generation

## Examples

Check the `examples/` directory for more detailed examples:

```python
# See examples/api_uses.py for comprehensive search examples
# See examples/summarization_examples.py for AI summarization examples
# See examples/semantic_search_examples.py for semantic search examples
# See examples/personalization_examples.py for personalized discovery examples
# Or open examples/Api_examples.ipynb in Jupyter
```

## API Reference

### Main Class: `Resp`

#### Constructor
```python
Resp(
    api_key=None,
    config=None,
    summarizer=None,
    enable_semantic_search=False,
    embedder_model="multi-qa-MiniLM-L6-cos-v1"
)
```
- `api_key`: SerpAPI key (optional)
- `config`: Config object (optional)
- `summarizer`: 'openai', 'local', or None
- `enable_semantic_search`: Enable semantic re-ranking
- `embedder_model`: SentenceTransformers model name

#### Methods

**Search Methods:**
- `acl(keyword, max_pages)` - Search ACL Anthology
- `arxiv(keyword, max_pages)` - Search arXiv via Google
- `arxiv_direct(keyword, max_pages, use_api, summarize)` - Direct arXiv search with abstracts
- `pmlr(keyword, max_pages)` - Search PMLR
- `semantic_scholar(keyword, max_pages)` - Search Semantic Scholar
- `nips(keyword, max_pages)` - Search NeurIPS
- `ijcai(keyword, max_pages)` - Search IJCAI
- `openreview(keyword, max_pages)` - Search OpenReview
- `cvf(keyword, max_pages)` - Search CVF
- `google_scholar_internal(keyword, max_pages)` - Direct Google Scholar search
- `all_related_papers(query)` - Find related papers from multiple sources
- `custom_search(url, keyword, max_pages)` - Search custom site

**Summarization Methods:**
- `set_summarizer(summarizer_type)` - Set or change summarizer
- `summarize_papers(papers_df)` - Add summaries to papers DataFrame

**Semantic Search Methods:**
- `enable_semantic_search(embedder_model)` - Enable semantic re-ranking
- `semantic_rerank(query, papers_df, top_k)` - Re-rank papers by semantic similarity
- `init_vector_store(embedder_model, index_type)` - Initialize vector database
- `build_vector_index(papers_df)` - Build vector index from papers
- `semantic_search(query, k)` - Search vector store for similar papers
- `add_to_vector_index(papers_df)` - Add papers to existing index
- `save_vector_index(directory)` - Save index to disk
- `load_vector_index(directory)` - Load index from disk

**Personalization Methods:**
- `set_research_profile(profile)` - Set research profile (file path or ResearchProfile object)
- `rank_by_relevance(papers_df, threshold, api_key)` - Rank papers by LLM-based relevance (1-10)
- `fetch_daily_papers(days_back, max_papers)` - Fetch recent papers from profile categories

## Citation

If you find this repository useful, please cite our project:

```bibtex
@misc{Resp2021,
  title = {RESP: Research Papers Search and Summarization},
  author = {Pal, Ankit},
  year = {2021},
  howpublished = {\url{https://github.com/monk1337/resp}},
  note = {Fetch and Summarize Academic Research Papers from multiple sources}
}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Support

If you'd like to support this project, consider buying me a coffee :)

<p align="center">
<br>
<a href="https://www.buymeacoffee.com/stoicbatman"><img src="https://github.com/appcraftstudio/buymeacoffee/raw/master/Images/snapshot-bmc-button.png" width="300"></a>
</p>

[![Star History Chart](https://api.star-history.com/svg?repos=monk1337/resp&type=Date)](https://star-history.com/#monk1337/resp&Date)
