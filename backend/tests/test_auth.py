def test_signup(client):
    response = client.post(
        "/signup",
        json={
            "username": "testuser",
            "password": "password123",
            "password_confirmation": "password123"
        }
    )

    assert response.status_code == 201


def test_login(client):
    client.post(
        "/signup",
        json={
            "username": "testuser",
            "password": "password123",
            "password_confirmation": "password123"
        }
    )

    response = client.post(
        "/login",
        json={
            "username": "testuser",
            "password": "password123"
        }
    )

    assert response.status_code == 200
    assert "token" in response.json