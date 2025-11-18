"""
Local model summarizer using transformers or llama-cpp-python.
"""

from typing import Dict, Optional
from resp.summarizers.base import BaseSummarizer

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False


class LocalSummarizer(BaseSummarizer):
    """
    Summarizer using local models via transformers or llama-cpp-python.

    Supports:
    - Transformers models (BART, T5, Pegasus, etc.)
    - GGUF models via llama.cpp
    """

    def __init__(
        self,
        model_type: str = "transformers",
        model_name: str = "facebook/bart-large-cnn",
        model_path: Optional[str] = None,
        device: str = "cpu",
        max_length: int = 150,
        min_length: int = 50,
        **kwargs
    ):
        """
        Initialize local model summarizer.

        Args:
            model_type: "transformers" or "llama_cpp"
            model_name: Model name/identifier for transformers
                       (e.g., "facebook/bart-large-cnn", "google/flan-t5-base")
            model_path: Path to local GGUF model file (for llama_cpp)
            device: Device to run on ("cpu", "cuda", "mps")
            max_length: Maximum length of generated summary
            min_length: Minimum length of generated summary
            **kwargs: Additional parameters
        """
        super().__init__(**kwargs)

        self.model_type = model_type
        self.max_length = max_length
        self.min_length = min_length

        if model_type == "transformers":
            if not TRANSFORMERS_AVAILABLE:
                raise ImportError(
                    "Transformers not installed. Install with: pip install transformers torch"
                )
            self._init_transformers_model(model_name, device)

        elif model_type == "llama_cpp":
            if not LLAMA_CPP_AVAILABLE:
                raise ImportError(
                    "llama-cpp-python not installed. Install with: pip install llama-cpp-python"
                )
            if not model_path:
                raise ValueError("model_path required for llama_cpp model type")
            self._init_llama_cpp_model(model_path, **kwargs)

        else:
            raise ValueError(f"Unknown model_type: {model_type}")

    def _init_transformers_model(self, model_name: str, device: str):
        """Initialize a transformers model."""
        try:
            self.summarizer = pipeline(
                "summarization",
                model=model_name,
                device=device if device != "cpu" else -1
            )
        except Exception as e:
            # Fallback to manual loading for better error handling
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
                if device != "cpu":
                    self.model = self.model.to(device)
                self.summarizer = None
            except Exception as e2:
                raise Exception(f"Error loading model {model_name}: {str(e2)}")

    def _init_llama_cpp_model(self, model_path: str, **kwargs):
        """Initialize a llama.cpp model."""
        llama_kwargs = {
            "model_path": model_path,
            "n_ctx": kwargs.get("n_ctx", 2048),
            "n_threads": kwargs.get("n_threads", 4),
            "n_gpu_layers": kwargs.get("n_gpu_layers", 0),
        }
        try:
            self.llm = Llama(**llama_kwargs)
        except Exception as e:
            raise Exception(f"Error loading llama.cpp model: {str(e)}")

    def summarize(self, text: str, max_length: Optional[int] = None) -> str:
        """
        Generate a summary of the input text.

        Args:
            text: The text to summarize
            max_length: Maximum length (overrides default if provided)

        Returns:
            The generated summary
        """
        max_len = max_length if max_length else self.max_length

        if self.model_type == "transformers":
            return self._summarize_transformers(text, max_len)
        elif self.model_type == "llama_cpp":
            return self._summarize_llama_cpp(text, max_len)

    def _summarize_transformers(self, text: str, max_length: int) -> str:
        """Summarize using transformers model."""
        try:
            if self.summarizer:
                # Use pipeline
                result = self.summarizer(
                    text,
                    max_length=max_length,
                    min_length=self.min_length,
                    do_sample=False
                )
                return result[0]['summary_text']
            else:
                # Use manual model/tokenizer
                inputs = self.tokenizer(
                    text,
                    max_length=1024,
                    truncation=True,
                    return_tensors="pt"
                )
                summary_ids = self.model.generate(
                    inputs["input_ids"],
                    max_length=max_length,
                    min_length=self.min_length,
                    num_beams=4,
                    early_stopping=True
                )
                return self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)

        except Exception as e:
            raise Exception(f"Error in transformers summarization: {str(e)}")

    def _summarize_llama_cpp(self, text: str, max_length: int) -> str:
        """Summarize using llama.cpp model."""
        prompt = f"""Summarize the following research paper abstract concisely:

{text}

Summary:"""

        try:
            output = self.llm(
                prompt,
                max_tokens=max_length,
                temperature=0.3,
                stop=["</s>", "\n\n"]
            )
            return output['choices'][0]['text'].strip()

        except Exception as e:
            raise Exception(f"Error in llama.cpp summarization: {str(e)}")

    def summarize_paper(self, title: str, abstract: str) -> Dict[str, str]:
        """
        Generate a structured summary of a research paper.

        Args:
            title: Paper title
            abstract: Paper abstract

        Returns:
            Dictionary containing summary, key_points, and tldr
        """
        # For local models, we'll generate a simple summary
        # More complex structured output would require fine-tuned models
        try:
            full_text = f"Title: {title}\n\nAbstract: {abstract}"
            summary = self.summarize(full_text)

            # Generate a shorter TLDR
            tldr = summary.split('.')[0] + '.' if '.' in summary else summary[:100]

            return {
                'summary': summary,
                'key_points': summary,  # For simple models, same as summary
                'tldr': tldr
            }

        except Exception as e:
            return {
                'summary': f"Error generating summary: {str(e)}",
                'key_points': '',
                'tldr': ''
            }
