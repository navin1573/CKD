import os
import joblib
import pandas as pd
import numpy as np
import shap

# Cache the model and explainer in memory to avoid reloading on every request
_model_pipeline = None
_metadata = None
_shap_explainer = None

def get_model_paths():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pipeline_path = os.path.join(base_dir, "ckd_model_pipeline.joblib")
    metadata_path = os.path.join(base_dir, "model_metadata.joblib")
    return pipeline_path, metadata_path

def load_model():
    global _model_pipeline, _metadata, _shap_explainer
    pipeline_path, metadata_path = get_model_paths()
    
    if _model_pipeline is None:
        if not os.path.exists(pipeline_path) or not os.path.exists(metadata_path):
            raise FileNotFoundError("Model pipeline files not found. Train the model first.")
            
        _model_pipeline = joblib.load(pipeline_path)
        _metadata = joblib.load(metadata_path)
        
        # Initialize SHAP explainer for the classifier inside the pipeline
        classifier = _model_pipeline.named_steps['classifier']
        _shap_explainer = shap.TreeExplainer(classifier)
        
    return _model_pipeline, _metadata, _shap_explainer

def get_preprocessed_feature_names(preprocessor, numerical_cols, categorical_cols):
    """
    Extracts the feature names outputted by the ColumnTransformer preprocessor.
    This is necessary to map SHAP values back to their corresponding features.
    """
    # 1. Numerical columns remain unchanged
    num_features = list(numerical_cols)
    
    # 2. Categorical columns are one-hot encoded
    # We navigate through the named pipeline step to get the onehot transformer
    cat_pipeline = preprocessor.named_transformers_['cat']
    onehot_encoder = cat_pipeline.named_steps['onehot']
    
    # Get feature names out from the one-hot encoder
    cat_features = list(onehot_encoder.get_feature_names_out(categorical_cols))
    
    return num_features + cat_features

def predict_and_explain(patient_data_dict):
    """
    Takes a dictionary of raw patient features, runs preprocessing and prediction,
    and returns prediction class, probability, and SHAP explanation data.
    """
    pipeline, metadata, explainer = load_model()
    
    # Create single row DataFrame matching training columns
    df = pd.DataFrame([patient_data_dict])
    
    # Reorder columns to match the training data
    df = df[metadata['features']]
    
    # Clean numeric types in the input (force numeric conversion for safety)
    numeric_cols = metadata['numerical_cols']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    # Run prediction
    prediction_class = int(pipeline.predict(df)[0])
    prediction_prob = float(pipeline.predict_proba(df)[0][1])
    
    # Determine risk level based on clinical thresholds
    if prediction_prob < 0.3:
        risk_level = "LOW"
    elif prediction_prob < 0.7:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"
        
    # Get preprocessed representation to calculate SHAP values
    preprocessor = pipeline.named_steps['preprocessor']
    X_preprocessed = preprocessor.transform(df)
    
    # Calculate SHAP values
    # shap_values shape depends on model. For Random Forest, it returns [array(class0), array(class1)]
    # For XGBoost/LightGBM, it returns array(class1) directly or of shape (1, n_features)
    raw_shap_values = explainer.shap_values(X_preprocessed)
    
    if isinstance(raw_shap_values, list):
        # Scikit-learn Random Forest returns a list of shap values per class
        shap_values_instance = raw_shap_values[1][0]
    else:
        # XGBoost/LightGBM return shap values directly
        if len(raw_shap_values.shape) == 3:
            # Multi-class shape fallback
            shap_values_instance = raw_shap_values[0, :, 1]
        elif len(raw_shap_values.shape) == 2:
            shap_values_instance = raw_shap_values[0]
        else:
            shap_values_instance = raw_shap_values
            
    # Get preprocessed feature names to map SHAP values
    feature_names = get_preprocessed_feature_names(
        preprocessor, metadata['numerical_cols'], metadata['categorical_cols']
    )
    
    # Compile explanations list
    explanations = []
    
    # Convert preprocessed row back to dense array for matching
    if hasattr(X_preprocessed, "toarray"):
        preprocessed_values = X_preprocessed.toarray()[0]
    else:
        preprocessed_values = X_preprocessed[0]
        
    for name, shap_val, prep_val in zip(feature_names, shap_values_instance, preprocessed_values):
        explanations.append({
            'feature': name,
            'shap_value': float(shap_val),
            'preprocessed_value': float(prep_val)
        })
        
    # Sort by absolute SHAP value to show most influential factors first
    explanations = sorted(explanations, key=lambda x: abs(x['shap_value']), reverse=True)
    
    # Add base value (expected value of the model prediction)
    # TreeExplainer stores expected_value. For Random Forest list, it is expected_value[1]
    expected_value = explainer.expected_value
    if isinstance(expected_value, list) or isinstance(expected_value, np.ndarray):
        if len(expected_value) > 1:
            base_value = float(expected_value[1])
        else:
            base_value = float(expected_value[0])
    else:
        base_value = float(expected_value)
        
    return {
        'prediction': prediction_class,
        'probability': prediction_prob,
        'risk_level': risk_level,
        'base_value': base_value,
        'explanations': explanations
    }
