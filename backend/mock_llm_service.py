import logging
from typing import List

logger = logging.getLogger(__name__)


class MockLLMService:
    """Professional mock LLM service with real recipe database"""

    # Real recipes database based on common dorm ingredients
    RECIPE_DATABASE = {
        # Simple recipes
        "eggs_toast": {
            "title": "Buttered Toast with Scrambled Eggs",
            "description": "Classic breakfast dish with fluffy scrambled eggs and crispy toasted bread",
            "steps": [
                {
                    "step_number": 1,
                    "instruction": "Toast the bread until golden brown",
                    "duration_minutes": 3
                },
                {
                    "step_number": 2,
                    "instruction": "Beat eggs with a pinch of salt and pepper",
                    "duration_minutes": 2
                },
                {
                    "step_number": 3,
                    "instruction": "Melt butter in a pan over medium heat",
                    "duration_minutes": 2
                },
                {
                    "step_number": 4,
                    "instruction": "Pour beaten eggs and stir gently until cooked (3-5 minutes)",
                    "duration_minutes": 4
                },
                {
                    "step_number": 5,
                    "instruction": "Spread eggs on toast and serve immediately",
                    "duration_minutes": 1
                }
            ],
            "time_minutes": 12,
            "difficulty": "easy",
            "servings": 2,
            "notes": "Add cheese or herbs for extra flavor. Keep heat medium to avoid scrambling too fast."
        },
        "pasta_simple": {
            "title": "Easy Pasta with Butter and Cheese",
            "description": "Classic Italian-style pasta dish with creamy butter and melted cheese sauce",
            "steps": [
                {
                    "step_number": 1,
                    "instruction": "Boil water in a pot and add salt",
                    "duration_minutes": 5
                },
                {
                    "step_number": 2,
                    "instruction": "Add pasta and cook until al dente (8-10 minutes)",
                    "duration_minutes": 9
                },
                {
                    "step_number": 3,
                    "instruction": "Drain pasta, reserving 1 cup of pasta water",
                    "duration_minutes": 2
                },
                {
                    "step_number": 4,
                    "instruction": "Mix butter and cheese with pasta, add pasta water as needed",
                    "duration_minutes": 2
                },
                {
                    "step_number": 5,
                    "instruction": "Stir well until creamy and serve hot",
                    "duration_minutes": 1
                }
            ],
            "time_minutes": 19,
            "difficulty": "easy",
            "servings": 2,
            "notes": "Use high quality butter and cheese for better taste. Don't overcook pasta!"
        },
        "rice_simple": {
            "title": "Microwave Rice with Butter",
            "description": "Quick and fluffy microwaved rice perfect for any meal",
            "steps": [
                {
                    "step_number": 1,
                    "instruction": "Measure 1 cup rice and rinse under cold water",
                    "duration_minutes": 2
                },
                {
                    "step_number": 2,
                    "instruction": "Add 2 cups water and a pinch of salt to microwave-safe bowl",
                    "duration_minutes": 1
                },
                {
                    "step_number": 3,
                    "instruction": "Cover with microwave-safe lid and cook on high for 10 minutes",
                    "duration_minutes": 10
                },
                {
                    "step_number": 4,
                    "instruction": "Let stand covered for 5 minutes",
                    "duration_minutes": 5
                },
                {
                    "step_number": 5,
                    "instruction": "Fluff with fork and add butter, then serve",
                    "duration_minutes": 1
                }
            ],
            "time_minutes": 19,
            "difficulty": "easy",
            "servings": 3,
            "notes": "Great base for adding vegetables, proteins, or sauces. Don't skip the standing time!"
        },
        "bread_cheese": {
            "title": "Cheese Toast in Air Fryer",
            "description": "Crispy melted cheese on toasted bread, ready in minutes",
            "steps": [
                {
                    "step_number": 1,
                    "instruction": "Slice bread and place in air fryer basket",
                    "duration_minutes": 2
                },
                {
                    "step_number": 2,
                    "instruction": "Air fry at 375°F for 3 minutes until edges start toasting",
                    "duration_minutes": 3
                },
                {
                    "step_number": 3,
                    "instruction": "Add cheese slices on top",
                    "duration_minutes": 1
                },
                {
                    "step_number": 4,
                    "instruction": "Air fry for another 2-3 minutes until cheese melts",
                    "duration_minutes": 3
                },
                {
                    "step_number": 5,
                    "instruction": "Remove carefully and let cool 1 minute before serving",
                    "duration_minutes": 1
                }
            ],
            "time_minutes": 10,
            "difficulty": "easy",
            "servings": 2,
            "notes": "Use good quality cheese for better melting. Watch carefully to prevent burning!"
        },
        "omelette": {
            "title": "Simple Omelette",
            "description": "Fluffy omelette filled with cheese and herbs",
            "steps": [
                {
                    "step_number": 1,
                    "instruction": "Beat 3 eggs with salt, pepper, and a splash of milk",
                    "duration_minutes": 2
                },
                {
                    "step_number": 2,
                    "instruction": "Heat butter in a non-stick pan over medium-high heat",
                    "duration_minutes": 2
                },
                {
                    "step_number": 3,
                    "instruction": "Pour eggs and let cook undisturbed for 30 seconds",
                    "duration_minutes": 1
                },
                {
                    "step_number": 4,
                    "instruction": "Gently push cooked portions to center, tilt pan to uncooked eggs",
                    "duration_minutes": 2
                },
                {
                    "step_number": 5,
                    "instruction": "Add cheese and fold in half when mostly set",
                    "duration_minutes": 1
                },
                {
                    "step_number": 6,
                    "instruction": "Slide onto plate and serve immediately",
                    "duration_minutes": 1
                }
            ],
            "time_minutes": 9,
            "difficulty": "medium",
            "servings": 1,
            "notes": "Don't overcook - omelettes should still be slightly wet when folded. Practice makes perfect!"
        }
    }

    async def generate(self, ingredients: List[str], appliances: List[str]) -> dict:
        """
        Generate a recipe matching available ingredients and appliances
        
        Args:
            ingredients: List of available ingredients
            appliances: List of kitchen appliances to use
            
        Returns:
            dict: Real recipe content
        """
        ingredients_lower = [i.lower() for i in ingredients]
        appliances_lower = [a.lower() for a in appliances]

        # Match recipe to ingredients and appliances
        recipe_key = self._find_best_recipe(ingredients_lower, appliances_lower)
        
        if recipe_key:
            recipe = self.RECIPE_DATABASE[recipe_key].copy()
            recipe["appliances_used"] = appliances
            logger.info(f"Generated recipe: {recipe.get('title', 'Unknown')}")
            return recipe
        
        # Fallback: create generic recipe
        return self._create_fallback_recipe(ingredients, appliances)

    def _find_best_recipe(self, ingredients: List[str], appliances: List[str]) -> str:
        """Find best matching recipe based on ingredients and appliances"""
        
        # Recipe requirements mapping
        recipe_requirements = {
            "eggs_toast": {
                "ingredients": {"eggs", "bread", "butter"},
                "appliances": {"toaster", "hot plate"},
                "score_boost": 2
            },
            "pasta_simple": {
                "ingredients": {"pasta", "butter", "cheese"},
                "appliances": {"hot plate", "oven"},
                "score_boost": 2
            },
            "rice_simple": {
                "ingredients": {"rice"},
                "appliances": {"microwave"},
                "score_boost": 3
            },
            "bread_cheese": {
                "ingredients": {"bread", "cheese"},
                "appliances": {"air fryer"},
                "score_boost": 3
            },
            "omelette": {
                "ingredients": {"eggs", "butter", "cheese"},
                "appliances": {"hot plate"},
                "score_boost": 2
            }
        }

        best_recipe = None
        best_score = 0

        for recipe_key, req in recipe_requirements.items():
            # Check ingredient match
            ingredient_matches = sum(
                1 for req_ing in req["ingredients"] 
                if any(req_ing in ing for ing in ingredients)
            )
            
            if ingredient_matches == 0:
                continue

            # Check appliance match
            appliance_matches = sum(
                1 for req_app in req["appliances"]
                if any(req_app in app for app in appliances)
            )

            if appliance_matches == 0:
                continue

            # Calculate score
            score = (ingredient_matches * 2) + (appliance_matches * req["score_boost"])
            
            if score > best_score:
                best_score = score
                best_recipe = recipe_key

        return best_recipe

    def _create_fallback_recipe(self, ingredients: List[str], appliances: List[str]) -> dict:
        """Create a generic fallback recipe"""
        ingredient_str = ', '.join(ingredients[:3])
        appliance_name = appliances[0] if appliances else "microwave"

        return {
            "title": f"Creative {ingredient_str} Dish",
            "description": f"A resourceful dorm meal using {ingredient_str} prepared with your {appliance_name}",
            "steps": [
                {
                    "step_number": 1,
                    "instruction": f"Gather and prepare your ingredients: {ingredient_str}",
                    "duration_minutes": 5
                },
                {
                    "step_number": 2,
                    "instruction": f"Use your {appliance_name} to cook the ingredients",
                    "duration_minutes": 10
                },
                {
                    "step_number": 3,
                    "instruction": "Check for doneness and adjust cooking time as needed",
                    "duration_minutes": 5
                },
                {
                    "step_number": 4,
                    "instruction": "Plate and enjoy your creation!",
                    "duration_minutes": 2
                }
            ],
            "time_minutes": 22,
            "difficulty": "easy",
            "servings": 2,
            "appliances_used": appliances,
            "notes": "This is a creative recipe based on your available ingredients. Experiment with seasonings and cooking times!"
        }
