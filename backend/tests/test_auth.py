import pytest


def test_user_registration_success(client):
    """SCRUM-8: User Registration - Valid details create user account."""
    res = client.post("/api/auth/register", json={
        "email": "newuser@university.edu",
        "password": "Password123!",
        "full_name": "New User"
    })
    assert res.status_code == 201
    data = res.json()
    assert "access_token" in data
    assert data["user"]["email"] == "newuser@university.edu"
    assert data["user"]["full_name"] == "New User"


def test_user_registration_duplicate_rejected(client, registered_user):
    """SCRUM-8: Duplicate emails must be rejected with 400."""
    res = client.post("/api/auth/register", json={
        "email": registered_user["user"]["email"],
        "password": "AnotherPassword123!",
        "full_name": "Duplicate Person"
    })
    assert res.status_code == 400
    assert "already exists" in res.json()["detail"].lower()


def test_user_login_success(client, registered_user):
    """SCRUM-9: User Login - Correct credentials issue access token."""
    res = client.post("/api/auth/login", json={
        "email": registered_user["user"]["email"],
        "password": registered_user["raw_password"]
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["email"] == registered_user["user"]["email"]


def test_user_login_invalid_password(client, registered_user):
    """SCRUM-9: Wrong password returns 401 Unauthorized."""
    res = client.post("/api/auth/login", json={
        "email": registered_user["user"]["email"],
        "password": "WrongPasswordXYZ!"
    })
    assert res.status_code == 401
    assert "Invalid email or password" in res.json()["detail"]


def test_user_profile_management(client, registered_user):
    """SCRUM-10: User Profile Management - View and update details."""
    headers = registered_user["headers"]

    # View profile
    res_get = client.get("/api/users/profile", headers=headers)
    assert res_get.status_code == 200
    assert res_get.json()["email"] == registered_user["user"]["email"]

    # Update profile
    res_put = client.put("/api/users/profile", json={
        "full_name": "Alex Updated",
        "bio": "Graduate researcher in AI systems."
    }, headers=headers)
    assert res_put.status_code == 200
    assert res_put.json()["full_name"] == "Alex Updated"
    assert res_put.json()["bio"] == "Graduate researcher in AI systems."


def test_user_logout(client, registered_user):
    """SCRUM-11: User Logout endpoint."""
    headers = registered_user["headers"]
    res = client.post("/api/auth/logout", headers=headers)
    assert res.status_code == 200
    assert res.json()["success"] is True


def test_password_change(client, registered_user):
    """SCRUM-20: Change password with validation."""
    headers = registered_user["headers"]

    # Attempt with wrong current password
    bad_res = client.post("/api/users/change-password", json={
        "current_password": "WrongPassword!",
        "new_password": "BrandNewPassword123!"
    }, headers=headers)
    assert bad_res.status_code == 400

    # Successful password change
    good_res = client.post("/api/users/change-password", json={
        "current_password": registered_user["raw_password"],
        "new_password": "BrandNewPassword123!"
    }, headers=headers)
    assert good_res.status_code == 200
    assert good_res.json()["success"] is True

    # Verify login with new password
    login_res = client.post("/api/auth/login", json={
        "email": registered_user["user"]["email"],
        "password": "BrandNewPassword123!"
    })
    assert login_res.status_code == 200
