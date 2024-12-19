from typing import List, Optional, Dict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from app.core import setting
from .models import RecipeResponse
from .prompts import prompt

class RecipeGenerator:    
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        temperature: float = 0.3,
        max_tokens: int = 5000,
    ):
        if not (api_key := setting.OPENAI_API_KEY):
            raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
            
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=api_key
        ).with_structured_output(RecipeResponse)

    def format_ingredients(self, ingredients: List[Dict[str, str]]) -> str:
        return "\n".join(
            f"{item['ingredients']}: {item['quantities']}" 
            for item in ingredients
        )
    def generate_recipes(
        self, 
        user_ingredients: List[Dict[str, str]], 
        search_response: str
    ) -> Optional[RecipeResponse]:
        #레시피 추천 응답을 생성하는 함수
        try:
            formatted_messages = prompt.format_messages(
                ingredients=self.format_ingredients(user_ingredients),
                documents=search_response
            )
            return self.llm.invoke(formatted_messages)
        except Exception as e:
            print(f"레시피 생성 중 오류 발생: {e}")
            return None

# 전역 인스턴스 생성
recipe_generator = RecipeGenerator()

def generate_response(user_ingredients: List[Dict[str, str]], search_response: str) -> Optional[Dict]:
    #레시피 추천 응답을 생성하는 함수
    response = recipe_generator.generate_recipes(user_ingredients, search_response)
    return response.model_dump(by_alias=True) if response else None