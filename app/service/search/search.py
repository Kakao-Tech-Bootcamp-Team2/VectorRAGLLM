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

    async def search_recipes_by_text(self, query: str, top_k: int = 100) -> List[Dict]:
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

        try:
            # 먼저 500개 검색
            results = db.query(
                vector=query_embedding,
                top_k=500  # 더 많은 결과를 가져옵니다
            )

            if not results["matches"]:
                logger.warning("검색 결과가 없습니다.")
                return []

            logger.info(f"총 매치 수: {len(results['matches'])}")
            # 상위 100개만 포맷팅하여 반환
            return self._format_results(results["matches"], limit=100)

        except Exception as e:
            logger.error(f"데이터베이스 검색 중 오류 발생: {e}")
            raise AppException("Database search error", status_code=503)
        finally:
            self._cleanup_db_connection(db)

    def _format_results(self, matches: List[Dict], limit: int = 100) -> List[Dict]:
        """검색 결과 포맷팅"""
        formatted_results = []
        
        # 유사도 점수(score)를 기준으로 정렬하고 상위 limit개만 처리
        for match in sorted(matches, key=lambda x: x['score'], reverse=True)[:limit]:
            formatted_results.append({
                "id": match['id'],
                "title": match["metadata"].get("title", ""),
                "ingredients": match["metadata"].get("raw_ingredients", []),
                "steps": match["metadata"].get("steps", []),
            })
            logger.debug(f"매칭된 레시피: {match['metadata'].get('title')} (점수: {match['score']})")

        logger.info(f"=== 최종 결과 ===")
        logger.info(f"검색 결과 수: {len(formatted_results)}")
        return formatted_results

    def _cleanup_db_connection(self, db: DatabaseConnection):
        """데이터베이스 연결 정리"""
        db._unload_connection()
        del db
        gc.collect()

# 전역 검색 서비스 인스턴스
search_service = RecipeSearchService()
