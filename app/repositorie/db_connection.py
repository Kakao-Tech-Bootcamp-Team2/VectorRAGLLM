from pinecone import Pinecone, ServerlessSpec
from app.core import setting
from typing import List, Dict
from threading import Lock
from app.core.exception import DatabaseException
from app.core.logger import setup_logger
from app.core import setting
import re
import gc

logger = setup_logger(__name__)

class DatabaseConnection:
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.index_name = setting.VECTOR_DB_NAME
                cls._instance.dimension = setting.VECTOR_DIMENSION
                cls._instance._connection_lock = Lock()
                cls._instance._index = None
                cls._instance._pc = None
            return cls._instance

    def _load_connection(self):
        with self._connection_lock:
            try :
                if self._pc is None:
                    logger.info("Pinecone Connection Loading...")
                    self._pc = Pinecone(api_key=setting.PINECONE_API_KEY)
                
                    # 인덱스 존재 여부 확인
                    if self.index_name not in self._pc.list_indexes().names():
                        self._pc.create_index(
                            name=self.index_name,
                            dimension=self.dimension,
                            metric='cosine',
                            spec=ServerlessSpec(cloud='aws',region='us-east-1')
                    )
                    logger.info(f"index '{self.index_name}'create.")
                else:
                    logger.info("Pinecone '{self.index_name}'Connection Loaded.")
                # 인덱스 불러오기
                self._index = self._pc.Index(self.index_name)
            except Exception as e: 
                logger.error(f"Connection Error: {e}")
                raise DatabaseException("Pinecone Connection Error")

    def _unload_connection(self):
        try:
            if self._index is not None:
                # Index 객체 참조 제거
                del self._index
                self._index = None
                
            if self._pc is not None:
                # Pinecone 클라이언트 정리
                del self._pc
                self._pc = None
                
            # 강제로 가비지 컬렉션 실행
            gc.collect()
            logger.info("Connection Unloaded.")
        except Exception as e:
            logger.error(f"Connection Unload Error: {e}")
            raise DatabaseException("Pinecone Connection Unload Error")

    def query(self, vector, top_k, include_metadata=True):
        try:
            self._load_connection()
            result = self._index.query(
                vector=vector,
                top_k=top_k,
                include_metadata=include_metadata
            )
            return result
        except Exception as e: 
            logger.error(f"Query Error: {e}")
            raise DatabaseException("Pinecone Query Error")
        finally:
            self._unload_connection()

    @staticmethod
    # 재료 이름에서 양과 단위를 제거하는 함수
    def strip_quantities(self, ingredients: List[str]) -> List[str]:
        cleaned_ingredients = []
        for ingredient in ingredients:
            # 숫자와 단위 제거를 위한 더 포괄적인 패턴
            ingredient = re.sub(r'\d+\.?\d*[a-zA-Z가-힣]*', '', ingredient)
            # 분수 형태 제거
            ingredient = re.sub(r'\d+\/\d+', '', ingredient)
            # 측정 단위 제거
            ingredient = re.sub(r'(약간|T|t|컵|큰술|은술|숟가락|스푼|g|kg|ml|L)', '', ingredient)
            # 남은 숫자들 제거
            ingredient = re.sub(r'\d+', '', ingredient)
            # 특수문자 제거 (슬래시, 물결표 등)
            ingredient = re.sub(r'[/~]+', '', ingredient)
            # 양쪽 공백 제거하고 결과 추가
            cleaned = ingredient.strip()
            if cleaned:  # 빈 문자열이 아닌 경우만 추가
                cleaned_ingredients.append(cleaned)
        return cleaned_ingredients
    
    @staticmethod
    def extract_ingredient_name(self, ingredient:str) -> str:
        # 괄호와 슬래시, 물결표 등 불필요한 문자 제거
        return re.match(r'([^(/~]+)', ingredient).group(1).strip()
    
    @staticmethod
    def process_ingredients(self, recipe_metadata: Dict) -> List[str]:
        return [self.extract_ingredient_name(ing) for ing in recipe_metadata['ingredients']]