"""
Tests for Authentication Endpoints
"""
import pytest
from httpx import AsyncClient
from app.main import app


@pytest.fixture
def test_user_data():
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPassword123!",
        "full_name": "Test User"
    }


@pytest.mark.asyncio
async def test_register_user(test_user_data):
    """Test user registration"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["username"] == test_user_data["username"]
        assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(test_user_data):
    """Test registration with duplicate email"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First registration
        await client.post("/api/v1/auth/register", json=test_user_data)
        
        # Duplicate registration
        response = await client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_success(test_user_data):
    """Test successful login"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register user first
        await client.post("/api/v1/auth/register", json=test_user_data)
        
        # Login
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        response = await client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(test_user_data):
    """Test login with wrong password"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register user first
        await client.post("/api/v1/auth/register", json=test_user_data)
        
        # Login with wrong password
        login_data = {
            "email": test_user_data["email"],
            "password": "WrongPassword123!"
        }
        response = await client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(test_user_data):
    """Test getting current user profile"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register and login
        await client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await client.post("/api/v1/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        
        token = login_response.json()["access_token"]
        
        # Get current user
        response = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_data["email"]
