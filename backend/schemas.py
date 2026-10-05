from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict

class HealthResponse(BaseModel):
    status: str = Field(..., example="healthy")
    model_loaded: bool = Field(..., example=True)
    model_name: str = Field(..., example="LightGBM Heavy Equipment Price Regressor")
    version: str = Field(..., example="1.0.0")
    expected_features_count: int = Field(..., example=45)


class PredictRequest(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={
            "example": {
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
                "Spec_ReleaseSeries": None,
                "Spec_VariantModifier": None,
                "AssetScaleFactor": None,
                "FunctionalClassification": "Wheel Loader - 110.0 to 120.0 Horsepower",
                "RegionCode": "Alabama",
                "InventoryGroupCategory": "WL",
                "InventoryGroupDescription": "Wheel Loader",
                "CabinType": "EROPS w AC",
                "Forks": "None or Unspecified",
                "col1": "None or Unspecified",
                "col3": None,
                "DrivetrainType": None,
                "col6": None,
                "col7": None,
                "col8": None,
                "col9": None,
                "col10": "2 Valve",
                "col11": None,
                "col12": None,
                "col13": None,
                "col14": None,
                "col15": None,
                "col16": "None or Unspecified",
                "col20": "None or Unspecified",
                "col21": None,
                "col22": None,
                "col23": None,
                "col24": None,
                "col25": None,
                "col27": None,
                "col28": None,
                "col29": "Standard",
                "col30": "Conventional",
                "HasOperationalHours": 1
            }
        }
    )

    # Core identification & temporal
    AssetID: Optional[int] = None
    ProductConfigID: Optional[int] = None
    DataOriginCode: Optional[str] = None
    VendorPartnerID: Optional[str] = None
    ManufactureYear: Optional[float] = None
    OperationalHoursMeter: Optional[float] = None
    UtilizationTier: Optional[str] = None
    TransactionDate: Optional[str] = None

    # Specifications
    Spec_FullDescriptor: Optional[str] = None
    Spec_BaseClass: Optional[str] = None
    Spec_SubClass: Optional[str] = None
    Spec_ReleaseSeries: Optional[str] = None
    Spec_VariantModifier: Optional[str] = None
    AssetScaleFactor: Optional[str] = None
    FunctionalClassification: Optional[str] = None
    RegionCode: Optional[str] = None
    InventoryGroupCategory: Optional[str] = None
    InventoryGroupDescription: Optional[str] = None

    # Operational & subsystem configurations
    CabinType: Optional[str] = None
    DrivetrainType: Optional[str] = None
    Forks: Optional[str] = None
    col1: Optional[str] = None
    col3: Optional[str] = None
    col6: Optional[str] = None
    col7: Optional[str] = None
    col8: Optional[str] = None
    col9: Optional[str] = None
    col10: Optional[str] = None
    col11: Optional[str] = None
    col12: Optional[str] = None
    col13: Optional[str] = None
    col14: Optional[str] = None
    col15: Optional[str] = None
    col16: Optional[str] = None
    col20: Optional[str] = None
    col21: Optional[str] = None
    col22: Optional[str] = None
    col23: Optional[str] = None
    col24: Optional[str] = None
    col25: Optional[str] = None
    col27: Optional[str] = None
    col28: Optional[str] = None
    col29: Optional[str] = None
    col30: Optional[str] = None
    HasOperationalHours: Optional[int] = None


class PredictResponse(BaseModel):
    predicted_price: float = Field(..., description="Estimated heavy equipment selling price in US Dollars")
    predicted_price_formatted: str = Field(..., description="Currency formatted string, e.g. $64,193.41")
    log_prediction: float = Field(..., description="Raw log1p model output")
    currency: str = Field(default="USD")
    model_used: str = Field(default="LightGBM")
    equipment_summary: Dict[str, Any] = Field(default_factory=dict, description="Key features of the assessed asset")
