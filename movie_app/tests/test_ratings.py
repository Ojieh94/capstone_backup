import pytest


@pytest.mark.parametrize("payload, expected_rating", [
    ({"movie_id": "1",
     "rating_value": "8"}, 8)
])
def test_rate_movie(client,setup_database, payload, expected_rating):
  # Signup a user

    user_data = {"username": "testuser", "email": "testuser@example.com",
                 "full_name": "Test User", "password": "testpassword123"}

    response = client.post(
        "/signup/", json=user_data)
    assert response.status_code == 201

    # Authenticate and get token
    response = client.post(
        "/login/", data={"username": "testuser",  "password": "testpassword123"})

    assert response.status_code == 200
    
    token = response.json()["access_token"]

    # Create two movies

    movie_data = {"title": "New Movie", "genre": "Drama",
                  "description": "A new drama movie."}

    another_movie_data = {"title": "Another Movie", "genre": "Action",
                          "description": "A new action movie."}

    response = client.post(
        '/movies',
        json=movie_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201

    response = client.post(
        '/movies',
        json=another_movie_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201

    response = client.post("/movies/ratings/", json=payload)

    assert response.status_code == 401

    response = client.post(
        "/movies/ratings/",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()
    
    assert data["rating_value"] == expected_rating
    assert data["user_id"] == 1

    response = client.post(
        '/movies/ratings/',
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 409
    data = response.json()
    assert data == {
        "detail": "You have already rated movie. Update existing rating"}

    
    

def test_get_rating(client, setup_database):
   response = client.get("/movies/ratings/")

   assert response.status_code == 200
   data = response.json()

   assert all("rating_value" in rating for rating in data)
   assert all("movie_id" in rating for rating in data)
   assert all("user_id" in rating for rating in data)


@pytest.mark.parametrize("rating_id, wrong_id, expected_rating_value, expected_movie_id, expected_user_id", [(1, 99, 8, 1, 1)])
def test_get_rating_by_id(client, setup_database, rating_id, wrong_id, expected_rating_value, expected_movie_id, expected_user_id):
    # Assert for invalid id
    response = client.get(f"/movies/ratings/{wrong_id}")
    assert response.status_code == 404

    response = client.get(f"/movies/ratings/{rating_id}")

    assert response.status_code == 200
    data = response.json()

    assert data["rating_value"] == expected_rating_value
    assert data["movie_id"] == expected_movie_id
    assert data["user_id"] == expected_user_id


@pytest.mark.parametrize("movie_id, wrong_id, expected_rating_value", [(1, 99, 8)])
def test_get_rating_by_movie_id(client, setup_database, movie_id, wrong_id, expected_rating_value):
    # Assert for invalid id
    response = client.get(f"/movies/ratings/movie_id/{wrong_id}")
    assert response.status_code == 404

    response = client.get(f"/movies/ratings/{movie_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["rating_value"] == expected_rating_value
    

@pytest.mark.parametrize("rating_id, wrong_id, payload, expected_rating", [
    (1, 99, {"rating_value": "5"}, 5)
])
def test_update_rating(client, setup_database,rating_id, wrong_id, payload, expected_rating):
    # Test without authentication

    response = client.put(f"/movies/ratings/{rating_id}")

    assert response.status_code == 401

    # Login and Authenticate 

    response = client.post(
        "/login/", data={"username": "testuser",  "password": "testpassword123"})

    assert response.status_code == 200
    token = response.json()["access_token"]

    response = client.put(
        f"/movies/ratings/{wrong_id}", json=payload, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": "Rating not found"}

    response = client.put(
        f"/movies/ratings/{rating_id}", json=payload, headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["rating_value"] == expected_rating

    # Login and authenticate another user to ensure that wrong user can update rating
    # Signup a user

    user_data = {"username": "testuser2", "email": "testuser2@example.com",
                 "full_name": "Test User2", "password": "testpassword123"}

    response = client.post(
        "/signup/", json=user_data)
    assert response.status_code == 201

    # Authenticate and get token
    response = client.post(
        "/login/", data={"username": "testuser2",  "password": "testpassword123"})
    
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Try to update another user's rating (should throw a 401)
    response = client.put(
        f"/movies/ratings/{rating_id}", json=payload, headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 401
    data = response.json()
    assert data == {"detail": "Not authorized"}


@pytest.mark.parametrize("rating_id, wrong_id", [
    (1, 99)
])
def test_delete_rating(client, setup_database, rating_id, wrong_id):
    # Test delete without authentication

    response = client.delete(f"/movies/ratings/{rating_id}")

    assert response.status_code == 401

    # Login and Authenticate

    response = client.post(
        "/login/", data={"username": "testuser",  "password": "testpassword123"})

    assert response.status_code == 200
    token_user1 = response.json()["access_token"]

    response = client.delete(
        f"/movies/ratings/{wrong_id}", headers={"Authorization": f"Bearer {token_user1}"})

    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": "Rating not found"}

    # Login and authenticate another user to ensure that wrong user can delete rating

    # Authenticate and get token
    response = client.post(
        "/login/", data={"username": "testuser2",  "password": "testpassword123"})

    assert response.status_code == 200
    token_user2 = response.json()["access_token"]

    # Try to delete another user's rating (should throw a 401)
    response = client.delete(
        f"/movies/ratings/{rating_id}", headers={"Authorization": f"Bearer {token_user2}"})

    assert response.status_code == 401
    data = response.json()
    assert data == {"detail": "Not authorized"}

    # Test delete rating

    response = client.delete(
        f"/movies/ratings/{rating_id}", headers={"Authorization": f"Bearer {token_user1}"})

    assert response.status_code == 200
    data = response.json()
    assert data == {"message": "Successful"}
