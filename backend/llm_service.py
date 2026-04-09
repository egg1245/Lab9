"""LLM Service - Qwen CLI Integration"""
import logging
import asyncio
import json
import re
from typing import List

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.timeout = 60
        logger.info("✅ LLMService initialized: Real Qwen CLI")

    async def generate(self, ingredients: List[str], appliances: List[str]) -> dict:
        try:
            ing_str = ", ".join(ingredients)
            app_str = ", ".join(appliances) if isinstance(appliances, list) else appliances
            
            prompt = f'You are a dorm cooking expert. Generate JSON recipe using: {ing_str} and {app_str}. Return ONLY: {{"title":"Recipe","description":"Dish","servings":2,"time_minutes":30,"difficulty":"easy","steps":[{{"step_number":1,"instruction":"Cook","duration_minutes":30}}],"notes":"Enjoy"}}'
            
            logger.info(f"🍳 Calling Qwen: {ing_str}")
            process = await asyncio.create_subprocess_shell(
                f'/usr/bin/qwen --output-format json "{prompt}"',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=self.timeout)
            
            if process.returncode != 0:
                logger.error(f"Qwen error: {stderr.decode()}")
                raise Exception("Qwen failed")
            
            output = stdout.decode('utf-8', errors='ignore')
            logger.info(f"Output: {output[:80]}")
            
            recipe = json.loads(output)
            recipe.setdefault('title', f"Creative {ing_str}")
            recipe.setdefault('description', f"Dorm meal")
            recipe.setdefault('servings', 2)
            recipe.setdefault('time_minutes', 30)
            recipe.setdefault('difficulty', 'easy')
            recipe.setdefault('steps', [])
            recipe.setdefault('notes', 'Enjoy!')
            
            logger.info(f"✅ Recipe: {recipe['title']}")
            return recipe
        except Exception as e:
            logger.error(f"LLM error: {e}")
            raise
