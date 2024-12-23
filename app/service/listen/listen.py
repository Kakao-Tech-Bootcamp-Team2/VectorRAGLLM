from typing import Dict, Optional
from app.core import setting
from app.core.logger import setup_logger
from app.core.exception import AppException
from app.service.search.search import search_service 
from app.service.llm import generate_response
from app.service.publish.publish import publisher

import aio_pika
import json

logger = setup_logger(__name__)

class MessageProcessor:
    @staticmethod
    async def process_message(body: bytes) -> Optional[Dict]:
        try:
            ingredients_data = json.loads(body.decode())
            query = ",".join(item["ingredients"] for item in ingredients_data)
            logger.info(f"검색할 재료: {query}")
    
            search_results = await search_service.search_recipes_by_text(query)
            if not search_results:
                logger.warning("검색 결과가 없습니다.")
                return None
            
            logger.debug(f"ingredients_data: {ingredients_data}")
            llm_response = generate_response(ingredients_data, search_results)
            logger.info(f"응답 생성 완료 (검색된 레시피: {len(search_results)}개)")
            
            await publisher.publish_message(llm_response)
            return llm_response
            
        except Exception as e:
            logger.error(f"메시지 처리 중 오류 발생: {e}")
            raise AppException("Message processing error", status_code=500)

class RabbitMQListener:
    def __init__(
            self, 
            host: str = setting.RABBITMQ_HOST, 
            queue: str = setting.RABBITMQ_QUEUE
        ):
        self.host = host
        self.queue = queue
        self.connection = None
        self.channel = None
        self._running = False

    async def setup(self):
        """RabbitMQ 연결 설정"""
        try:
            if not self._running:
                logger.info("RabbitMQ listener connection setting...")
                connection_url = f"amqp://{self.host}/"
                self.connection = await aio_pika.connect_robust(connection_url)
                self.channel = await self.connection.channel()
                await self.channel.declare_queue(
                    self.queue, 
                    durable=True,
                    arguments=setting.RABBITMQ_QUEUE_ARGUMENTS
                )
                await self.channel.set_qos(prefetch_count=1)
                
                self._running = True
                logger.info(f"'{self.queue}' 큐에서 메시지 대기 중...")
            
        except Exception as e:
            logger.error(f"RabbitMQ 연결 실패: {e}")
            raise AppException("RabbitMQ connection error",status_code=503)

    async def consume(self):
        """메시지 소비"""
        try:
            if not self._running:
                await self.setup()
                
            queue = await self.channel.declare_queue(self.queue, durable=True)
            async for message in queue:
                async with message.process():
                    await MessageProcessor.process_message(message.body)
                    
        except Exception as e:
            logger.error(f"메시지 소비 중 오류 발생: {e}")
            raise AppException("Message consumption error", status_code=500)
        finally:
            self._running = False

    async def cleanup(self):
        """리소스 정리"""
        if self.connection:
            await self.connection.close()
            self._running = False
            self.connection = None
            self.channel = None
            logger.info("RabbitMQ connection closed.")

# 전역 리스너 인스턴스
listener = RabbitMQListener()
