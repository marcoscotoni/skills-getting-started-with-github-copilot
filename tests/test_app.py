import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivitiesEndpoint:
    """Tests for the /activities GET endpoint"""

    def test_get_activities_returns_200(self):
        """Test that /activities returns a 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self):
        """Test that /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()

        for activity_name, activity_details in activities.items():
            assert isinstance(activity_name, str)
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)

    def test_get_activities_has_chess_club(self):
        """Test that Chess Club is in the activities"""
        response = client.get("/activities")
        activities = response.json()
        assert "Chess Club" in activities


class TestSignupEndpoint:
    """Tests for the /activities/{activity_name}/signup POST endpoint"""

    def test_signup_valid_activity_and_email(self):
        """Test successful signup for a valid activity and email"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        assert "message" in response.json()
        assert "Signed up" in response.json()["message"]

    def test_signup_nonexistent_activity(self):
        """Test signup for a non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_duplicate_email(self):
        """Test that duplicate signup returns 400 error"""
        email = "duplicate@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        assert response1.status_code == 200

        # Second signup with same email should fail
        response2 = client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"].lower()

    def test_signup_persists_participant(self):
        """Test that signup adds participant to the activity"""
        email = "persistent@mergington.edu"
        
        # Sign up
        client.post(
            "/activities/Art Studio/signup",
            params={"email": email}
        )

        # Verify participant is in the activity
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Art Studio"]["participants"]


class TestUnregisterEndpoint:
    """Tests for the /activities/{activity_name}/unregister POST endpoint"""

    def test_unregister_valid_participant(self):
        """Test successful unregister of a participant"""
        email = "unregister@mergington.edu"
        
        # First, sign up
        client.post(
            "/activities/Basketball Team/signup",
            params={"email": email}
        )

        # Then unregister
        response = client.post(
            "/activities/Basketball Team/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]

    def test_unregister_removes_participant(self):
        """Test that unregister removes the participant from the activity"""
        email = "remove@mergington.edu"
        
        # Sign up
        client.post(
            "/activities/Tennis Club/signup",
            params={"email": email}
        )

        # Unregister
        client.post(
            "/activities/Tennis Club/unregister",
            params={"email": email}
        )

        # Verify participant is removed
        response = client.get("/activities")
        activities = response.json()
        assert email not in activities["Tennis Club"]["participants"]

    def test_unregister_nonexistent_activity(self):
        """Test unregister from non-existent activity returns 404"""
        response = client.post(
            "/activities/Fake Activity/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404

    def test_unregister_not_registered_participant(self):
        """Test unregister for non-registered participant returns 400"""
        response = client.post(
            "/activities/Debate Team/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"].lower()


class TestRootEndpoint:
    """Tests for the root / endpoint"""

    def test_root_redirects(self):
        """Test that root endpoint redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
