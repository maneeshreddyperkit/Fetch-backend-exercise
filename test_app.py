import pytest
from app import app, calculate_points

@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client

def test_calculate_points():
    receipt = {
        "retailer": "Target",
        "purchaseDate": "2023-01-01",
        "purchaseTime": "14:30",
        "items": [
            {"shortDescription": "Pepsi 12 Pack", "price": "5.49"},
            {"shortDescription": "Bread", "price": "3.99"}
        ],
        "total": "9.48"
    }
    points = calculate_points(receipt)
    assert points == 60  # Replace with the expected point total for this receipt

def test_process_receipt(client):
    payload = {
        "retailer": "Target",
        "purchaseDate": "2023-01-01",
        "purchaseTime": "14:30",
        "items": [
            {"shortDescription": "Pepsi 12 Pack", "price": "5.49"},
            {"shortDescription": "Bread", "price": "3.99"}
        ],
        "total": "9.48"
    }
    response = client.post('/receipts/process', json=payload)
    assert response.status_code == 200
    assert "id" in response.json

def test_get_points(client):
    payload = {
        "retailer": "Target",
        "purchaseDate": "2023-01-01",
        "purchaseTime": "14:30",
        "items": [
            {"shortDescription": "Pepsi 12 Pack", "price": "5.49"},
            {"shortDescription": "Bread", "price": "3.99"}
        ],
        "total": "9.48"
    }
    post_response = client.post('/receipts/process', json=payload)
    receipt_id = post_response.json["id"]
    get_response = client.get(f'/receipts/{receipt_id}/points')
    assert get_response.status_code == 200
    assert "points" in get_response.json
