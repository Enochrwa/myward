"""Integration tests for auth endpoints."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


def test_register_and_login(client: TestClient) -> None:
    # Register
    resp = client.post(
        "/api/v1/auth/register",
        data={
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepass123",
            "full_name": "Test User",
            "gender": "other",
        },
    )
    assert resp.status_code == 201
    assert "access_token" in resp.json()

    # Login
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "securepass123"},
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    assert token

    # Me
    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["username"] == "testuser"


def test_login_wrong_password(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": "nonexistent", "password": "wrongpass"},
    )
    assert resp.status_code == 401


def test_duplicate_username(client: TestClient) -> None:
    data = {
        "username": "dupuser",
        "email": "dup@example.com",
        "password": "pass12345",
        "full_name": "Dup",
        "gender": "male",
    }
    client.post("/api/v1/auth/register", data=data)
    resp = client.post(
        "/api/v1/auth/register",
        data={**data, "email": "dup2@example.com"},
    )
    assert resp.status_code == 400
    assert "Username" in resp.json()["detail"]
