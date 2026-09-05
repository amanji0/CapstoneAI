from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "online", "message": "Welcome to CapstoneAI API"}

def test_generate_ideas_valid():
    payload = {
        "name": "Aman",
        "academic_field": "Computer Science",
        "interests": ["AI", "Healthcare"],
        "skills": ["Python", "React"],
        "complexity": "Beginner",
        "time_available": 16
    }
    response = client.post("/api/generate-ideas", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "ideas" in data
    assert len(data["ideas"]) <= 3
    assert data["profile_summary"]["name"] == "Aman"

def test_generate_ideas_invalid_input():
    payload = {
        "name": "", # Invalid (min_length=2)
        "academic_field": "CS",
        "interests": [],
        "skills": [],
        "complexity": "Super Advanced", # Invalid pattern
        "time_available": 100 # Invalid (max 52)
    }
    response = client.post("/api/generate-ideas", json=payload)
    assert response.status_code == 422 # Unprocessable Entity (Pydantic validation failed)

def test_analyze_github_invalid_user():
    response = client.post("/api/analyze-github", json={"username": "this-user-definitely-does-not-exist-9999999"})
    assert response.status_code == 404
