import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange: Reset activities before each test
    for activity in activities.values():
        activity["participants"] = []


def test_get_activities():
    # Arrange: Ensure at least one activity exists
    activities["Chess Club"]["participants"] = ["alice@mergington.edu"]

    # Act: Send GET request
    response = client.get("/activities")

    # Assert: Check response
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["participants"] == ["alice@mergington.edu"]


def test_signup_for_activity():
    # Arrange: Prepare email and activity
    email = "bob@mergington.edu"
    activity_name = "Chess Club"

    # Act: Send POST request to sign up
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Check response and participant added
    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"


def test_signup_duplicate():
    # Arrange: Add participant first
    email = "bob@mergington.edu"
    activity_name = "Chess Club"
    activities[activity_name]["participants"] = [email]

    # Act: Try to sign up again
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Should return error
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_signup_nonexistent_activity():
    # Arrange: Use invalid activity name
    email = "bob@mergington.edu"
    activity_name = "Nonexistent"

    # Act: Try to sign up
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Should return 404
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
