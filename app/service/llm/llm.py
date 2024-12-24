from typing import List, Optional, Dict
from langchain_openai import ChatOpenAI
from app.core import setting
from app.core.exception import AppException
from app.core.logger import setup_logger
from app.service.llm.models import RecipeResponse
from app.service.llm.prompts import prompt

logger = setup_logger(__name__)

class RecipeGenerator: 
    """레시피 생성을 위한 LLM 기반 생성기 클래스""" 
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        temperature: float = 0.3,
        max_tokens: int = 5000,
    ):
        try :
            if not (api_key := setting.OPENAI_API_KEY):
                raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")

            # LLM 모델 설정
            self.llm = ChatOpenAI(
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=api_key
            ).with_structured_output(RecipeResponse)

            logger.info("LLM Generate Initialized.")  # 초기화 완료 로그
        except Exception as e:
            logger.error("LLM generate Error: %s", str(e))
            raise AppException("LLM Generate Error", status_code=503) from e
                
    def format_ingredients(
        self, 
        ingredients: List[Dict[str, str]]
    ) -> str:
        """재료 목록을 문자열로 포맷팅하는 함수"""
        return "\n".join(
            f"{item['ingredients']}: {item['quantities']}" 
            for item in ingredients
        )
    def generate_recipes(
        self, 
        user_ingredients: List[Dict[str, str]], 
        search_response: str
    ) -> Optional[RecipeResponse]:
        """레시피 추천 응답을 생성하는 함수"""
        try:
            logger.info("Recipe Generation Start.")
            # 메시지 포맷팅 및 LLM 호출
            return self.llm.invoke(
                prompt.format_messages(
                    ingredients=self.format_ingredients(user_ingredients),
                    documents=search_response
                )
            )
        except Exception as e:
            logger.error("LLM generate Error: %s", str(e))
            raise AppException("LLM Generate Error", status_code=503) from e
        
# 전역 인스턴스 생성
recipe_generator = RecipeGenerator()

def generate_response(user_ingredients: List[Dict[str, str]], search_response: str) -> Optional[Dict]:
    """레시피 추천 응답을 생성하는 함수"""
    try:
        response = recipe_generator.generate_recipes(user_ingredients, search_response)
        return response.model_dump(by_alias=True) if response else None
    except Exception as e:
        logger.error("LLM generate Error: %s", str(e))
        raise AppException("LLM Generate Error", status_code=503) from e
