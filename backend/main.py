import logging
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from .models import RecipeRequest, RecipeResponse, RecipeContent, ApplianceCreate, ApplianceUpdate, ApplianceResponse
from .database import init_db, close_db, get_db, Recipe, Appliance

# Try to import real LLM service, fallback to mock
try:
    from .llm_service import LLMService
    LLM_AVAILABLE = True
except Exception:
    from .mock_llm_service import MockLLMService as LLMService
    LLM_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="DormChef API",
    description="Generate personalized recipes based on ingredients and appliances",
    version="1.0.0",
)

# Initialize LLM service with fallback to mock
llm_service = LLMService()
logger.info(f"LLM Service initialized: {'Real OpenAI' if LLM_AVAILABLE else 'Mock (testing mode)'}")


@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    await init_db()
    logger.info("DormChef backend started")


@app.on_event("shutdown")
async def shutdown():
    """Close database on shutdown"""
    await close_db()
    logger.info("DormChef backend shutdown")


@app.post("/api/generate", response_model=RecipeResponse)
async def generate_recipe(
    request: RecipeRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a recipe based on ingredients and appliance.
    
    Args:
        request: RecipeRequest with ingredients list and appliance
        db: Database session
        
    Returns:
        RecipeResponse with generated recipe and ID
    """
    try:
        # Validate input
        if not request.ingredients or len(request.ingredients) == 0:
            raise HTTPException(status_code=400, detail="At least one ingredient required")
        
        if not request.appliance or len(request.appliance.strip()) == 0:
            raise HTTPException(status_code=400, detail="Appliance is required")

        # Call LLM service
        logger.info(f"Generating recipe with {len(request.ingredients)} ingredients, appliance: {request.appliance}")
        recipe_content = await llm_service.generate(request.ingredients, request.appliance)

        # Validate LLM response
        if not recipe_content or not isinstance(recipe_content, dict):
            raise HTTPException(status_code=500, detail="Invalid recipe format")

        # Create Recipe DB record
        recipe_db = Recipe(
            ingredients=request.ingredients,
            appliance=request.appliance,
            content=recipe_content,
        )

        db.add(recipe_db)
        await db.commit()
        await db.refresh(recipe_db)

        logger.info(f"Recipe saved with ID: {recipe_db.id}")

        # Convert to response model
        response = RecipeResponse(
            id=recipe_db.id,
            ingredients=recipe_db.ingredients,
            appliance=recipe_db.appliance,
            content=RecipeContent(**recipe_content),
            created_at=recipe_db.created_at,
        )

        return response

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/recipes", response_model=list[RecipeResponse])
async def get_recipes(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve recipe history (paginated, sorted by newest first).
    
    Args:
        skip: Number of recipes to skip
        limit: Maximum number of recipes to return
        db: Database session
        
    Returns:
        List of recipes from database
    """
    try:
        stmt = select(Recipe).order_by(desc(Recipe.created_at)).offset(skip).limit(limit)
        result = await db.execute(stmt)
        recipes = result.scalars().all()

        return [
            RecipeResponse(
                id=r.id,
                ingredients=r.ingredients,
                appliance=r.appliance,
                content=RecipeContent(**r.content),
                created_at=r.created_at,
            )
            for r in recipes
        ]
    except Exception as e:
        logger.error(f"Error retrieving recipes: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Appliances CRUD endpoints
@app.get("/api/appliances", response_model=list[ApplianceResponse])
async def get_appliances(db: AsyncSession = Depends(get_db)):
    """Get all appliances (built-in and user-created)"""
    try:
        result = await db.execute(select(Appliance).order_by(desc(Appliance.is_default), Appliance.name))
        appliances = result.scalars().all()
        return [ApplianceResponse.from_orm(a) for a in appliances]
    except Exception as e:
        logger.error(f"Error retrieving appliances: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/appliances", response_model=ApplianceResponse)
async def create_appliance(appliance: ApplianceCreate, db: AsyncSession = Depends(get_db)):
    """Create a new appliance"""
    try:
        # Check if name already exists
        result = await db.execute(select(Appliance).where(Appliance.name == appliance.name))
        if result.scalars().first():
            raise HTTPException(status_code=400, detail="Appliance with this name already exists")
        
        db_appliance = Appliance(
            name=appliance.name,
            description=appliance.description,
            is_default=0  # User-created appliances are not default
        )
        db.add(db_appliance)
        await db.commit()
        await db.refresh(db_appliance)
        return ApplianceResponse.from_orm(db_appliance)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating appliance: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


@app.put("/api/appliances/{appliance_id}", response_model=ApplianceResponse)
async def update_appliance(appliance_id: int, appliance: ApplianceUpdate, db: AsyncSession = Depends(get_db)):
    """Update an appliance"""
    try:
        result = await db.execute(select(Appliance).where(Appliance.id == appliance_id))
        db_appliance = result.scalars().first()
        if not db_appliance:
            raise HTTPException(status_code=404, detail="Appliance not found")
        
        # Cannot update default appliances
        if db_appliance.is_default:
            raise HTTPException(status_code=400, detail="Cannot update default appliances")
        
        if appliance.name:
            # Check if new name already exists
            result = await db.execute(select(Appliance).where(
                Appliance.name == appliance.name,
                Appliance.id != appliance_id
            ))
            if result.scalars().first():
                raise HTTPException(status_code=400, detail="Appliance with this name already exists")
            db_appliance.name = appliance.name
        
        if appliance.description is not None:
            db_appliance.description = appliance.description
        
        await db.commit()
        await db.refresh(db_appliance)
        return ApplianceResponse.from_orm(db_appliance)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating appliance: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


@app.delete("/api/appliances/{appliance_id}")
async def delete_appliance(appliance_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a user-created appliance"""
    try:
        result = await db.execute(select(Appliance).where(Appliance.id == appliance_id))
        db_appliance = result.scalars().first()
        if not db_appliance:
            raise HTTPException(status_code=404, detail="Appliance not found")
        
        # Cannot delete default appliances
        if db_appliance.is_default:
            raise HTTPException(status_code=400, detail="Cannot delete default appliances")
        
        await db.delete(db_appliance)
        await db.commit()
        return {"message": "Appliance deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting appliance: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/")
async def root():
    """Serve frontend"""
    import os
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "index.html")
    if not os.path.exists(frontend_path):
        return {"error": f"Frontend not found at {frontend_path}"}
    return FileResponse(frontend_path)


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
