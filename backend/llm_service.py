import os
import json
import logging
from typing import List
from openai import AsyncOpenAI
import asyncio

logger = logging.getLogger(__name__)

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
LLM_MODEL = os.getenv("LLM_MODEL", "openrouter/qwen/qwen-2.5-72b-instruct")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")

SYSTEM_PROMPT = """You are a dorm cooking expert. Your task is to generate a detailed, step-by-step recipe using ONLY the provided ingredients and ONE specific kitchen appliance.

The recipe must:
1. Use ONLY the provided ingredients (no substitutions or additional items)
2. Use ONLY the specified appliance (no other tools)
3. Be realistic for a student to prepare in a dorm
4. Be detailed and actionable

Format your response as valid JSON with this exact structure:
{
  "title": "Recipe name",
  "description": "Brief description of what you're making",
  "steps": [
    {
      "step_number": 1,
      "instruction": "Detailed step instruction",
      "duration_minutes": 5
    }
  ],
  "time_minutes": 20,
  "difficulty": "easy",
  "servings": 2,
  "notes": "Optional cooking tips"
}

Respond ONLY with valid JSON, no additional text."""


class LLMService:
    """Service for LLM integration"""

    def __init__(self, provider: str = LLM_PROVIDER):
        self.provider = provider
        if provider == "openai":
            self.client = AsyncOpenAI(
                api_key=OPENAI_API_KEY,
                base_url=OPENAI_API_BASE
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    async def generate(self, ingredients: List[str], appliance: str) -> dict:
        """
        Generate a recipe using LLM
        
        Args:
            ingredients: List of available ingredients
            appliance: Kitchen appliance to use
            
        Returns:
            dict: Parsed recipe content
        """
        user_prompt = f"""Generate a recipe using these ingredients: {', '.join(ingredients)}

Kitchen appliance available: {appliance}

Remember: Use ONLY these ingredients and ONLY this appliance."""

        try:
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=LLM_MODEL,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.7,
                    max_tokens=1500,
                ),
                timeout=30.0,
            )

            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            recipe = json.loads(content)
            logger.info(f"Recipe generated: {recipe.get('title', 'Unknown')}")
            return recipe

        except asyncio.TimeoutError:
            logger.error("LLM call timed out")
            raise ValueError("Recipe generation timed out. Please try again.")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from LLM: {e}")
            raise ValueError("Invalid recipe format returned from LLM")
        except Exception as e:
            logger.error(f"LLM error: {e}")
            raise ValueError(f"Recipe generation failed: {str(e)}")
