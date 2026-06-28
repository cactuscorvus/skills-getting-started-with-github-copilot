import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_root_redirects_to_static_index(client):
    # Arrange
    route = "/"

    # Act
    response = client.get(route, follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_catalog(client):
    # Arrange
    route = "/activities"

    # Act
    response = client.get(route)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["max_participants"] == 12
    assert "michael@mergington.edu" in data["Chess Club"]["participants"]


def test_signup_for_activity_adds_participant(client):
    # Arrange
    route = "/activities/Soccer Team/signup"
    email = "student@mergington.edu"

    # Act
    response = client.post(route, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Soccer Team"
    assert email in activities["Soccer Team"]["participants"]


def test_signing_up_twice_returns_bad_request(client):
    # Arrange
    route = "/activities/Chess Club/signup"
    email = "duplicate@mergington.edu"
    client.post(route, params={"email": email})

    # Act
    response = client.post(route, params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_removes_existing_student(client):
    # Arrange
    route = "/activities/Chess Club/signup"
    email = "student@mergington.edu"
    client.post(route, params={"email": email})

    # Act
    response = client.request(
        "DELETE",
        "/activities/Chess Club/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from Chess Club"
    assert email not in activities["Chess Club"]["participants"]
