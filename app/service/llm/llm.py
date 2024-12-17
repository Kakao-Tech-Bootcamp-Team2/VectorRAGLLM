import json
from app.core import setting
from langchain_openai import ChatOpenAI

def generate_response(user_query, search_response, model="gpt-4o-mini", temperature=0.3, max_tokens=3000, timeout=30, max_retries=3):
    api_key = setting.OPENAI_API_KEY
    if not api_key:
        raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
    
    llm = ChatOpenAI(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout,
        max_retries=max_retries,
        api_key=api_key
    )
    
    prompt = f"""
    사용자가 소지한 재료: {user_query}
    관련 문서:
    {search_response}
    위의 사용자가 소지한 재료와 관련 문서를 참고하여 **레시피를 1개에서 5개 추천해주세요**.
    요구사항:
    - 위 사용자가 소지한 재료와 관련 문서를 기반으로 서로 다른 유형의 레시피를 1개에서 5개 추천해주세요.
    - 비슷한 스타일의 레시피(예: 모두 돼지고기 수육류)를 반복하지 말고 다양하게 구성해주세요.
    - 추가적인 재료는 최소화해주세요.
    - 각 레시피의 '재료' 목록에는 반드시 '재료명'과 '양'을 포함해주세요.
    - 조리 방법은 단계별로 다음 사항을 포함해주세요:
        - 사용된 재료와 양, 단위를 명확히 언급 (예: "돼지고기 100g을 넣고...")
        - 조리 온도나 불 세기 (예: "중불에서", "약불에서")
        - 대략적인 조리 시간 (예: "약 1분간 볶아주세요.")
        - 질감, 색 변화 등의 상태 묘사 (예: "양파가 투명해질 때까지", "고기가 갈색빛이 돌 때까지")
        - 가능한 한 자세히 단계별로 나누어 설명 (예: "1분간 볶은 뒤 간장 1큰술을 넣고 다시 30초간 볶아주세요.")
    - 최종 답변은 다음의 JSON 형식을 엄격하게 준수해주세요(코드 블록 없이):

    {{
      "레시피 목록": [
        {{
          "레시피 id": "관련 문서의 recipe_id",
          "레시피 이름": "레시피 이름",
          "재료": [
            {{"재료명": "재료1", "양": "양1"}},
            {{"재료명": "재료2", "양": "양2"}}
          ],
          "조리 방법": ["조리 단계1", "조리 단계2", ...]
        }},
        ...
      ]
    }}
    """

    # 모델 호출 및 응답 생성
    response = llm.invoke([{"role": "user", "content": prompt}])
    assistant_content = response.content

    # JSON 내용 파싱
    try:
        recipe = json.loads(assistant_content)
    except json.JSONDecodeError as e:
        print("JSON 파싱 실패:", e)
        recipe = None

    return recipe