from confluent_kafka import Producer as ConfluentProducer
from loguru import logger
import asyncio
import json

class Producer:
    def __init__(self, bootstrap_servers: list) -> None:
        conf = {'bootstrap.servers': ','.join(bootstrap_servers)}
        self.producer = ConfluentProducer(conf)
    
    async def send(self, topic, data: dict):
        try:
            logger.debug(f"trying to send to kafka topic: {topic}")
            
            await asyncio.to_thread(self.producer.produce, topic, json.dumps(data).encode('utf-8'))
            await asyncio.to_thread(self.producer.flush)
            
            logger.info(f"Terkirim ke kafka")
        except Exception as e:
            logger.error(f"Error when trying to send to kafka: {e}")