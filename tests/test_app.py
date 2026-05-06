import copy

from fastapi.testclient import TestClient

from src import app

client = TestClient(app.app)


def reset_activities():
    original = copy.deepcopy(app.activities)
    try:
        yield
    finally:
        app.activities.clear()
        app.activities.update(original)


def test_get_activities_returns_all_activities():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert expected_activity in data
    assert "description" in data[expected_activity]
    assert "participants" in data[expected_activity]


def test_signup_for_activity_adds_participant_and_returns_success():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    original_participants = list(app.activities[activity_name]["participants"])

    try:
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        assert email in app.activities[activity_name]["participants"]
        assert len(app.activities[activity_name]["participants"]) == len(original_participants) + 1
    finally:
        app.activities[activity_name]["participants"] = original_participants


def test_duplicate_signup_returns_bad_request():
    # Arrange
    activity_name = "Chess Club"
    email = app.activities[activity_name]["participants"][0]

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
