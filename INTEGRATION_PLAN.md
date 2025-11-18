# ArxivDigest Integration Plan

## Comparison: RESP vs ArxivDigest

### Current RESP Capabilities
✅ **Multi-source paper search** (9+ sources: arXiv, ACL, PMLR, Semantic Scholar, etc.)
✅ **Official arXiv API integration** with full metadata
✅ **AI Summarization** (OpenAI, DeepSeek, local models)
✅ **Semantic Search** (embeddings, vector DB, re-ranking)
✅ **Flexible architecture** (API-based, modular)
✅ **Multiple embedding models** (SentenceTransformers, OpenAI)
✅ **Persistent vector indices** (FAISS)
✅ **Batch processing**

### ArxivDigest Unique Features
🎯 **Personalized relevance ranking** (1-10 scale using LLM)
🎯 **Natural language interest profiles** (not just keywords)
🎯 **Automated daily digests** (GitHub Actions scheduling)
🎯 **Email delivery** (SendGrid integration)
🎯 **HTML digest generation** (sortable, formatted output)
🎯 **Negative filtering** ("do not care about" specifications)
🎯 **Gradio web UI** (interactive configuration)
🎯 **YAML-based configuration** (user preferences)

---

## Key Differences

| Aspect | RESP | ArxivDigest |
|--------|------|-------------|
| **Scope** | Broad (multiple sources) | Focused (arXiv only) |
| **Search** | Keyword + Semantic | Category-based |
| **Ranking** | Semantic similarity | LLM relevance scoring |
| **Personalization** | Query-based | Profile-based |
| **Automation** | Manual/Script | GitHub Actions daily |
| **Output** | DataFrame/CSV | HTML digest + Email |
| **Configuration** | Python API | YAML file |
| **UI** | None | Gradio web interface |
| **Focus** | Research tool/library | Daily digest service |

---

## Integration Strategy

### Phase 1: Core Personalization Features (HIGH PRIORITY)

#### 1.1 User Interest Profiles
**Goal**: Enable natural language research interest specification

```python
# New module: resp/personalization/profile.py
class ResearchProfile:
    - Load from YAML/JSON
    - Define interests (natural language)
    - Define exclusions (topics to avoid)
    - Multiple profiles per user
    - Profile templates (ML, NLP, CV, etc.)
```

**Files to create**:
- `resp/personalization/__init__.py`
- `resp/personalization/profile.py`
- `resp/personalization/scorer.py`

#### 1.2 LLM-Based Relevance Scoring
**Goal**: Score papers against user interests using LLM

```python
# New module: resp/personalization/scorer.py
class RelevanceScorer:
    - Score papers 1-10 against profile
    - Use OpenAI/compatible APIs
    - Batch scoring for efficiency
    - Caching for cost optimization
    - Explanation generation (why relevant?)
```

**Features**:
- Single paper scoring
- Batch scoring (100+ papers)
- Cost tracking
- Configurable models (gpt-3.5, gpt-4, etc.)
- Rate limiting

#### 1.3 Integration with Existing Search
**Goal**: Add relevance scoring to search results

```python
# Enhanced Resp class
resp = Resp()
resp.set_research_profile("my_interests.yaml")

papers = resp.arxiv_direct("machine learning", max_pages=5)
ranked_papers = resp.rank_by_relevance(papers)  # Adds relevance_score column
```

---

### Phase 2: Digest Generation (MEDIUM PRIORITY)

#### 2.1 HTML Digest Generator
**Goal**: Create beautiful, sortable HTML digests

```python
# New module: resp/digest/generator.py
class DigestGenerator:
    - HTML template (sortable table)
    - Filtering by score threshold
    - Categorization by topic
    - Summary cards
    - Export to HTML file
```

**Features**:
- Responsive design
- Sortable columns (title, score, date)
- Filterable by category/score
- Dark/light theme
- PDF export option

#### 2.2 Email Delivery
**Goal**: Send digests via email

```python
# New module: resp/digest/email_sender.py
class EmailSender:
    - SendGrid integration
    - SMTP fallback
    - HTML email formatting
    - Attachment support
    - Scheduling
```

**Providers**:
- SendGrid (recommended)
- SMTP (Gmail, Outlook, custom)
- AWS SES (optional)

---

### Phase 3: Automation & Scheduling (MEDIUM PRIORITY)

#### 3.1 Daily Digest Workflow
**Goal**: Automate daily paper discovery

```python
# New module: resp/automation/digest_workflow.py
class DigestWorkflow:
    - Load profile
    - Fetch new papers (last 24h)
    - Score and rank
    - Generate digest
    - Send email
    - Log results
```

#### 3.2 GitHub Actions Integration
**Goal**: Enable serverless automation

**Files to create**:
- `.github/workflows/daily-digest.yml`
- `.github/workflows/weekly-digest.yml`
- Template repository for users to fork

**Features**:
- Scheduled runs (daily/weekly)
- Manual trigger
- Secrets management
- Result artifacts

---

### Phase 4: Advanced Features (LOWER PRIORITY)

#### 4.1 Web Interface (Gradio)
**Goal**: Interactive configuration and preview

```python
# New file: resp/ui/app.py
- Configure research profile
- Preview results
- Test queries
- Download digests
- Manage profiles
```

#### 4.2 Enhanced Filtering
**Goal**: Sophisticated paper filtering

```python
# Enhanced scoring system
- Multi-dimensional scoring (novelty, impact, relevance)
- Author-based filtering
- Citation count weighting
- Publication venue preferences
- Recency bias
```

#### 4.3 Paper Recommendations
**Goal**: Discover related papers

```python
# New module: resp/recommendations/engine.py
- "Papers similar to this one"
- "Papers citing this work"
- "Papers by same authors"
- Collaborative filtering
```

---

## Implementation Roadmap

### Week 1-2: Foundation
- [ ] Create `resp/personalization/` module
- [ ] Implement `ResearchProfile` class
- [ ] Implement `RelevanceScorer` class
- [ ] Add YAML/JSON profile loading
- [ ] Integrate with main `Resp` class
- [ ] Write comprehensive tests

### Week 3-4: Digest Generation
- [ ] Create `resp/digest/` module
- [ ] Implement HTML generator
- [ ] Create email templates
- [ ] Implement email sender (SendGrid + SMTP)
- [ ] Add digest scheduling
- [ ] Create example templates

### Week 5-6: Automation
- [ ] Create GitHub Actions workflows
- [ ] Template repository setup
- [ ] Documentation for forking
- [ ] Implement `DigestWorkflow`
- [ ] Add logging and monitoring
- [ ] Cost optimization

### Week 7-8: Polish & Advanced
- [ ] Gradio web interface
- [ ] Enhanced filtering
- [ ] Recommendation engine
- [ ] Performance optimization
- [ ] Comprehensive documentation
- [ ] Example configurations

---

## Technical Design

### Architecture Overview

```
resp/
├── personalization/
│   ├── __init__.py
│   ├── profile.py          # ResearchProfile class
│   ├── scorer.py           # RelevanceScorer class
│   └── templates/          # Profile templates
│       ├── ml.yaml
│       ├── nlp.yaml
│       └── cv.yaml
│
├── digest/
│   ├── __init__.py
│   ├── generator.py        # DigestGenerator class
│   ├── email_sender.py     # EmailSender class
│   ├── templates/          # HTML templates
│   │   ├── default.html
│   │   └── modern.html
│   └── assets/            # CSS, JS
│
├── automation/
│   ├── __init__.py
│   ├── workflow.py         # DigestWorkflow class
│   └── scheduler.py        # Scheduling utilities
│
└── ui/                     # Optional Gradio interface
    └── app.py
```

### Data Flow

```
1. User defines research interests (YAML)
   ↓
2. RESP fetches papers (arXiv API)
   ↓
3. RelevanceScorer ranks papers (LLM)
   ↓
4. DigestGenerator creates HTML
   ↓
5. EmailSender delivers digest
   ↓
6. Optional: GitHub Actions automation
```

---

## Configuration Example

```yaml
# ~/.resp/profiles/my_interests.yaml

profile:
  name: "ML Research Profile"
  email: "user@example.com"

arxiv:
  subjects: ["cs"]
  categories:
    - "cs.LG"  # Machine Learning
    - "cs.AI"  # Artificial Intelligence
    - "cs.CL"  # Computation and Language

interests:
  primary:
    - "Large language models and their applications"
    - "Efficient fine-tuning methods like LoRA and QLoRA"
    - "Multi-modal learning combining vision and language"

  secondary:
    - "Reinforcement learning from human feedback"
    - "Model interpretability and explainability"

  exclusions:
    - "Pure theoretical papers without experiments"
    - "Papers focused only on medical imaging"
    - "Hardware-specific optimizations"

scoring:
  model: "gpt-3.5-turbo"
  threshold: 6.0  # Minimum relevance score
  max_papers: 50  # Papers to score per run

digest:
  format: "html"
  template: "modern"
  frequency: "daily"
  time: "08:00 UTC"

email:
  enabled: true
  provider: "sendgrid"
  subject: "Daily ML Papers Digest"
```

---

## API Design

### Basic Usage

```python
from resp import Resp
from resp.personalization import ResearchProfile

# Initialize with profile
resp = Resp()
profile = ResearchProfile.from_yaml("my_interests.yaml")
resp.set_profile(profile)

# Fetch and rank papers
papers = resp.fetch_daily_papers()  # Last 24 hours
ranked = resp.rank_papers(papers)

# Generate digest
from resp.digest import DigestGenerator
generator = DigestGenerator(template="modern")
html = generator.generate(ranked, profile)

# Send email
from resp.digest import EmailSender
sender = EmailSender(provider="sendgrid")
sender.send(html, to=profile.email)
```

### Advanced Usage

```python
# Multi-profile support
profiles = [
    ResearchProfile.from_yaml("ml.yaml"),
    ResearchProfile.from_yaml("nlp.yaml"),
]

for profile in profiles:
    papers = resp.fetch_papers(profile.categories)
    ranked = resp.rank_papers(papers, profile)
    digest = generator.generate(ranked, profile)
    sender.send(digest, to=profile.email)
```

### Automation Script

```python
# scripts/daily_digest.py
from resp.automation import DigestWorkflow

workflow = DigestWorkflow(
    profile="my_interests.yaml",
    output_dir="digests/"
)

workflow.run()  # Fetch, rank, generate, send
```

---

## Key Improvements Over ArxivDigest

### 1. **Multi-Source Support**
- Not limited to arXiv
- Can aggregate from ACL, PMLR, Semantic Scholar, etc.
- Cross-source deduplication

### 2. **Hybrid Ranking**
- Combine LLM scoring with semantic similarity
- Multiple ranking strategies
- Ensemble approaches

### 3. **Advanced Personalization**
- Multiple interest profiles
- Time-based preferences
- Learning from user feedback

### 4. **Better Architecture**
- Modular design
- Extensible scoring system
- Plugin-based email providers
- Multiple output formats

### 5. **Cost Optimization**
- Semantic pre-filtering (reduce LLM calls)
- Caching and batching
- Configurable models
- Local model support

---

## Dependencies to Add

```python
# setup.py additions
personalization_deps = [
    'openai>=1.0.0',  # Already have
    'pyyaml>=6.0',     # Already have
]

digest_deps = [
    'jinja2>=3.0.0',           # HTML templating
    'sendgrid>=6.9.0',         # Email delivery
    'python-dotenv>=1.0.0',    # Environment variables
]

ui_deps = [
    'gradio>=3.40.0',          # Web interface
]

# Update extras_require
extras_require={
    'personalization': personalization_deps,
    'digest': digest_deps,
    'ui': ui_deps,
    'all': (summarization_deps + local_models_deps +
            semantic_search_deps + personalization_deps +
            digest_deps + ui_deps),
}
```

---

## Migration Path for ArxivDigest Users

### Easy Migration

1. **Convert config.yaml to RESP format**
   ```bash
   python -m resp.tools.convert_arxivdigest_config config.yaml
   ```

2. **Run with RESP**
   ```bash
   resp digest --profile my_interests.yaml --send-email
   ```

3. **Schedule with GitHub Actions**
   - Fork template repo
   - Add profile
   - Set secrets
   - Enable workflow

---

## Success Metrics

- ✅ Personalized relevance scoring (1-10 scale)
- ✅ Natural language interest profiles
- ✅ Automated daily digests
- ✅ Email delivery (multiple providers)
- ✅ HTML digest generation
- ✅ GitHub Actions automation
- ✅ Better than ArxivDigest in every way
- ✅ Backward compatible with RESP
- ✅ Zero breaking changes

---

## Next Steps

1. Review and approve this plan
2. Set up development branch
3. Implement Phase 1 (personalization)
4. Create examples and documentation
5. Beta testing with users
6. Full release

---

## Questions to Resolve

1. **Scoring model defaults**: gpt-3.5-turbo or gpt-4?
2. **Email provider priority**: SendGrid first or SMTP?
3. **UI necessity**: Gradio or CLI-only initially?
4. **Profile format**: YAML, JSON, or both?
5. **Digest frequency**: Daily only or configurable?
6. **Cost limits**: Max API spend per digest?
7. **Storage**: Where to save digests long-term?

---

## Timeline Estimate

- **Phase 1 (Personalization)**: 2-3 weeks
- **Phase 2 (Digest Generation)**: 2 weeks
- **Phase 3 (Automation)**: 1-2 weeks
- **Phase 4 (Advanced)**: 3-4 weeks

**Total**: 8-11 weeks for full implementation

**MVP** (Phases 1-2): 4-5 weeks
