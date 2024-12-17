# VectorRAGLLM

레시피 추천 시스템 - 벡터 데이터베이스와 LLM을 활용한 RAG(Retrieval-Augmented Generation) 기반 레시피 추천 서비스

## 시스템 구조

- FastAPI 기반의 웹 서버
- Pinecone 벡터 데이터베이스를 활용한 레시피 검색
- HuggingFace 임베딩 모델(multilingual-e5-large-instruct)을 사용한 텍스트 임베딩
- OpenAI GPT 모델을 활용한 레시피 생성

## 주요 기능

1. **재료 기반 레시피 검색** (`/recipes/search`)
   - 사용자가 입력한 재료를 기반으로 유사한 레시피 검색
   - 벡터 유사도 기반 검색 구현

2. **맞춤형 레시피 생성** (`/recipes/llm`)
   - 검색된 레시피를 기반으로 LLM이 상황에 맞는 새로운 레시피 생성
   - 상세한 조리 방법과 재료 정보 제공
- 추후 RabbitMQ를 활용한 비동기 처리 구현

## 설치 및 실행

### 환경 설정

1. 필요한 환경 변수 설정 (.env 파일)
```
RECIPE_DB_API_KEY=your_recipe_db_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_HOST_URL=your_pinecone_host_url
OPENAI_API_KEY=your_openai_api_key
```

### 실행 방법

1. 의존성 설치
```bash
pip install -r requirements.txt
```

2. 서버 실행
```bash
uvicorn app.main:app --reload
```

## 시스템 특징

- **메모리 최적화**: 임베딩 모델과 데이터베이스 연결의 효율적인 관리
- **싱글톤 패턴**: 리소스 효율적 사용을 위한 서비스 인스턴스 관리
- **비동기 처리**: FastAPI의 비동기 처리를 통한 효율적인 요청 처리
- **자동 리소스 정리**: 사용이 끝난 모델과 연결의 자동 해제

## API 엔드포인트

### GET /recipes/search
- 재료 기반 레시피 검색
- Query Parameter: `query` (검색할 재료 목록, 쉼표로 구분)

### GET /recipes/llm
- LLM 기반 맞춤형 레시피 생성
- Query Parameter: `query` (사용 가능한 재료 목록)

## 기술 스택

- FastAPI
- Pinecone
- LangChain
- HuggingFace Transformers
- OpenAI GPT
```
