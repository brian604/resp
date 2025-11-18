<h2 align="center">RESP: Research Papers Search and Summarization</h2>
<h4 align="center">Fetch and Summarize Academic Research Papers from Multiple Sources</h4>

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

### 🤖 AI Summarization (NEW!)
- **OpenAI API Support**: Use GPT models for high-quality summarization
- **OpenAI-Compatible APIs**: Support for DeepSeek, Groq, and other compatible services
- **Local Models**: Run summarization locally using Transformers or llama.cpp
- **Structured Summaries**: Generate concise summaries, key points, and TL;DRs
- **Batch Processing**: Summarize multiple papers efficiently

## Installation

### Basic Installation
```shell
git clone https://github.com/monk1337/resp
cd resp
pip install -r requirements.txt && pip install -e .
```

### With AI Summarization
```shell
# For OpenAI and compatible APIs
pip install -e ".[summarization]"

# For local models (transformers)
pip install -e ".[local]"

# Install everything
pip install -e ".[all]"
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

**Transformers models** (require `pip install transformers torch`):
- `facebook/bart-large-cnn` - Good general summarizer
- `google/flan-t5-base` - Instruction-tuned model
- `philschmid/flan-t5-base-samsum` - Conversation summarization
- Any Seq2Seq model on Hugging Face

**llama.cpp models** (require `pip install llama-cpp-python`):
- Any GGUF format model
- Llama, Mistral, Phi, etc.

## Examples

Check the `examples/` directory for more detailed examples:

```python
# See examples/api_uses.py for comprehensive examples
# Or open examples/Api_examples.ipynb in Jupyter
```

## API Reference

### Main Class: `Resp`

#### Constructor
```python
Resp(api_key=None, config=None, summarizer=None)
```
- `api_key`: SerpAPI key (optional)
- `config`: Config object (optional)
- `summarizer`: 'openai', 'local', or None

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
