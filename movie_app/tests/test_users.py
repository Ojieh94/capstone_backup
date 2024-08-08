import pytest


@pytest.mark.parametrize("username, email, full_name, password", [("testuser", "testuser@example.com", "Test User", "testpassword123")])
def test_signup_new_user(client, setup_database, username, email, full_name, password):
    response = client.post(
        "/signup/", json={"username": username, "email": email, "full_name": full_name, "password": password})

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"
    assert data["full_name"] == "Test User"

    assert "password" not in data


@pytest.mark.parametrize("username, email, full_name, password", [("testuser", "testuser@example.com", "Test User", "testpassword123")])
def test_signup_existing_user(client, setup_database, username, email, full_name, password):

    # Attempt to signup with existing user
    response = client.post(
        "/signup/", json={"username": username, "email": email, "full_name": full_name, "password": password})

    assert response.status_code == 400
    assert response.json() == {"detail": "User already registered"}


@pytest.mark.parametrize("username, password", [("testuser", "testpassword123")])
def test_login(client, setup_database, username, password):


    # Login
    response = client.post(
        "/login/", data={"username": username,  "password": password})

    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Test Login with wrong username
    response = client.post(
        "/login/", data={"username": "wrong_username",  "password": password})
    
    assert response.status_code == 401
    data = response.json()
    assert data == {"detail": "Incorrect username or password"}

    # Test Login with incorrect password
    response = client.post(
        "/login/", data={"username": username,  "password": "wrong_password"})

    assert response.status_code == 401
    data = response.json()
    assert data == {"detail": "Incorrect username or password"}

def test_get_users(client, setup_database):

    response = client.get("/users")

    assert response.status_code == 200
    data = response.json()
    
    assert all("username" in user for user in data)
    assert all("email" in user for user in data)
    assert all("full_name" in user for user in data)
    

@pytest.mark.parametrize("user_id, wrong_id, expected_username, expected_email, expected_fullname", [(1, 99, "testuser", "testuser@example.com", "Test User")])
def test_get_user_by_id(client, setup_database, user_id, wrong_id, expected_username, expected_email, expected_fullname):
    # Assert for invalid id
    response = client.get(f"/users/{wrong_id}")
    assert response.status_code == 404

    response = client.get(f"/users/{user_id}")

    assert response.status_code == 200
    data = response.json()

    assert data["username"] == expected_username
    assert data["email"] == expected_email
    assert data["full_name"] == expected_fullname

    
@pytest.mark.parametrize("username, wrong_username, email, full_name", [("testuser", "wronguser", "testuser@example.com", "Test User")])
def test_get_user_by_username(client, setup_database, username, wrong_username, email, full_name):
    response = client.get(f"/users/name/{username}")

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email
    assert data["full_name"] == full_name

    # Test for wrong username

    response = client.get(f"/users/name/{wrong_username}")

    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": "User not found"}


@pytest.mark.parametrize("username, password, user_id, wrong_id, another_user_id", [
    ("testuser", "testpassword123", 1, 99, 2)
])
def test_update_user(client, setup_database, username, password, user_id, wrong_id, another_user_id):
    # Test if user exists
    response = client.get(f"/users/{user_id}")

    assert response.status_code == 200

    # Test if not user
    response = client.get(f"/users/{wrong_id}")

    assert response.status_code == 404

    # Login to authenticate
    response = client.post(
        "/login/", data={"username": username,  "password": password})

    assert response.status_code == 200
    token = response.json()["access_token"]

    update_payload = {"full_name": "Updated User"}

    # Test authentication
    response = client.put(f"/users/{user_id}", json=update_payload)
    assert response.status_code == 401

    response = client.put(f"/users/{user_id}", json=update_payload,
                          headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == update_payload["full_name"]
    assert data["username"] == username

    # Test authentication for authenticated user not to be able to delete another user

    # Signup another_user
    response = client.post(
        "/signup/", json={"username": "testuser2", "email": "testuser2@email.com", "full_name": "Test User2", "password": "testpassword123"})

    # Test to see if an authenticated user can edit another_user (should throw a 401 because not authorized to do so)
    response = client.put(f"/users/{another_user_id}", json=update_payload,
                          headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    data = response.json()
    assert data == {"detail": "Not authorized"}


@pytest.mark.parametrize("username, password, user_id, wrong_id, another_user_id", [("testuser2", "testpassword123", 2, 99, 1)])
def test_delete_user(client, setup_database, username, password, user_id, wrong_id, another_user_id):
   

    # Login to authenticate
    response = client.post(
        "/login/", data={"username": username,  "password": password})

    assert response.status_code == 200
    token = response.json()["access_token"]

    # Test for authentication
    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 401

    # Test to delete user not in db
    response = client.delete(f"/users/{wrong_id}",
                             headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": "User not found"}

    # Test if authenticated user can delete another user
    response = client.delete(f"/users/{another_user_id}",
                             headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    data = response.json()
    assert data == {"detail": "Not authorized"}

    # Test Authenticated user can delete account
    response = client.delete(
        f"/users/{user_id}", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert data == {"message": "Successful"}
