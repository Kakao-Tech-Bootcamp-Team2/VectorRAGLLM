from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.route.route import router
from app.service.listen.listen import listener
import asyncio
import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"

_listener_task = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _listener_task
    
    try:
        # 리스너 설정
        await listener.setup()
        
        # 백그라운드 태스크로 리스너 실행
        if _listener_task is None:
            _listener_task = asyncio.create_task(listener.consume())
            
        yield
        
    finally:
        # 종료 시 리소스 정리
        if _listener_task:
            await listener.cleanup()
            _listener_task.cancel()
            try:
                await _listener_task
            except asyncio.CancelledError:
                pass

app = FastAPI(lifespan=lifespan)
app.include_router(router)