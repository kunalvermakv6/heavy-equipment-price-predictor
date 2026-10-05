import os
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from backend.schemas import HealthResponse, PredictRequest, PredictResponse
from backend.model_service import model_service

app = FastAPI(
    title="Heavy Equipment Selling Price Predictor API",
    description="Production-ready FastAPI service predicting heavy equipment transaction prices using a trained LightGBM Gradient Boosted Regressor.",
    version="1.0.0",
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """
    Health check endpoint returning system status and whether the ML model is loaded.
    """
    return HealthResponse(
        status="healthy" if model_service.is_loaded else "degraded",
        model_loaded=model_service.is_loaded,
        model_name="LightGBM Heavy Equipment Price Regressor",
        version="1.0.0",
        expected_features_count=len(model_service.preprocessor.feature_names) if model_service.preprocessor else 45,
    )


@app.post("/predict", response_model=PredictResponse, tags=["Prediction"])
def predict_price(request: PredictRequest):
    """
    Predict the selling price of heavy equipment given its mechanical,
    operational, and inventory configuration features.
    """
    if not model_service.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not loaded or unavailable."
        )

    try:
        input_data = request.model_dump()
        price, log_pred = model_service.predict(input_data)
        
        formatted_price = f"${price:,.2f}"
        
        summary = {
            "AssetID": request.AssetID,
            "ManufactureYear": request.ManufactureYear,
            "OperationalHoursMeter": request.OperationalHoursMeter,
            "Spec_FullDescriptor": request.Spec_FullDescriptor,
            "FunctionalClassification": request.FunctionalClassification,
            "RegionCode": request.RegionCode,
            "CabinType": request.CabinType,
        }

        return PredictResponse(
            predicted_price=round(price, 2),
            predicted_price_formatted=formatted_price,
            log_prediction=round(log_pred, 5),
            currency="USD",
            model_used="LightGBM Regressor (45 features)",
            equipment_summary={k: v for k, v in summary.items() if v is not None}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Prediction error: {str(e)}"
        )


# Serve frontend if built
dist_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(dist_dir):
    app.mount("/assets", StaticFiles(directory=os.path.join(dist_dir, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend(full_path: str):
        file_path = os.path.join(dist_dir, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(dist_dir, "index.html"))
else:
    @app.get("/", tags=["Root"])
    def root():
        return {
            "message": "Heavy Equipment Price Prediction API",
            "docs": "/docs",
            "health": "/health",
            "predict": "/predict",
            "status": "online"
        }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)
