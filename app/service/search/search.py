from typing import List, Dict
from app.repositorie.db_connection import DatabaseConnection
from app.service.preprocess.data_embedding import EmbeddingService
from app.core.logger import setup_logger
from app.core.exception import AppException
import gc

logger = setup_logger(__name__)

class RecipeSearchService:
    def __init__(self, embedding_service: EmbeddingService = None):
        self.embedding_service = embedding_service or EmbeddingService()

    async def search_recipes_by_text(self, query: str, top_k: int = 500) -> List[Dict]:
        """텍스트 쿼리로 레시피 검색"""
        try:
            # 쿼리 전처리
            query_ingredients = self._preprocess_query(query)
            query_text = " ".join(query_ingredients)
            logger.debug(f"전처리된 쿼리 재료: {query_ingredients}")
            logger.debug(f"임베딩할 텍스트: {query_text}")
            
            # 쿼리 임베딩
            query_embedding = self.embedding_service.embed_query(query_text)
            logger.debug(f"임베딩 벡터 길이: {len(query_embedding)}")
            
            return await self._search_recipes(query_embedding, query_ingredients, top_k)
            
        except Exception as e:
            logger.error(f"레시피 검색 중 오류 발생: {e}")
            raise AppException("Recipe search error", status_code=500)

    def _preprocess_query(self, query: str) -> List[str]:
        """쿼리 전처리"""
        if "," not in query:
            return [query.strip()]
        return [ingredient.strip() for ingredient in query.split(",")]

    async def _search_recipes(self, query_embedding: List[float], query_ingredients: List[str], top_k: int) -> List[Dict]:
        """임베딩 벡터로 레시피 검색"""
        db = DatabaseConnection()
        logger.info(f"=== 검색 시작 ===")
        logger.info(f"검색할 재료: {query_ingredients}")
        logger.debug(f"임베딩 벡터 샘플: {query_embedding[:5]}...")

        try:
            results = db.query(
                vector=query_embedding,
                top_k=top_k
            )

            if not results["matches"]:
                logger.warning("검색 결과가 없습니다.")
                return []

            logger.info(f"총 매치 수: {len(results['matches'])}")
            return self._filter_and_format_results(results["matches"], query_ingredients)

        except Exception as e:
            logger.error(f"데이터베이스 검색 중 오류 발생: {e}")
            raise AppException("Database search error", status_code=503)
        finally:
            self._cleanup_db_connection(db)

    def _filter_and_format_results(self, matches: List[Dict], query_ingredients: List[str]) -> List[Dict]:
        """검색 결과 필터링 및 포맷팅"""
        filtered_results = []

        for match in sorted(matches, key=lambda x: x['score'], reverse=True):
            match_ingredients = match["metadata"].get("ingredients", [])
            
            # 쿼리 재료가 레시피의 재료 목록에 모두 포함되어 있는지 확인
            if self._check_ingredients_match(query_ingredients, match_ingredients):
                filtered_results.append(self._format_recipe(match))
                logger.debug(f"매칭된 레시피: {match['metadata'].get('title')} (점수: {match['score']})")

        logger.info(f"=== 최종 결과 ===")
        logger.info(f"필터링된 결과 수: {len(filtered_results)}")
        return filtered_results

    def _check_ingredients_match(self, query_ingredients: List[str], recipe_ingredients: List[str]) -> bool:
        """쿼리 재료가 레시피 재료에 포함되어 있는지 확인"""
        return all(
            any(query_ing.lower() in ingredient.lower() for ingredient in recipe_ingredients)
            for query_ing in query_ingredients
        )

    def _format_recipe(self, match: Dict) -> Dict:
        """레시피 정보 포맷팅"""
        return {
            "id": match['id'],
            "title": match["metadata"].get("title", ""),
            "ingredients": match["metadata"].get("raw_ingredients", []),
            "steps": match["metadata"].get("steps", []),
        }

    def _cleanup_db_connection(self, db: DatabaseConnection):
        """데이터베이스 연결 정리"""
        db._unload_connection()
        del db
        gc.collect()

# 전역 검색 서비스 인스턴스
search_service = RecipeSearchService()
