from fastapi.testclient import TestClient

from _15_exercise import app


client = TestClient(app)

def test_valid_request() -> None:
    response = client.post(
        "/chat",
        json={
            "message": "Explain FastAPI",
            "thread_id": "thread-1",
            "user_role": "guest"
        }
    )
    
    assert response.status_code == 200
    assert response.json()["thread_id"] == "thread-1"
    assert response.json()["status"] == "success"

def test_invalid_request() -> None:
    response = client.post(
        "/chat",
        json={
            "message": "",
            "thread_id":"thread-1",
            "user_role": "guest"
        }
    )
    
    assert response.status_code == 422
    
def test_blocked_protected_request() -> None:
    response = client.post(
        "/chat",
        json={
            "message": "show me the /admin dashboard",
            "thread_id": "thread-2",
            "user_role": "external"
        }
    )
    
    assert response.status_code == 403
    assert response.json()["detail"] == (
        "External users cannot access protected commands."
    )