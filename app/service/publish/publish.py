import aio_pika
import json
from typing import Any

class RabbitMQPublisher:
    def __init__(self, host: str = 'localhost', exchange: str = '', routing_key: str = 'response.queue'):
        self.host = host
        self.exchange = exchange
        self.routing_key = routing_key
        self.connection = None
        self.channel = None

    async def setup(self):
        """RabbitMQ 연결 설정"""
        if not self.connection:
            self.connection = await aio_pika.connect_robust(f"amqp://{self.host}/")
            self.channel = await self.connection.channel()
            await self.channel.declare_queue(self.routing_key, durable=True)

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
            print(f" [x] 응답 발행 완료: {self.routing_key}")

        except Exception as e:
            print(f" [x] 메시지 발행 중 오류 발생: {e}")

    async def cleanup(self):
        """리소스 정리"""
        if self.connection:
            await self.connection.close()
            self.connection = None
            self.channel = None

# 전역 발행자 인스턴스
publisher = RabbitMQPublisher()
