# Heavy Equipment Selling Price Predictor

This project predicts the sale price, in USD, of used heavy equipment from its specifications, age, operating hours, and sale region. The trained LightGBM regressor predicts log price; the API converts that result back to dollars.

## Example request

Send this JSON to `POST /predict`:

```json
{
  "ManufactureYear": 2005,
  "OperationalHoursMeter": 68.0,
  "Spec_FullDescriptor": "521D",
  "FunctionalClassification": "Wheel Loader - 110.0 to 120.0 Horsepower",
  "RegionCode": "Alabama",
  "CabinType": "EROPS w AC"
}
```

Example response:

```json
{
  "predicted_price": 63054.16,
  "predicted_price_formatted": "$63,054.16",
  "log_prediction": 11.05177,
  "currency": "USD",
  "model_used": "LightGBM Regressor (45 features)",
  "equipment_summary": {
    "ManufactureYear": 2005,
    "OperationalHoursMeter": 68.0,
    "Spec_FullDescriptor": "521D",
    "FunctionalClassification": "Wheel Loader - 110.0 to 120.0 Horsepower",
    "RegionCode": "Alabama",
    "CabinType": "EROPS w AC"
  }
}
```

The predicted value in the response depends on the supplied features and the bundled model.

## Run locally

Python 3.10+ and Node.js are needed. From the project root:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

In a second terminal, run the Vue development frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173>. The API is at <http://localhost:8000>; interactive API docs are at <http://localhost:8000/docs>. `GET /health` reports whether the model loaded. The trained model is `lgbm_model.pkl`; the fitted preprocessing artifact is `backend/preprocessor.pkl`.
