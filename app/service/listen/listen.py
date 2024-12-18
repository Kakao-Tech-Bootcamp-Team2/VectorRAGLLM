import aio_pika
import json
import asyncio
from typing import List, Dict, Optional
from app.service.search import search_recipes_by_text
from app.service.llm import generate_response

class MessageProcessor:
    @staticmethod
    async def process_message(body: bytes) -> Optional[Dict]:
        try:
            # 입력 데이터 처리
            ingredients_data = json.loads(body.decode())
            #ingredients_str = ", ".join(f'{item["ingredients"]}({item["quantities"]})' for item in ingredients_data)
            #print(ingredients_str)
            query = ",".join(item["ingredients"] for item in ingredients_data)
            print(f" [x] 검색할 재료: {query}")
    
            # 레시피 검색 및 LLM 처리
            search_results = search_recipes_by_text(query)
            if not search_results:
                print(" [x] 검색 결과가 없습니다.")
                return None
            
            llm_response = generate_response(ingredients_data, search_results)
            print(f" [x] 응답 생성 완료 (검색된 레시피: {len(search_results)}개)")
            return print(llm_response)
            
        except Exception as e:
            print(f" [x] 처리 중 오류 발생: {e}")
            return None

class RabbitMQListener:
    def __init__(self, host: str = 'localhost', queue: str = 'recommendation.queue'):
        self.host = host
        self.queue = queue
        self.connection = None
        self.channel = None
        self._running = False

    async def setup(self):
        """RabbitMQ 연결 설정"""
        if self._running:
            return
            
        try:
            self.connection = await aio_pika.connect_robust(f"amqp://{self.host}/")
            self.channel = await self.connection.channel()
            
            await self.channel.declare_queue(self.queue, durable=True)
            await self.channel.set_qos(prefetch_count=1)
            
            self._running = True
            print(f" [*] '{self.queue}' 큐에서 메시지 대기 중...")
            
        except Exception as e:
            print(f" [x] RabbitMQ 연결 실패: {e}")
            raise

    async def consume(self):
        """메시지 소비"""
        if not self._running:
            return
        try:
            queue = await self.channel.declare_queue(self.queue, durable=True)
            async for message in queue:
                async with message.process():
                    await MessageProcessor.process_message(message.body)
        except Exception as e:
            print(f" [x] 메시지 소비 중 오류 발생: {e}")
        finally:
            self._running = False

    async def cleanup(self):
        """리소스 정리"""
        if self.connection:
            await self.connection.close()
            self._running = False

# 전역 리스너 인스턴스
listener = RabbitMQListener()
