import json
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    print("GET /health -> Status Code:", response.status_code)
    data = response.json()
    print("Response JSON:", json.dumps(data, indent=2))
    assert response.status_code == 200
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    print("Health check passed!")

def test_predict():
    payload = {
        "AssetID": 999097,
        "ProductConfigID": 3168,
        "DataOriginCode": "ACH138",
        "VendorPartnerID": "GTX",
        "ManufactureYear": 2005,
        "OperationalHoursMeter": 68.0,
        "UtilizationTier": "Low",
        "TransactionDate": "2007-11-16",
        "Spec_FullDescriptor": "521D",
        "Spec_BaseClass": "521",
        "Spec_SubClass": "D",
        "FunctionalClassification": "Wheel Loader - 110.0 to 120.0 Horsepower",
        "RegionCode": "Alabama",
        "InventoryGroupCategory": "WL",
        "InventoryGroupDescription": "Wheel Loader",
        "CabinType": "EROPS w AC",
        "Forks": "None or Unspecified",
        "col10": "2 Valve",
        "col28": "Standard",
        "col29": "Conventional"
    }

    response = client.post("/predict", json=payload)
    print("\nPOST /predict -> Status Code:", response.status_code)
    data = response.json()
    print("Response JSON:", json.dumps(data, indent=2))
    assert response.status_code == 200
    assert "predicted_price" in data
    assert data["predicted_price"] > 0
    print("Prediction test passed!")

if __name__ == "__main__":
    test_health()
    test_predict()
