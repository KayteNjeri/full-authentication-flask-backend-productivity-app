def test_workouts_require_authentication(client):
    response = client.get("/workouts")

    assert response.status_code == 401


def test_create_workout(client, auth_headers):
    response = client.post(
        "/workouts",
        json={
            "date": "2026-09-12",
            "duration_minutes": 45,
            "notes": "Morning workout"
        },
        headers=auth_headers
    )

    assert response.status_code == 201