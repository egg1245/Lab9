"""
Test suite for DormChef appliances CRUD and multi-appliance recipes
Run with: pytest backend/test_appliances.py -v
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import async_engine, Base
from backend.main import app


@pytest.fixture
async def db_session():
    """Create a test database session"""
    async with AsyncSession(async_engine) as session:
        async with session.begin():
            # Create tables
            await session.run_sync(Base.metadata.create_all)
        yield session
        async with session.begin():
            # Drop tables after test
            await session.run_sync(Base.metadata.drop_all)


@pytest.fixture
def client():
    """FastAPI test client"""
    from fastapi.testclient import TestClient
    return TestClient(app)


class TestAppliancesCRUD:
    """Test CRUD operations for appliances"""

    def test_get_all_appliances(self, client):
        """Test fetching all appliances"""
        response = client.get("/api/appliances")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 6  # At least 6 default appliances

    def test_appliances_have_default_flag(self, client):
        """Test that appliances have is_default flag"""
        response = client.get("/api/appliances")
        assert response.status_code == 200
        data = response.json()
        assert all('is_default' in a for a in data)
        assert any(a['is_default'] for a in data)  # At least one default

    def test_create_custom_appliance(self, client):
        """Test creating a new custom appliance"""
        payload = {
            "name": "Coffee Maker",
            "description": "Brew fresh coffee"
        }
        response = client.post("/api/appliances", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data['name'] == "Coffee Maker"
        assert data['description'] == "Brew fresh coffee"
        assert not data['is_default']

    def test_create_appliance_duplicate_name(self, client):
        """Test that duplicate appliance names are rejected"""
        payload = {
            "name": "Coffee Maker",
            "description": "Test"
        }
        client.post("/api/appliances", json=payload)
        response = client.post("/api/appliances", json=payload)
        assert response.status_code == 400
        assert "already exists" in response.json()['detail'].lower()

    def test_create_appliance_empty_name(self, client):
        """Test that empty names are rejected"""
        payload = {"name": "", "description": "Test"}
        response = client.post("/api/appliances", json=payload)
        assert response.status_code == 422  # Validation error

    def test_update_custom_appliance(self, client):
        """Test updating a custom appliance"""
        # Create appliance
        create_payload = {
            "name": "Test Appliance",
            "description": "Original description"
        }
        create_response = client.post("/api/appliances", json=create_payload)
        appliance_id = create_response.json()['id']

        # Update appliance
        update_payload = {
            "name": "Updated Appliance",
            "description": "Updated description"
        }
        response = client.put(f"/api/appliances/{appliance_id}", json=update_payload)
        assert response.status_code == 200
        data = response.json()
        assert data['name'] == "Updated Appliance"
        assert data['description'] == "Updated description"

    def test_cannot_update_default_appliance(self, client):
        """Test that default appliances cannot be edited"""
        # Get first default appliance
        response = client.get("/api/appliances")
        appliances = response.json()
        default_appliance = next(a for a in appliances if a['is_default'])

        # Try to update it
        update_payload = {
            "name": "Modified Microwave",
            "description": "Should fail"
        }
        response = client.put(
            f"/api/appliances/{default_appliance['id']}",
            json=update_payload
        )
        assert response.status_code == 400
        assert "default" in response.json()['detail'].lower()

    def test_delete_custom_appliance(self, client):
        """Test deleting a custom appliance"""
        # Create appliance
        create_payload = {
            "name": "Delete Me",
            "description": "Test"
        }
        create_response = client.post("/api/appliances", json=create_payload)
        appliance_id = create_response.json()['id']

        # Delete appliance
        response = client.delete(f"/api/appliances/{appliance_id}")
        assert response.status_code == 200

        # Verify deletion
        response = client.get(f"/api/appliances/{appliance_id}")
        assert response.status_code == 404

    def test_cannot_delete_default_appliance(self, client):
        """Test that default appliances cannot be deleted"""
        # Get first default appliance
        response = client.get("/api/appliances")
        appliances = response.json()
        default_appliance = next(a for a in appliances if a['is_default'])

        # Try to delete it
        response = client.delete(f"/api/appliances/{default_appliance['id']}")
        assert response.status_code == 400
        assert "default" in response.json()['detail'].lower()

    def test_delete_nonexistent_appliance(self, client):
        """Test deleting non-existent appliance"""
        response = client.delete("/api/appliances/9999")
        assert response.status_code == 404


class TestRecipeGeneration:
    """Test recipe generation with multi-appliance support"""

    def test_generate_recipe_single_appliance(self, client):
        """Test generating recipe with single appliance"""
        payload = {
            "ingredients": ["eggs", "bread"],
            "appliance_ids": [1]  # Assuming ID 1 exists (default)
        }
        response = client.post("/api/generate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert 'id' in data
        assert 'content' in data
        assert 'appliances' in data
        assert len(data['appliances']) >= 1

    def test_generate_recipe_multi_appliance(self, client):
        """Test generating recipe with multiple appliances"""
        # Get some default appliances
        response = client.get("/api/appliances")
        appliances = response.json()
        default_ids = [a['id'] for a in appliances if a['is_default']][:2]

        if len(default_ids) < 2:
            pytest.skip("Not enough default appliances for multi-test")

        payload = {
            "ingredients": ["rice", "water"],
            "appliance_ids": default_ids
        }
        response = client.post("/api/generate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert len(data['appliances']) == len(default_ids)

    def test_generate_recipe_missing_ingredients(self, client):
        """Test that empty ingredients list is rejected"""
        payload = {
            "ingredients": [],
            "appliance_ids": [1]
        }
        response = client.post("/api/generate", json=payload)
        assert response.status_code == 422  # Validation error

    def test_generate_recipe_no_appliances(self, client):
        """Test that missing appliances is rejected"""
        payload = {
            "ingredients": ["eggs"],
            "appliance_ids": []
        }
        response = client.post("/api/generate", json=payload)
        assert response.status_code == 422  # Validation error

    def test_generate_recipe_invalid_appliance_id(self, client):
        """Test that invalid appliance ID is rejected"""
        payload = {
            "ingredients": ["eggs"],
            "appliance_ids": [9999]
        }
        response = client.post("/api/generate", json=payload)
        assert response.status_code == 400
        assert "not found" in response.json()['detail'].lower()

    def test_recipe_content_structure(self, client):
        """Test that recipe content has required fields"""
        payload = {
            "ingredients": ["bread"],
            "appliance_ids": [1]
        }
        response = client.post("/api/generate", json=payload)
        assert response.status_code == 200
        data = response.json()
        content = data['content']

        required_fields = ['title', 'description', 'steps', 'time_minutes', 'difficulty', 'servings']
        assert all(field in content for field in required_fields)
        assert isinstance(content['steps'], list)
        assert len(content['steps']) > 0


class TestRecipeHistory:
    """Test recipe history retrieval"""

    def test_get_recipes_history(self, client):
        """Test fetching recipe history"""
        response = client.get("/api/recipes")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_recipe_history_includes_appliances(self, client):
        """Test that history recipes include appliances array"""
        # Generate a recipe first
        payload = {
            "ingredients": ["eggs"],
            "appliance_ids": [1]
        }
        client.post("/api/generate", json=payload)

        # Get history
        response = client.get("/api/recipes")
        assert response.status_code == 200
        data = response.json()

        if len(data) > 0:
            recipe = data[0]
            assert 'appliances' in recipe
            assert isinstance(recipe['appliances'], list)
            if len(recipe['appliances']) > 0:
                assert 'id' in recipe['appliances'][0]
                assert 'name' in recipe['appliances'][0]

    def test_recipe_history_pagination(self, client):
        """Test pagination in recipe history"""
        # Generate multiple recipes
        for i in range(5):
            payload = {
                "ingredients": [f"ingredient{i}"],
                "appliance_ids": [1]
            }
            client.post("/api/generate", json=payload)

        # Test limit parameter
        response = client.get("/api/recipes?limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3


class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_server_errors_return_detail(self, client):
        """Test that errors include detail message"""
        response = client.delete("/api/appliances/9999")
        assert response.status_code == 404
        assert 'detail' in response.json()

    def test_validation_errors_return_422(self, client):
        """Test validation error status code"""
        payload = {
            "ingredients": [],
            "appliance_ids": []
        }
        response = client.post("/api/generate", json=payload)
        assert response.status_code == 422

    def test_invalid_json_returns_422(self, client):
        """Test malformed JSON returns validation error"""
        response = client.post(
            "/api/generate",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [422, 400]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
