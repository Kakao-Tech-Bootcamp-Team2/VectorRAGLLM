from fastapi import APIRouter 
from app.service.search import search_recipes_by_text
from app.service.llm import generate_response
from app.service.preprocess.data_embedding import EmbeddingService
router = APIRouter()

@router.get("/recipes/search")
def search_recipes(query: str):
    return search_recipes_by_text(query)

@router.get("/recipes/llm")
async def generate_recipe(query: str):
    # 임베딩 서비스 인스턴스 재사용
    embedding_service = EmbeddingService()
    try:
        search_response = search_recipes_by_text(query, embedding_service)
        return generate_response(query, search_response)
    finally:
        embedding_service._unload_model()  # 작업 완료 후 모델 해제