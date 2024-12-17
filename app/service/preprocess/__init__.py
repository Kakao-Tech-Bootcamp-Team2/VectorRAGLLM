from langchain_huggingface import HuggingFaceEmbeddings
import gc

class EmbeddingService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.model_name = "intfloat/multilingual-e5-large-instruct"
            cls._instance._embedding_model = None
        return cls._instance

    def __init__(self):
        pass

    def _load_model(self):
        if self._embedding_model is None:
            self._embedding_model = HuggingFaceEmbeddings(model_name=self.model_name)

    def _unload_model(self):
        if self._embedding_model is not None:
            del self._embedding_model
            self._embedding_model = None
            gc.collect()  # 메모리 정리

    def embed_text(self, texts):
        try:
            self._load_model()
            result = self._embedding_model.embed_documents(texts)
            return result
        finally:
            self._unload_model()

    def embed_query(self, query):
        try:
            self._load_model()
            result = self._embedding_model.embed_query(query)
            return result
        finally:
            self._unload_model()