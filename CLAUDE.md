# CLAUDE.md - AI Assistant Guide for RESP

## Project Overview

**RESP (Research Papers Search)** is a Python library for fetching academic research papers from multiple sources including Google Scholar, ACL, ACM, PMLR, Arxiv, Semantic Scholar, NeurIPS, IJCAI, OpenReview, and CVF. The library provides a unified interface for searching papers by keywords or titles and can fetch citations, related papers, and connected papers.

**Repository**: https://github.com/monk1337/resp
**License**: Apache License 2.0
**Author**: Ankit Pal
**Version**: 0.0.0 (early stage)

## Codebase Structure

```
resp/
├── LICENSE                 # Apache 2.0 license
├── README.md              # Project documentation
├── requirements.txt       # Python dependencies
├── setup.py              # Package installation configuration
├── .gitignore            # Git ignore patterns
├── examples/
│   └── api_uses.py       # Usage examples (minimal)
└── resp/
    ├── __init__.py       # Package initialization (minimal)
    ├── resp.py           # Main API class with unified interface
    └── apis/
        ├── __init__.py   # APIs module initialization
        ├── serp_api.py   # SerpAPI integration for Google Scholar/Search
        ├── cnnp.py       # Connected Papers scraper using Selenium
        ├── semantic_s.py # Semantic Scholar API client
        ├── arxiv_api.py  # Arxiv search client
        └── acm_api.py    # ACM Digital Library scraper
```

## Architecture & Design Patterns

### Core Design

1. **Facade Pattern**: The `Resp` class in `resp/resp.py` provides a unified interface to multiple research paper sources.

2. **Modular API Design**: Each data source has its own dedicated module in `resp/apis/`:
   - `serp_api.py`: Handles Google Scholar and general Google searches via SerpAPI
   - `cnnp.py`: Scrapes Connected Papers using Selenium
   - `semantic_s.py`: Direct API integration with Semantic Scholar
   - `arxiv_api.py`: HTML scraping for Arxiv
   - `acm_api.py`: HTML scraping for ACM Digital Library

3. **Data Normalization**: All methods return pandas DataFrames with consistent columns: `title`, `link`, `snippet`, `source`, `keyword`

### Key Classes

#### `Resp` (resp/resp.py)
Main entry point for the library. Initialized with a SerpAPI key.

**Methods**:
- `acl(keyword, max_pages)`: Search ACL Anthology
- `pmlr(keyword, max_pages)`: Search PMLR proceedings
- `arxiv(keyword, max_pages)`: Search Arxiv
- `semantic_scholar(keyword, max_pages)`: Search Semantic Scholar
- `nips(keyword, max_pages)`: Search NeurIPS papers
- `ijcai(keyword, max_pages)`: Search IJCAI papers
- `openreview(keyword, max_pages)`: Search OpenReview
- `cvf(keyword, max_pages)`: Search CVF (CVPR/ICCV)
- `google_scholar(keyword, max_pages)`: Search Google Scholar
- `google_scholar_internal(keyword, max_pages)`: Direct Google Scholar API
- `custom_search(url, keyword, max_pages)`: Search custom domain
- `all_related_papers(query)`: Combine Connected Papers + Google Scholar related papers

#### `Serp` (resp/apis/serp_api.py)
Handles SerpAPI integration for Google-based searches.

**Key Methods**:
- `google_search(query, max_pages)`: Generic Google search with site restriction
- `google_scholar_search(q, max_pages)`: Google Scholar specific search
- `get_citations(query)`: Fetch all citations for a paper
- `get_related_pages(query)`: Fetch related papers from Google Scholar
- `pagination(cengine, max_pages, save_result)`: Handle paginated results

**Features**:
- Automatic pagination support
- JSON and CSV export of results
- MD5-based folder naming for caching
- Creates folders: `Google_data/Google_search/`, `Google_data/Google_Scholar/`, `Google_data/Citation_data/`, `Google_data/related_pages/`

#### `connected_papers` (resp/apis/cnnp.py)
Selenium-based scraper for Connected Papers.

**Key Methods**:
- `search_(query, result_n)`: Navigate and download BibTeX from Connected Papers
- `download_papers(query, n)`: Download top N paper graphs and parse them
- `bib2df(text)`: Convert BibTeX to pandas DataFrame

**Important**: Uses headless Chrome and creates `Connected_Papers_Data/` directory.

#### `Semantic_Scholar` (resp/apis/semantic_s.py)
Direct API client for Semantic Scholar.

**Key Methods**:
- `payload(keyword, page, min_year, max_year)`: Construct API request
- `ss(keyword, max_pages, min_year, max_year, api_wait)`: Fetch papers with year filtering

#### `Arxiv` (resp/apis/arxiv_api.py)
HTML scraper for Arxiv search results.

**Key Methods**:
- `arxiv(keyword, max_pages, api_wait)`: Fetch Arxiv papers

#### `ACM` (resp/apis/acm_api.py)
HTML scraper for ACM Digital Library.

**Key Methods**:
- `acm(keyword, max_pages, min_year, max_year, api_wait)`: Fetch ACM papers

## Dependencies

### Core Dependencies
- **beautifulsoup4**: HTML parsing for scrapers
- **requests**: HTTP client for API calls
- **pandas**: Data manipulation and DataFrame output
- **selenium**: Browser automation for Connected Papers
- **google-search-results (serpapi)**: SerpAPI Python client
- **pybtex**: BibTeX parsing
- **tqdm**: Progress bars

### Supporting Libraries
- **shutup**: Suppress warnings
- **latexcodec**: LaTeX encoding support
- Various async/crypto libraries for Selenium

## Development Workflows

### Setting Up Development Environment

```bash
git clone https://github.com/monk1337/resp
cd resp
pip install -r requirements.txt
pip install -e .
```

### Adding a New Data Source

1. **Create API module**: Add new file in `resp/apis/` (e.g., `new_source_api.py`)
2. **Create class**: Follow pattern of existing API classes
3. **Implement search method**: Return pandas DataFrame with columns: `title`, `link`, `snippet`
4. **Add to main class**: Import in `resp/resp.py` and add convenience method
5. **Test**: Ensure pagination, error handling, and data normalization work

### Code Conventions

#### Class Naming
- API classes use descriptive names: `Semantic_Scholar`, `ACM`, `Arxiv`, `connected_papers`
- Main interface class: `Resp`

#### Method Naming
- Lowercase with underscores: `google_search()`, `get_citations()`
- Private/internal methods prefixed with `_`: `_req_pagination()`

#### Data Storage Patterns
- Results stored in folders named by MD5 hash of query
- Both JSON (raw) and CSV (processed) formats saved
- Folder structure: `Google_data/{search_type}/{md5_hash}/`

#### Error Handling
- Check for API limit exhaustion: `if "error" in data`
- Use try-except blocks for HTML parsing failures
- Print error messages, continue processing other results

#### API Rate Limiting
- Include `api_wait` parameter (default: 5 seconds)
- Use `time.sleep(api_wait)` between requests
- Display progress with `tqdm` for long operations

## Data Flow

### Typical Search Flow
1. User calls `resp.{source}(keyword, max_pages)`
2. Resp class constructs site-restricted Google query: `site:{domain} {keyword}`
3. Query passed to `Serp.google_search()`
4. SerpAPI fetches results with pagination
5. Results filtered and normalized into DataFrame
6. Raw JSON and processed CSV saved to disk
7. DataFrame returned to user

### Citation/Related Papers Flow
1. User calls `resp.get_citations(query)` or `all_related_papers(query)`
2. Initial search finds paper on Google Scholar
3. Extract citation/related links from results
4. For each link, fetch full paginated results
5. Merge and deduplicate results
6. Return combined DataFrame

## Key Technical Considerations

### Authentication & API Keys

**SerpAPI Key Required**: The `Resp` class requires a SerpAPI key for initialization. This is used for Google Scholar and general Google searches.

```python
from resp.resp import Resp
api = Resp(api_key="your_serpapi_key")
```

### Web Scraping Considerations

1. **Selenium for Dynamic Content**: Connected Papers requires Selenium because content is JavaScript-rendered
2. **Rate Limiting**: All scrapers implement delays to avoid overwhelming servers
3. **User-Agent Spoofing**: Some APIs (Semantic Scholar, Arxiv) use mobile user agents
4. **Headless Browser**: Chrome runs in headless mode for Connected Papers

### Data Caching

- All searches automatically cache results to disk
- Cache organized by MD5 hash of query
- Both raw JSON and processed CSV formats saved
- No cache expiration mechanism implemented

### Output Format

Standard DataFrame columns:
- `title`: Paper title (string)
- `link`: URL to paper (string)
- `snippet`: Abstract/description (string, optional)
- `source`: Data source name (string, for merged results)
- `keyword`: Original search query (string, for merged results)

## Common Tasks for AI Assistants

### 1. Adding Support for a New Conference/Source

**Steps**:
1. Identify if source can use Google site search or needs custom scraper
2. For Google-based: Add method to `Resp` class following existing patterns
3. For custom API/scraper: Create new file in `resp/apis/`
4. Implement pagination, error handling, and data normalization
5. Test with various queries and edge cases
6. Update README.md with new source

**Example**:
```python
# In resp/resp.py
def iclr(self, keyword, max_pages=None):
    result = self.engine.google_search(
        f'site:openreview.net/group?id=ICLR.cc {keyword}',
        max_pages)
    return result
```

### 2. Fixing Scraping Issues

**Common Issues**:
- HTML structure changes: Check selectors in `soup.find()` calls
- API endpoint changes: Verify URLs in `requests.post()` calls
- Rate limiting: Increase `api_wait` parameter
- SerpAPI limits: Check API credits/quotas

**Debugging Approach**:
1. Test with simple query first
2. Print intermediate results (soup objects, API responses)
3. Check if error is in pagination or initial fetch
4. Verify folder creation doesn't fail

### 3. Enhancing Data Quality

**Recommendations**:
- Add duplicate detection across sources (currently only by `title` and `link`)
- Implement result ranking/scoring
- Add metadata extraction (authors, year, venue, citations count)
- Parse abstracts more consistently

### 4. Improving Performance

**Optimization Opportunities**:
- Implement async/await for parallel API calls
- Add proper caching layer with TTL
- Use connection pooling for requests
- Batch process multiple queries

### 5. Testing Strategy

**Current State**: No tests implemented

**Recommended Additions**:
```
tests/
├── test_resp.py           # Test main Resp class
├── test_serp_api.py       # Test SerpAPI integration
├── test_scrapers.py       # Test HTML scrapers
├── fixtures/
│   └── sample_responses/  # Mock API responses
└── conftest.py           # Pytest configuration
```

**Testing Considerations**:
- Mock external API calls to avoid rate limits
- Test pagination edge cases (0 results, 1 page, many pages)
- Verify DataFrame schema consistency
- Test error handling for API failures

### 6. Code Style & Best Practices

**Current Patterns to Follow**:
- Class-based organization for each API
- Pandas DataFrames as return type
- tqdm for progress indication
- Descriptive print statements for user feedback
- MD5 hashing for unique folder names

**Improvements to Consider**:
- Add type hints throughout codebase
- Implement proper logging instead of print statements
- Add docstrings to all public methods
- Create configuration file for API keys
- Implement proper exception hierarchy

### 7. Security Considerations

**Potential Issues**:
- API keys hardcoded in examples (use environment variables)
- No input sanitization on search queries
- Web scraping may violate terms of service
- Selenium downloads to predictable paths

**Recommendations**:
- Use `python-dotenv` for API key management
- Add input validation for queries
- Document legal/ethical use of scrapers
- Add option to disable local file caching

## Git Workflow

### Branching Strategy
- Main branch: `main`
- Feature branches: `claude/claude-md-{session-id}` (for AI assistants)

### Commit Conventions
- Use descriptive commit messages
- Reference issue numbers when applicable
- Group related changes in single commits

### Pull Request Process
1. Create feature branch from `main`
2. Make changes and commit
3. Push with: `git push -u origin <branch-name>`
4. Create PR with clear description
5. Include test plan if applicable

## Common Pitfalls to Avoid

1. **Forgetting SerpAPI Key**: Many methods fail silently without proper API key
2. **Not Checking API Limits**: SerpAPI has usage quotas that exhaust
3. **Selenium Chrome Driver**: Must have Chrome/Chromium installed for Connected Papers
4. **Folder Permissions**: Automatic folder creation may fail in restricted environments
5. **Pandas Concatenation**: Empty DataFrames can cause issues in `pd.concat()`
6. **HTML Changes**: Scrapers break when websites update their structure
7. **Encoding Issues**: Paper titles with special characters may need proper encoding

## Future Enhancements

### Recommended Priorities
1. Add comprehensive test suite
2. Implement async/concurrent fetching
3. Create command-line interface
4. Add proper configuration management
5. Implement result caching with expiration
6. Add paper metadata extraction (citations, authors)
7. Create documentation with Sphinx
8. Add GitHub Actions for CI/CD
9. Publish to PyPI with proper versioning
10. Add more data sources (DBLP, IEEE Xplore, etc.)

## Quick Reference

### Initialization
```python
from resp.resp import Resp
api = Resp(api_key="your_serpapi_key")
```

### Basic Search
```python
# Search specific venue
results = api.acl("transformer", max_pages=2)

# Search multiple sources
arxiv_results = api.arxiv("BERT", max_pages=3)
semantic_results = api.semantic_scholar("BERT", max_pages=3)

# Combine results
all_results = pd.concat([arxiv_results, semantic_results])
```

### Advanced Queries
```python
# Get all related papers
related = api.all_related_papers("Attention is All You Need")

# Custom domain search
results = api.custom_search("neurips.cc", "reinforcement learning", max_pages=5)
```

### File Locations
- Search results: `Google_data/Google_search/{md5}/`
- Citations: `Google_data/Citation_data/{md5}/`
- Related papers: `Google_data/related_pages/{md5}/`
- Connected Papers: `Connected_Papers_Data/`

## Support & Resources

- **Issues**: https://github.com/monk1337/resp/issues
- **Pull Requests**: https://github.com/monk1337/resp/pulls
- **Colab Demo**: https://colab.research.google.com/drive/188cWcZrBRVGAF3Dp_5uswmLgbBNKSioB

---

**Last Updated**: 2025-11-18
**For AI Assistants**: This document is specifically designed to help AI coding assistants understand the RESP codebase structure, conventions, and best practices when contributing to the project.
