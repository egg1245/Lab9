import os
import json
import logging
from typing import List
from openai import AsyncOpenAI
import asyncio

logger = logging.getLogger(__name__)

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")

SYSTEM_PROMPT = """You are an expert dorm cooking advisor. Your task is to generate detailed, step-by-step recipes using ONLY the provided ingredients and the specified kitchen appliances.

CRITICAL REQUIREMENTS:
1. Use ONLY the provided ingredients - NO substitutions or additional items
2. Use ONLY the specified appliances - NO other tools or equipment
3. Recipes must be realistic and safe for a student dorm environment
4. Provide clear, actionable instructions that a beginner can follow
5. Include realistic time estimates for each step
6. Suggest variations or tips when applicable

RESPONSE FORMAT - Return ONLY valid JSON (no extra text):
{
  "title": "Descriptive recipe name",
  "description": "1-2 sentence summary of the dish",
  "steps": [
    {
      "step_number": 1,
      "instruction": "Detailed, clear instruction for this step",
      "duration_minutes": 5
    },
    {
      "step_number": 2,
      "instruction": "Next instruction...",
      "duration_minutes": 10
    }
  ],
  "time_minutes": 25,
  "difficulty": "easy",
  "servings": 2,
  "appliances_used": ["Microwave"],
  "notes": "Safety tips, storage suggestions, or helpful variations"
}

IMPORTANT: Respond ONLY with valid JSON, no other text or explanations."""


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

    async def generate(self, ingredients: List[str], appliances: List[str]) -> dict:
        """
        Generate a recipe using LLM
        
        Args:
            ingredients: List of available ingredients
            appliances: List of kitchen appliances to use
            
        Returns:
            dict: Parsed recipe content
        """
        appliances_str = ', '.join(appliances)
        user_prompt = f"""Generate a recipe using ONLY these ingredients:
{', '.join(ingredients)}

Kitchen appliances available (you can use one or more):
{appliances_str}

CONSTRAINTS:
- Do NOT use any ingredients not listed above
- Do NOT use any appliances other than those listed above
- Make it doable in a student dorm
- Provide realistic timing for each step
- Be specific and actionable in your instructions"""

        try:
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=LLM_MODEL,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.7,
                    max_tokens=2000,
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
            logger.error(f"LLM error: {type(e).__name__}: {e}")
            # Fallback to mock for network/connection errors
            logger.info("Falling back to mock service...")
            from .mock_llm_service import MockLLMService
            mock = MockLLMService()
            return await mock.generate(ingredients, appliances)
