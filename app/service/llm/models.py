
from typing import List
from pydantic import BaseModel, Field

class Ingredient(BaseModel):
    """레시피 재료 모델"""
    name: str = Field(..., alias="재료명")
    amount: str = Field(..., alias="양")

class Recipe(BaseModel):
    """레시피 모델"""
    recipe_id: str = Field(..., alias="레시피 id")
    name: str = Field(..., alias="레시피 이름")
    ingredients: List[Ingredient] = Field(..., alias="재료")
    steps: List[str] = Field(..., alias="조리 방법")

class RecipeResponse(BaseModel):
    """전체 레시피 응답 모델"""
    recipes: List[Recipe] = Field(..., alias="레시피 목록")

class UserIngredient(BaseModel):
    """사용자 입력 재료 모델"""
    ingredients: str
    quantities: str