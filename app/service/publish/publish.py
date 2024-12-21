from typing import Any
from app.core import setting
from app.core.logger import setup_logger
from app.core.exception import AppException

import aio_pika
import json

logger = setup_logger(__name__)


class RabbitMQPublisher:
    def __init__(
            self, host: str = setting.RABBITMQ_HOST, exchange: str = '', 
            routing_key: str = setting.RABBITMQ_RESPONSE_QUEUE
            ):
        self.host = host
        self.exchange = exchange
        self.routing_key = routing_key
        self.connection = None
        self.channel = None

    async def setup(self):
        """RabbitMQ 연결 설정"""
        try :
            if not self.connection:
                logger.info("RabbitMQ connection setting...")
                self.connection = await aio_pika.connect_robust(f"amqp://{self.host}/")
                self.channel = await self.connection.channel()
                await self.channel.declare_queue(self.routing_key, durable=True)
                logger.info("RabbitMQ connection setting complete.")
        except Exception as e:
            logger.error(f"RabbitMQ connection setting error: {e}")
            raise AppException("RabbitMQ connection setting error",status_code=503)

    async def publish_message(self, message: Any):
        """메시지 발행"""
        try:
            if not self.channel:
                await self.setup()

            # 메시지를 JSON 문자열로 변환 (한글 유지)
            message_str = json.dumps(message, ensure_ascii=False)
            
            # UTF-8로 인코딩
            message_body = message_str.encode('utf-8')
            
            await self.channel.default_exchange.publish(
                aio_pika.Message(
                    body=message_body,
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                    content_type='application/json',
                    content_encoding='utf-8'
                ),
                routing_key=self.routing_key
            )
            logger.info(f"RabbitMQ published successfully")
        except Exception as e:
            logger.error(f"RabbitMQ message publish error: {e}")
            raise AppException("RabbitMQ message publish error",status_code=500)

    async def cleanup(self):
        """리소스 정리"""
        if self.connection:
            await self.connection.close()
            self.connection = None
            self.channel = None
            logger.info("RabbitMQ connection closed.")

# 전역 발행자 인스턴스
publisher = RabbitMQPublisher()
