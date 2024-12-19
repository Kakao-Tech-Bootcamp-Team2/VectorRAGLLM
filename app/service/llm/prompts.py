from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

SYSTEM_TEMPLATE = """당신은 주어진 재료로 만들 수 있는 레시피를 추천하는 요리 전문가입니다.
다음 요구사항에 맞춰 레시피를 추천해주세요:
- 서로 다른 유형의 레시피를 1개에서 5개 추천
- 비슷한 스타일의 레시피 반복 금지
- 추가 재료 최소화
- 각 레시피는 정확한 재료명과 양을 포함
- 조리 방법은 단계별로 다음 사항을 포함:
    - 사용된 재료와 양, 단위를 명확히 언급
    - 조리 온도나 불 세기
    - 대략적인 조리 시간
    - 질감, 색 변화 등의 상태 묘사
    - 가능한 한 자세히 단계별로 설명"""

HUMAN_TEMPLATE = """사용자가 소지한 재료:
{ingredients}

관련 문서:
{documents}"""

prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(SYSTEM_TEMPLATE),
    HumanMessagePromptTemplate.from_template(HUMAN_TEMPLATE)
])