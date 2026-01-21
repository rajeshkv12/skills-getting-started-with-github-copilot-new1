"""
Tests for the Mergington High School Activities API
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI application"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    global activities
    activities.clear()
    activities.update({
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
        "Soccer Team": {
            "description": "Competitive soccer training and inter-school matches",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["alex@mergington.edu", "ryan@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Basketball practice and friendly competitions",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["sarah@mergington.edu", "james@mergington.edu"]
        },
        "Drama Club": {
            "description": "Theater performances, acting workshops, and stage productions",
            "schedule": "Wednesdays, 3:30 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["emily@mergington.edu", "lucas@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and various visual arts techniques",
            "schedule": "Fridays, 3:00 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["ava@mergington.edu", "noah@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Competitive science team preparing for regional and national tournaments",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["ethan@mergington.edu", "mia@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop critical thinking and public speaking through competitive debates",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["william@mergington.edu", "isabella@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    })


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that root path redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for the GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Soccer Team" in data
    
    def test_get_activities_returns_correct_structure(self, client):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)
    
    def test_get_activities_returns_correct_participant_data(self, client):
        """Test that participant data is correct"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_successful(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
        
        # Verify the participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_for_nonexistent_activity(self, client):
        """Test signup for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]
    
    def test_signup_when_already_registered(self, client):
        """Test that a student cannot sign up for multiple activities"""
        # Student already registered in Chess Club
        response = client.post(
            "/activities/Programming Class/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"]
    
    def test_signup_with_special_characters_in_activity_name(self, client):
        """Test signup with URL-encoded activity name"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 200


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_successful(self, client):
        """Test successful unregistration from an activity"""
        # Verify student is registered
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" in activities_data["Chess Club"]["participants"]
        
        # Unregister the student
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "michael@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
        
        # Verify the participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]
    
    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregister from an activity that doesn't exist"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]
    
    def test_unregister_when_not_registered(self, client):
        """Test unregister when student is not registered for the activity"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "not registered" in data["detail"]
    
    def test_unregister_allows_signup_again(self, client):
        """Test that after unregistering, a student can sign up for another activity"""
        # Unregister from current activity
        client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        
        # Sign up for a different activity
        response = client.post(
            "/activities/Programming Class/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify the participant was added to the new activity
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" in activities_data["Programming Class"]["participants"]
    
    def test_unregister_with_special_characters_in_activity_name(self, client):
        """Test unregister with URL-encoded activity name"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200


class TestIntegrationScenarios:
    """Integration tests for complex scenarios"""
    
    def test_full_signup_and_unregister_flow(self, client):
        """Test a complete flow: signup, verify, unregister, verify"""
        email = "testflow@mergington.edu"
        activity = "Drama Club"
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Verify signup
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        
        # Verify unregistration
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity]["participants"]
    
    def test_multiple_participants_in_same_activity(self, client):
        """Test multiple students can join the same activity"""
        activity = "Art Studio"
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        for email in emails:
            response = client.post(
                f"/activities/{activity}/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify all participants are registered
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        for email in emails:
            assert email in activities_data[activity]["participants"]
