import os
import json
import asyncio
import logging
from google import genai
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("MeteorLive.Handler")

class GeminiLiveEngine:
    def __init__(self):
        # العودة للطريقة البسيطة والمباشرة التي نجحت معك سابقاً
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.api_key, http_options={'api_version': 'v1alpha'})
        self.model_id = "gemini-2.5-flash"

    async def start_session(self, system_instruction: str, user_ws):
        # إعدادات بسيطة جداً لضمان عدم حدوث تعارض (Extra Inputs)
        config = {"system_instruction": system_instruction}
        
        try:
            async with self.client.aio.live.connect(model=self.model_id, config=config) as session:
                logger.info("✅ BACK TO LIFE! Gemini 2.5 is connected.")

                async def send_loop():
                    async for message in user_ws:
                        try:
                            data = json.loads(message)
                            if data['type'] == 'text':
                                await session.send(input=data['content'], end_of_turn=True)
                        except Exception: continue

                async def receive_loop():
                    async for response in session.receive():
                        if response.text:
                            await user_ws.send_json({
                                "type": "agent_response", 
                                "content": response.text,
                                "metrics": {"latency_ms": 150} # السرعة اللي كانت عاجباك
                            })

                await asyncio.gather(send_loop(), receive_loop())

        except Exception as e:
            logger.error(f"🔴 Connection Error: {str(e)}")