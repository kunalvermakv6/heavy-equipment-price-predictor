"""
Script to prepare and serialize the data preprocessor using joblib.
Matches the feature engineering and ordinal encoding from the training notebook.
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import OrdinalEncoder

def fit_and_save_preprocessor(
    train_path: str = "heavy-equipment-selling-price-prediction-challenge (1)/train.csv",
    output_path: str = "backend/preprocessor.pkl",
    model_path: str = "lgbm_model.pkl"
):
    print(f"Reading training data from: {train_path}...")
    train = pd.read_csv(train_path, low_memory=False)
    
    # 1. Cleaning & Imputing
    sparse_cols = ['col4', 'col5', 'col18', 'col19']
    train_clean = train.drop(columns=sparse_cols, errors='ignore')
    
    cat_cols_initial = train_clean.select_dtypes(include=['object', 'string']).columns.tolist()
    for col in cat_cols_initial:
        train_clean[col] = train_clean[col].fillna('Unknown').astype(str)
        
    if 'ManufactureYear' in train_clean.columns:
        train_clean['ManufactureYear'] = train_clean['ManufactureYear'].replace(1001, np.nan)
        
    # 2. Feature engineering
    train_fe = train_clean.copy()
    if 'OperationalHoursMeter' in train_fe.columns:
        train_fe['HasOperationalHours'] = train_fe['OperationalHoursMeter'].notna().astype(int)
        
    # 3. Categorical columns for OrdinalEncoder
    cat_cols = train_fe.select_dtypes(include=['object', 'category', 'string']).columns.tolist()
    print(f"Fitting OrdinalEncoder on {len(cat_cols)} categorical columns...")
    encoder = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)
    encoder.fit(train_fe[cat_cols])
    
    # 4. Load model to get exact expected feature order
    model = joblib.load(model_path)
    feature_names = list(model.feature_name_)
    print(f"Model expects {len(feature_names)} features: {feature_names}")
    
    # 5. Build and save artifact as pure dictionary to avoid any module namespace pickle issues
    artifact = {
        "cat_cols": cat_cols,
        "encoder": encoder,
        "feature_names": feature_names,
        "sparse_cols": sparse_cols
    }
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    joblib.dump(artifact, output_path)
    print(f"Successfully saved preprocessor to {output_path} using joblib!")
    
    return artifact

if __name__ == "__main__":
    fit_and_save_preprocessor()
