"""
FastAPI tests using AAA (Arrange-Act-Assert) pattern
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app
from copy import deepcopy


# Store original activities for resetting between tests
ORIGINAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Basketball": {
        "description": "Team basketball practice and friendly matches",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": []
    },
    "Tennis": {
        "description": "Tennis lessons and court practice for all skill levels",
        "schedule": "Tuesdays and Thursdays, 3:45 PM - 5:00 PM",
        "max_participants": 10,
        "participants": []
    },
    "Painting Studio": {
        "description": "Learn painting techniques and create your own artwork",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": []
    },
    "Drama Club": {
        "description": "Act in school plays and develop theatrical performance skills",
        "schedule": "Fridays, 3:30 PM - 5:30 PM",
        "max_participants": 25,
        "participants": []
    },
    "Debate Team": {
        "description": "Develop public speaking and critical thinking skills",
        "schedule": "Mondays and Thursdays, 4:00 PM - 5:00 PM",
        "max_participants": 14,
        "participants": []
    },
    "Science Club": {
        "description": "Explore scientific concepts through experiments and projects",
        "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
        "max_participants": 22,
        "participants": []
    }
}


@pytest.fixture
def client():
    """Fixture to provide a test client and reset activities between tests"""
    # Reset activities to original state before each test
    from src.app import activities
    activities.clear()
    activities.update(deepcopy(ORIGINAL_ACTIVITIES))
    
    return TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_all_activities_returns_success(self, client):
        # Arrange: No setup needed, data is predefined
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_activities_have_required_fields(self, client):
        # Arrange
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful(self, client):
        # Arrange
        email = "test@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert email in data["message"]
        assert activity in data["message"]

    def test_signup_activity_not_found(self, client):
        # Arrange
        email = "test@mergington.edu"
        activity = "Nonexistent Activity"
        
        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_duplicate_registration_fails(self, client):
        # Arrange
        email = "michael@mergington.edu"  # Already registered in Chess Club
        activity = "Chess Club"
        
        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_adds_participant_to_activity(self, client):
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Tennis"
        
        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")
        activities_response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = activities_response.json()
        assert email in activities[activity]["participants"]


class TestUnregisterFromActivity:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_successful(self, client):
        # Arrange
        email = "michael@mergington.edu"  # Already registered in Chess Club
        activity = "Chess Club"
        
        # Act
        response = client.post(f"/activities/{activity}/unregister?email={email}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert email in data["message"]
        assert "Unregistered" in data["message"]

    def test_unregister_activity_not_found(self, client):
        # Arrange
        email = "test@mergington.edu"
        activity = "Nonexistent Activity"
        
        # Act
        response = client.post(f"/activities/{activity}/unregister?email={email}")
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_not_signed_up_fails(self, client):
        # Arrange
        email = "notstudent@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.post(f"/activities/{activity}/unregister?email={email}")
        
        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_removes_participant_from_activity(self, client):
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.post(f"/activities/{activity}/unregister?email={email}")
        activities_response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = activities_response.json()
        assert email not in activities[activity]["participants"]


class TestRootRedirect:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_index(self, client):
        # Arrange
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
