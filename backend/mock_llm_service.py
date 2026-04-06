import logging
from typing import List

logger = logging.getLogger(__name__)


class MockLLMService:
    """Mock LLM service for testing without API"""

    async def generate(self, ingredients: List[str], appliances: List[str]) -> dict:
        """
        Generate a mock recipe
        
        Args:
            ingredients: List of available ingredients
            appliances: List of kitchen appliances to use
            
        Returns:
            dict: Mock recipe content
        """
        # Create a simple mock recipe based on ingredients and appliances
        ingredient_str = ', '.join(ingredients[:3])  # Use first 3 ingredients
        appliance_str = appliances[0] if appliances else "Microwave"  # Use first appliance
        
        mock_recipe = {
            "title": f"Simple {ingredient_str} Recipe",
            "description": f"A delicious and easy-to-make dish using {ingredient_str} with a {appliance_str}",
            "steps": [
                {
                    "step_number": 1,
                    "instruction": f"Prepare your ingredients: {ingredient_str}",
                    "duration_minutes": 5
                },
                {
                    "step_number": 2,
                    "instruction": f"Use your {appliance_str} to heat/cook the ingredients",
                    "duration_minutes": 10
                },
                {
                    "step_number": 3,
                    "instruction": "Check for doneness and adjust heat if needed",
                    "duration_minutes": 5
                },
                {
                    "step_number": 4,
                    "instruction": "Serve hot and enjoy!",
                    "duration_minutes": 2
                }
            ],
            "time_minutes": 22,
            "difficulty": "easy",
            "servings": 2,
            "appliances_used": appliances,
            "notes": "This is a mock recipe for testing. For real recipes, please ensure a working API connection."
        }
        
        logger.info(f"Mock recipe generated: {mock_recipe.get('title', 'Unknown')}")
        return mock_recipe
