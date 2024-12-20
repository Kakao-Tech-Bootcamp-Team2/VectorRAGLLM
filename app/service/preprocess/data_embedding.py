from langchain_huggingface import HuggingFaceEmbeddings
from threading import Lock
from functools import lru_cache
from app.core import setting
from app.core.logger import setup_logger
from app.core.exception import EmbeddingException
import gc

logger = setup_logger(__name__)

class EmbeddingService:
    _lock = Lock()
    _instance = None

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.model_name = setting.MODEL_NAME
                cls._instance._embedding_model = None
                cls._instance._model_lock = Lock()
            return cls._instance

    def __init__(self):
        pass

    @lru_cache(maxsize=1)
    def _load_model(self):
        with self._model_lock:
            try:
                if self._embedding_model is None:
                    self._embedding_model = HuggingFaceEmbeddings(model_name=self.model_name)
            except Exception as e:
                raise EmbeddingException(f"모델 로드 중 오류 발생: {e}")

    def _unload_model(self):
        if self._embedding_model is not None:
            logger.info('model unload')
            del self._embedding_model
            self._embedding_model = None
            gc.collect()  # 메모리 정리

    def embed_text(self, texts):
        try:
            self._load_model()
            logger.info('model embed')
            return self._embedding_model.embed_documents(texts)
        except Exception as e:
            raise EmbeddingException(f"텍스트 임베딩 중 오류 발생: {e}")
        finally:
            self._unload_model()

    def embed_query(self, query):
        try:
            self._load_model()
            logger.info('model embed')
            return self._embedding_model.embed_query(query)
        except Exception as e: 
            raise EmbeddingException(f"쿼리 임베딩 중 오류 발생: {e}")
        finally:
            self._unload_model()