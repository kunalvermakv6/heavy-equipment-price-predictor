import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List

class EquipmentPreprocessor:
    def __init__(self, cat_cols: List[str], encoder: Any, feature_names: List[str], sparse_cols: List[str] = None):
        self.cat_cols = cat_cols
        self.encoder = encoder
        self.feature_names = feature_names
        self.sparse_cols = sparse_cols or ['col4', 'col5', 'col18', 'col19']

    def clean_and_impute(self, df: pd.DataFrame) -> pd.DataFrame:
        df_clean = df.copy()
        # Drop highly sparse columns identified in EDA
        df_clean = df_clean.drop(columns=[col for col in self.sparse_cols if col in df_clean.columns], errors='ignore')
        
        # Impute categorical columns with 'Unknown'
        for col in self.cat_cols:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].fillna('Unknown').astype(str)
            else:
                df_clean[col] = 'Unknown'
                
        # Handle numerical anomaly (ManufactureYear = 1001 placeholder)
        if 'ManufactureYear' in df_clean.columns:
            df_clean['ManufactureYear'] = pd.to_numeric(df_clean['ManufactureYear'], errors='coerce')
            df_clean['ManufactureYear'] = df_clean['ManufactureYear'].replace(1001, np.nan)
            
        return df_clean

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df_engineered = df.copy()
        
        # HasOperationalHours indicator
        if 'OperationalHoursMeter' in df_engineered.columns:
            hours = pd.to_numeric(df_engineered['OperationalHoursMeter'], errors='coerce')
            df_engineered['HasOperationalHours'] = hours.notna().astype(int)
        else:
            df_engineered['HasOperationalHours'] = 0
            
        # Temporal feature: AssetAge if TransactionYear or TransactionDate exists
        if 'TransactionYear' not in df_engineered.columns and 'TransactionDate' in df_engineered.columns:
            try:
                df_engineered['TransactionYear'] = pd.to_datetime(df_engineered['TransactionDate'], errors='coerce').dt.year
            except Exception:
                pass

        if 'TransactionYear' in df_engineered.columns and 'ManufactureYear' in df_engineered.columns:
            try:
                df_engineered['AssetAge'] = df_engineered['TransactionYear'] - df_engineered['ManufactureYear']
                df_engineered.loc[df_engineered['AssetAge'] < 0, 'AssetAge'] = np.nan
            except Exception:
                pass
                
        return df_engineered

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df_proc = self.clean_and_impute(df)
        df_proc = self.engineer_features(df_proc)
        
        # Ensure all cat_cols exist and are strings
        for col in self.cat_cols:
            if col not in df_proc.columns:
                df_proc[col] = 'Unknown'
            else:
                df_proc[col] = df_proc[col].astype(str)
                
        # Apply fitted OrdinalEncoder
        df_proc[self.cat_cols] = self.encoder.transform(df_proc[self.cat_cols])
        
        # Ensure all expected feature columns exist
        for col in self.feature_names:
            if col not in df_proc.columns:
                df_proc[col] = np.nan
            elif col not in self.cat_cols:
                # Optional numeric fields can arrive as object dtype when their
                # value is omitted (None). LightGBM requires numeric dtypes.
                df_proc[col] = pd.to_numeric(df_proc[col], errors='coerce')
                
        # Order columns to match model input
        return df_proc[self.feature_names]


class ModelService:
    def __init__(
        self,
        model_path: str = "lgbm_model.pkl",
        preprocessor_path: str = "backend/preprocessor.pkl"
    ):
        self.model_path = model_path
        self.preprocessor_path = preprocessor_path
        self.model = None
        self.preprocessor = None
        self.is_loaded = False
        self.load_artifacts()

    def load_artifacts(self):
        """Loads model and preprocessor using joblib."""
        try:
            # Check model file path (root or backend)
            actual_model_path = self.model_path
            if not os.path.exists(actual_model_path):
                alt_path = os.path.join(os.path.dirname(__file__), "..", self.model_path)
                if os.path.exists(alt_path):
                    actual_model_path = alt_path

            actual_prep_path = self.preprocessor_path
            if not os.path.exists(actual_prep_path):
                alt_prep = os.path.join(os.path.dirname(__file__), "preprocessor.pkl")
                if os.path.exists(alt_prep):
                    actual_prep_path = alt_prep

            print(f"Loading model from: {actual_model_path} using joblib...")
            self.model = joblib.load(actual_model_path)
            
            print(f"Loading preprocessor from: {actual_prep_path} using joblib...")
            artifact = joblib.load(actual_prep_path)
            
            if isinstance(artifact, dict):
                self.preprocessor = EquipmentPreprocessor(
                    cat_cols=artifact["cat_cols"],
                    encoder=artifact["encoder"],
                    feature_names=artifact["feature_names"],
                    sparse_cols=artifact.get("sparse_cols")
                )
            else:
                self.preprocessor = artifact
            
            self.is_loaded = True
            print("Model and preprocessor successfully loaded into memory!")
        except Exception as e:
            print(f"Warning: Failed to load model artifacts: {e}")
            self.is_loaded = False

    def predict(self, input_data: Dict[str, Any]) -> Tuple[float, float]:
        """
        Accepts raw equipment input dictionary, preprocesses it, and predicts
        selling price in USD using np.expm1() on log1p model output.
        """
        if not self.is_loaded or self.model is None or self.preprocessor is None:
            raise RuntimeError("Model or preprocessor is not loaded. Please verify artifact paths.")

        # Convert input dictionary to single-row DataFrame
        df_input = pd.DataFrame([input_data])
        
        # Preprocess features (clean, impute, engineer, ordinal encode, order)
        df_features = self.preprocessor.transform(df_input)
        
        # LightGBM predict returns log1p(TargetValue)
        log_preds = self.model.predict(df_features)
        log_pred = float(log_preds[0])
        
        # Reverse log1p to obtain dollar value
        price = float(np.expm1(log_pred))
        
        # Ensure non-negative price
        price = max(0.0, price)
        
        return price, log_pred

# Global singleton instance
model_service = ModelService()
