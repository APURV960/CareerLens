import threading
from sentence_transformers import SentenceTransformer

class EmbeddingService:
    """
    Centralized, thread-safe, lazy-loaded singleton service for generating embeddings
    using the 'all-MiniLM-L6-v2' model.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(EmbeddingService, cls).__new__(cls, *args, **kwargs)
                    cls._instance._model = None
        return cls._instance

    @property
    def model(self):
        """
        Lazily instantiates the SentenceTransformer model on first access.
        """
        if self._model is None:
            # Load the model only when it is actually needed
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
        return self._model

    def encode(self, texts, **kwargs):
        """
        Generates embeddings for the provided text or list of texts.
        """
        return self.model.encode(texts, **kwargs)
