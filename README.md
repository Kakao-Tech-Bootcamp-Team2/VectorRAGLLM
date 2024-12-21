# VectorRAGLLM

레시피 추천 시스템 - 벡터 데이터베이스와 LLM을 활용한 RAG(Retrieval-Augmented Generation) 기반 레시피 추천 서비스

## 시스템 구조

- FastAPI 기반의 웹 서버
- RabbitMQ를 활용한 비동기 메시지 큐 시스템
- Pinecone 벡터 데이터베이스를 활용한 레시피 검색
- HuggingFace 임베딩 모델(multilingual-e5-large-instruct)을 사용한 텍스트 임베딩
- OpenAI GPT 모델을 활용한 레시피 생성

## 주요 기능

1. **비동기 메시지 처리**
   - RabbitMQ를 통한 메시지 큐 시스템
   - Publisher/Subscriber 패턴으로 구현된 비동기 처리
   - 응답 큐를 통한 결과 전달

2. **재료 기반 레시피 검색**
   - 벡터 유사도 기반 검색 구현
   - 재료명 전처리 및 정규화
   - 효율적인 메모리 관리를 위한 동적 모델 로딩/언로딩

3. **맞춤형 레시피 생성**
   - 검색된 레시피를 기반으로 LLM이 상황에 맞는 새로운 레시피 생성
   - 구조화된 응답 포맷 (Pydantic 모델 활용)
   - 상세한 조리 방법과 재료 정보 제공

## 시스템 특징

- **메모리 최적화**
  - 임베딩 모델과 데이터베이스 연결의 효율적인 관리
  - 자동 리소스 정리 시스템
  - GC를 통한 메모리 관리

- **견고한 에러 처리**
  - 커스텀 예외 클래스를 통한 체계적인 에러 관리
  - 상세한 로깅 시스템
  - 우아한 종료 처리

- **싱글톤 패턴**
  - 리소스 효율적 사용을 위한 서비스 인스턴스 관리
  - 스레드 세이프한 구현

## 설치 및 실행

### 환경 설정

1. 필요한 환경 변수 설정 (.env 파일)
```
RECIPE_DB_API_KEY=your_recipe_db_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_HOST_URL=your_pinecone_host_url
OPENAI_API_KEY=your_openai_api_key
RABBITMQ_HOST=your_rabbitmq_host
```

### 실행 방법

1. 의존성 설치
```bash
pip install -r requirements.txt
```

2. RabbitMQ 서버 실행
```bash
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:management
```

3. 서버 실행
```bash
uvicorn app.main:app --reload
```

## 기술 스택

- FastAPI
- RabbitMQ
- Pinecone
- LangChain
- HuggingFace Transformers
- OpenAI GPT
- Pydantic

## 로깅 시스템

- 상세한 로그 레벨 관리
- 구조화된 로그 포맷
- 각 서비스 별 독립적인 로거

## 프로젝트 구조

```
app/
├── core/           # 핵심 설정 및 유틸리티
├── repositorie/    # 데이터베이스 관련 코드
├── service/        # 비즈니스 로직
│   ├── listen/     # RabbitMQ 리스너
│   ├── publish/    # RabbitMQ 퍼블리셔
│   ├── search/     # 검색 서비스
│   ├── llm/        # LLM 관련 서비스
│   └── preprocess/ # 데이터 전처리
└── main.py         # 애플리케이션 엔트리포인트
```
