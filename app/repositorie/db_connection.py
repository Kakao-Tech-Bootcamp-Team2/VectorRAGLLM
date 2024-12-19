from pinecone import Pinecone, ServerlessSpec
from app.core import setting
import gc
from typing import List, Dict, Final
import re
from threading import Lock

class DatabaseConnection:
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.index_name = "recipes"
                cls._instance.dimension = 1024
                cls._instance._connection_lock = Lock()
                cls._instance._index = None
                cls._instance._pc = None
            return cls._instance

    def __init__(self):
        pass

    def _load_connection(self):
        with self._connection_lock:
            if self._pc is None:
                self._pc = Pinecone(api_key=setting.PINECONE_API_KEY)
                
                # 인덱스 존재 여부 확인
                if self.index_name not in self._pc.list_indexes().names():
                    self._pc.create_index(
                        name=self.index_name,
                        dimension=self.dimension,
                        metric='cosine',
                        spec=ServerlessSpec(
                            cloud='aws',
                            region='us-east-1'
                        )
                    )
                    print(f"인덱스 '{self.index_name}'가 생성되었습니다.")
                else:
                    print(f"인덱스 '{self.index_name}'는 이미 존재합니다. 기존 인덱스를 사용합니다.")

                # 인덱스 불러오기
                self._index = self._pc.Index(self.index_name)

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
            print("Pinecone 연결이 정리되었습니다.")
        except Exception as e:
            print(f"연결 정리 중 오류 발생: {e}")

    async def upsert_recipe(self, recipe_id, embedding, metadata):
        try:
            self._load_connection()
            # ID로 기존 데이터 검색
            existing_data = self._index.fetch(ids=[str(recipe_id)])
            
            if existing_data.vectors:
                # 기존 데이터가 있으면 업데이트
                print(f"레시피 {recipe_id} 업데이트 중...")
                self._index.update(
                    id=str(recipe_id),
                    values=embedding,
                    metadata=metadata
                )
                return {"status": "updated"}
            else:
                # 새로운 데이터 삽입
                print(f"새로운 레시피 {recipe_id} 추가 중...")
                self._index.upsert(vectors=[{
                    'id': str(recipe_id),
                    'values': embedding,
                    'metadata': metadata
                }])
                return {"status": "inserted"}
        finally:
            self._unload_connection()

    def query(self, vector, top_k, include_metadata=True):
        try:
            self._load_connection()
            return self._index.query(
                vector=vector,
                top_k=top_k,
                include_metadata=include_metadata
            )
        finally:
            self._unload_connection()

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
    
    def extract_ingredient_name(self, ingredient:str) -> str:
        # 괄호와 슬래시, 물결표 등 불필요한 문자 제거
        return re.match(r'([^(/~]+)', ingredient).group(1).strip()
    
    def process_ingredients(self, recipe_metadata: Dict) -> List[str]:
        return [self.extract_ingredient_name(ing) for ing in recipe_metadata['ingredients']]