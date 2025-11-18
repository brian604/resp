import requests
import json
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
from typing import Optional, List, Dict
from resp.apis.serp_api import Serp
from resp.apis.cnnp import connected_papers
from resp.apis.arxiv_api import Arxiv
from resp.config import Config


class Resp(object):

    def __init__(
        self,
        api_key: Optional[str] = None,
        config: Optional[Config] = None,
        summarizer: Optional[str] = None,
        enable_semantic_search: bool = False,
        embedder_model: str = "multi-qa-MiniLM-L6-cos-v1"
    ):
        """
        Initialize RESP with search, summarization, and semantic search capabilities.

        Args:
            api_key: SerpAPI key for Google Scholar searches
            config: Configuration object (creates default if None)
            summarizer: Summarizer type ('openai', 'local', or None to disable)
            enable_semantic_search: Enable semantic search/re-ranking
            embedder_model: Model to use for embeddings (SentenceTransformers model name)
        """
        # Initialize configuration
        self.config = config or Config()

        # Get API key from parameter, config, or environment
        if api_key:
            self.serp_api_key = api_key
        else:
            self.serp_api_key = self.config.get_api_key('serp_api')

        # Initialize search engine
        if self.serp_api_key:
            self.engine = Serp(self.serp_api_key)
        else:
            self.engine = None
            print("Warning: No SerpAPI key provided. Google Scholar searches will not work.")

        # Initialize arXiv API
        self.arxiv_engine = Arxiv()

        # Initialize summarizer if requested
        self._summarizer = None
        if summarizer:
            self._init_summarizer(summarizer)

        # Initialize semantic search components
        self._semantic_reranker = None
        self._vector_store = None
        if enable_semantic_search:
            self._init_semantic_search(embedder_model)

    def _init_semantic_search(self, embedder_model: str):
        """Initialize semantic search components."""
        try:
            from resp.semantic_search import SentenceTransformerEmbedder, SemanticReranker
            embedder = SentenceTransformerEmbedder(model_name=embedder_model)
            self._semantic_reranker = SemanticReranker(embedder=embedder)
            print(f"Semantic search initialized with model: {embedder_model}")
        except Exception as e:
            print(f"Warning: Could not initialize semantic search: {e}")
            print("Install with: pip install sentence-transformers")
            self._semantic_reranker = None

    def enable_semantic_search(self, embedder_model: str = "multi-qa-MiniLM-L6-cos-v1"):
        """
        Enable semantic search/re-ranking.

        Args:
            embedder_model: SentenceTransformers model name
        """
        self._init_semantic_search(embedder_model)

    def init_vector_store(
        self,
        embedder_model: str = "multi-qa-MiniLM-L6-cos-v1",
        index_type: str = "flat"
    ):
        """
        Initialize vector store for semantic search.

        Args:
            embedder_model: SentenceTransformers model name
            index_type: FAISS index type ('flat', 'ivf', 'hnsw')
        """
        try:
            from resp.semantic_search import SentenceTransformerEmbedder, VectorStore
            embedder = SentenceTransformerEmbedder(model_name=embedder_model)
            self._vector_store = VectorStore(embedder=embedder, index_type=index_type)
            print(f"Vector store initialized with {index_type} index")
        except Exception as e:
            print(f"Warning: Could not initialize vector store: {e}")
            print("Install with: pip install sentence-transformers faiss-cpu")
            self._vector_store = None

    def _init_summarizer(self, summarizer_type: str):
        """Initialize the specified summarizer."""
        try:
            if summarizer_type == 'openai':
                from resp.summarizers import OpenAISummarizer
                summarizer_config = self.config.get_summarizer_config('openai')
                api_key = self.config.get_api_key('openai')
                self._summarizer = OpenAISummarizer(
                    api_key=api_key,
                    **summarizer_config
                )
            elif summarizer_type == 'local':
                from resp.summarizers import LocalSummarizer
                summarizer_config = self.config.get_summarizer_config('local')
                self._summarizer = LocalSummarizer(**summarizer_config)
            else:
                print(f"Warning: Unknown summarizer type: {summarizer_type}")
        except Exception as e:
            print(f"Warning: Could not initialize summarizer: {e}")
            self._summarizer = None

    def set_summarizer(self, summarizer_type: str):
        """
        Set or change the summarizer.

        Args:
            summarizer_type: 'openai', 'local', or None to disable
        """
        if summarizer_type is None:
            self._summarizer = None
        else:
            self._init_summarizer(summarizer_type)

    def summarize_papers(self, papers_df: pd.DataFrame) -> pd.DataFrame:
        """
        Add AI-generated summaries to papers DataFrame.

        Args:
            papers_df: DataFrame with 'title' and 'abstract' columns

        Returns:
            DataFrame with added summary columns
        """
        if self._summarizer is None:
            print("Warning: No summarizer initialized. Call set_summarizer() first.")
            return papers_df

        if 'abstract' not in papers_df.columns:
            print("Warning: No 'abstract' column found in DataFrame.")
            return papers_df

        print("Generating summaries...")
        papers_list = papers_df.to_dict('records')
        summarized_papers = self._summarizer.summarize_batch(papers_list)

        return pd.DataFrame(summarized_papers)

    def semantic_rerank(
        self,
        query: str,
        papers_df: pd.DataFrame,
        top_k: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Re-rank papers using semantic similarity.

        Args:
            query: Search query
            papers_df: DataFrame of papers to re-rank
            top_k: Number of top results to return

        Returns:
            Re-ranked DataFrame with semantic_score column
        """
        if self._semantic_reranker is None:
            print("Warning: Semantic search not initialized.")
            print("Enable with: resp.enable_semantic_search()")
            return papers_df

        return self._semantic_reranker.rerank_dataframe(query, papers_df, top_k)

    def semantic_search(
        self,
        query: str,
        k: int = 20
    ) -> pd.DataFrame:
        """
        Search vector store for papers semantically similar to query.

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            DataFrame of semantically similar papers
        """
        if self._vector_store is None:
            print("Warning: Vector store not initialized.")
            print("Initialize with: resp.init_vector_store()")
            return pd.DataFrame()

        results = self._vector_store.search(query, k=k)
        return pd.DataFrame(results)

    def build_vector_index(self, papers_df: pd.DataFrame):
        """
        Build vector index from papers DataFrame.

        Args:
            papers_df: DataFrame of papers with title and abstract
        """
        if self._vector_store is None:
            print("Warning: Vector store not initialized.")
            print("Initialize with: resp.init_vector_store()")
            return

        papers_list = papers_df.to_dict('records')
        self._vector_store.build_index(papers_list)

    def add_to_vector_index(self, papers_df: pd.DataFrame):
        """
        Add papers to existing vector index.

        Args:
            papers_df: DataFrame of papers to add
        """
        if self._vector_store is None:
            print("Warning: Vector store not initialized.")
            return

        papers_list = papers_df.to_dict('records')
        self._vector_store.add_papers(papers_list)

    def save_vector_index(self, directory: str):
        """
        Save vector index to disk.

        Args:
            directory: Directory to save index
        """
        if self._vector_store is None:
            print("Warning: Vector store not initialized.")
            return

        self._vector_store.save(directory)

    def load_vector_index(self, directory: str):
        """
        Load vector index from disk.

        Args:
            directory: Directory containing saved index
        """
        if self._vector_store is None:
            self.init_vector_store()

        self._vector_store.load(directory)

    def acl(self, keyword, max_pages = None, summarize: bool = False):
        result  = self.engine.google_search(
            f'site:aclanthology.org {keyword}', 
                                            max_pages)
        return result
    
    def pmlr(self, keyword, max_pages = None):
        result  = self.engine.google_search(
            f'site:proceedings.mlr.press {keyword}', 
                                            max_pages)
        return result
    
    def arxiv(self, keyword, max_pages = None, summarize: bool = False):
        """
        Search arXiv using Google (via SerpAPI).

        Args:
            keyword: Search keyword
            max_pages: Maximum pages to fetch
            summarize: Whether to generate summaries (requires abstracts)

        Returns:
            DataFrame with paper information
        """
        if not self.engine:
            print("Error: SerpAPI key required for this method. Use arxiv_direct() instead.")
            return pd.DataFrame()

        result = self.engine.google_search(
            f'site:arxiv.org {keyword}',
            max_pages)

        if summarize and self._summarizer:
            result = self.summarize_papers(result)

        return result

    def arxiv_direct(
        self,
        keyword: str,
        max_pages: int = 5,
        use_api: bool = True,
        summarize: bool = False
    ):
        """
        Search arXiv directly using arXiv API or web scraping.
        This method includes abstracts and doesn't require SerpAPI.

        Args:
            keyword: Search keyword
            max_pages: Number of pages to fetch
            use_api: Use official arXiv API (True) or web scraping (False)
            summarize: Whether to generate AI summaries

        Returns:
            DataFrame with paper information including abstracts
        """
        result = self.arxiv_engine.arxiv(
            keyword=keyword,
            max_pages=max_pages,
            use_api=use_api,
            include_abstract=True
        )

        if summarize and self._summarizer and not result.empty:
            result = self.summarize_papers(result)

        return result
    
    
    def semantic_scholar(self, keyword, max_pages = None):
        result  = self.engine.google_search(
            f'site:www.semanticscholar.org {keyword}', 
                                            max_pages)
        return result
    
    
    def nips(self, keyword, max_pages = None):
        result  = self.engine.google_search(
            f'site:papers.nips.cc {keyword}', 
                                            max_pages)
        return result
    
    
    def ijcai(self, keyword, max_pages = None):
        result  = self.engine.google_search(
            f'site:www.ijcai.org {keyword}', 
                                            max_pages)
        return result
    
    
    def openreview(self, keyword, max_pages = None):
        result  = self.engine.google_search(
            f'site:openreview.net {keyword}', 
                                            max_pages)
        return result
    
    def cvf(self, keyword, max_pages = None):
        result  = self.engine.google_search(
            f'site:openaccess.thecvf.com {keyword}', 
                                            max_pages)
        return result
    
    def google_scholar(self, keyword, max_pages = None):
        result  = self.engine.google_search(
            f'site:scholar.google.com {keyword}', 
                                            max_pages)
        return result
    
    def google_scholar_internal(self, keyword, max_pages = None):
        result = self.engine.google_scholar_search(keyword, 
                                                   max_pages)
        return result
    
    def custom_search(self, url, keyword, max_pages = None):
        result  = self.engine.google_search(
            f'site:{url} {keyword}', max_pages)
        return result


    def all_related_papers(self, query):
        """download all related papers from two sources"""

        result = []
        cp = connected_papers()
        rl_result = cp.download_papers(query, n=1)
        rl_result["source"] = ["connected_papers"] * len(rl_result)
        rl_result["keyword"] = [query] * len(rl_result)
        rl_result = rl_result.loc[:, ~rl_result.columns.str.contains("^Unnamed")]
        rl_result["title"] = rl_result["title"].str.lower()
        result.append(rl_result)
        
        rl_resultgp = self.engine.get_related_pages(query)
        rl_resultgp = rl_resultgp[list(rl_resultgp.keys())[0]]
        rl_resultgp["source"] = ["google_scholar"] * len(rl_resultgp)
        rl_resultgp["keyword"] = [query] * len(rl_resultgp)
        rl_resultgp["title"] = rl_resultgp["title"].str.lower()
        result.append(rl_resultgp)

        df = pd.concat(result)
        df = df.drop_duplicates("title", keep="last")
        df = df.drop_duplicates("link", keep="last")
        df = df[["title", "link", "source", "keyword"]]
        return df.reset_index(drop=True)