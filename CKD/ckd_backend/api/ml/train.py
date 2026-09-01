import os
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

# Import Classifiers
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

def load_and_clean_data(filepath):
    print("Loading dataset...")
    df = pd.read_csv(filepath)
    
    # Drop the 'id' column as it is a non-informative index
    if 'id' in df.columns:
        df = df.drop(columns=['id'])
        
    print("Initial shape:", df.shape)
    
    # 1. Clean nominal/categorical columns (strip spaces, remove tabs)
    nominal_cols = ['rbc', 'pc', 'pcc', 'ba', 'htn', 'dm', 'cad', 'appet', 'pe', 'ane', 'classification']
    for col in nominal_cols:
        if col in df.columns:
            # Convert to string, strip whitespace, replace tabs, and handle NaN
            df[col] = df[col].astype(str).str.strip().str.replace('\t', '')
            # Convert 'nan' back to numpy NaN
            df[col] = df[col].replace('nan', np.nan)
            
    # Clean specifically mislabeled classes in target and features
    # target 'classification' should only be 'ckd' or 'notckd'
    if 'classification' in df.columns:
        df['classification'] = df['classification'].replace({'ckd': 'ckd', 'notckd': 'notckd'})
        # Map target to 1 for ckd and 0 for notckd
        df['target'] = df['classification'].map({'ckd': 1, 'notckd': 0})
        df = df.drop(columns=['classification'])
        
    # Clean features like 'dm' (diabetes mellitus) and 'cad' (coronary artery disease)
    if 'dm' in df.columns:
        df['dm'] = df['dm'].replace({'yes': 'yes', 'no': 'no'})
    if 'cad' in df.columns:
        df['cad'] = df['cad'].replace({'yes': 'yes', 'no': 'no'})
        
    # 2. Clean numeric columns that were imported as objects
    numeric_object_cols = ['pcv', 'wc', 'rc']
    for col in numeric_object_cols:
        if col in df.columns:
            # Convert to numeric, force invalid parsing (like '?', '\t?') to NaN
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    print("Data cleaning complete. Target class distribution:")
    print(df['target'].value_counts(dropna=False))
    
    return df

def build_preprocessing_pipeline(numerical_cols, categorical_cols):
    # Numerical Preprocessing: Imputation (Median) + Scaling
    numerical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    # Categorical Preprocessing: Imputation (Most Frequent) + OneHotEncoding
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(drop='first', handle_unknown='ignore'))
    ])
    
    # Combine transformers
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numerical_transformer, numerical_cols),
            ('cat', categorical_transformer, categorical_cols)
        ]
    )
    
    return preprocessor

def train_and_evaluate_models(X_train, X_test, y_train, y_test, preprocessor):
    models = {
        'Decision Tree': DecisionTreeClassifier(random_state=42),
        'Random Forest': RandomForestClassifier(random_state=42, n_estimators=100),
        'K-Nearest Neighbors': KNeighborsClassifier(),
        'Support Vector Machine': SVC(probability=True, random_state=42),
        'XGBoost': XGBClassifier(random_state=42, eval_metric='logloss'),
        'LightGBM': LGBMClassifier(random_state=42, verbose=-1)
    }
    
    results = {}
    
    for name, clf in models.items():
        print(f"\nTraining {name}...")
        
        # Create pipeline
        pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('classifier', clf)
        ])
        
        # Train model
        pipeline.fit(X_train, y_train)
        
        # Predict
        y_pred = pipeline.predict(X_test)
        y_prob = pipeline.predict_proba(X_test)[:, 1]
        
        # Evaluate
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_prob)
        
        print(f"Accuracy: {acc:.4f} | Precision: {prec:.4f} | Recall: {rec:.4f} | F1: {f1:.4f} | AUC: {auc:.4f}")
        
        results[name] = {
            'pipeline': pipeline,
            'metrics': {
                'accuracy': acc,
                'precision': prec,
                'recall': rec,
                'f1_score': f1,
                'auc': auc
            }
        }
        
    return results

def main():
    dataset_path = "c:/Users/Arjun/CKD/dataset/kidney_disease.csv"
    df = load_and_clean_data(dataset_path)
    
    # Define columns
    target_col = 'target'
    X = df.drop(columns=[target_col])
    y = df[target_col]
    
    # Identify numerical and categorical columns
    numerical_cols = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_cols = X.select_dtypes(include=['object']).columns.tolist()
    
    print("\nNumerical features:", numerical_cols)
    print("Categorical features:", categorical_cols)
    
    # Train-test split (80-20 stratified split to preserve class ratios)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    
    print(f"\nTrain set shape: {X_train.shape}, Test set shape: {X_test.shape}")
    
    # Build preprocessor
    preprocessor = build_preprocessing_pipeline(numerical_cols, categorical_cols)
    
    # Train and compare models
    model_results = train_and_evaluate_models(X_train, X_test, y_train, y_test, preprocessor)
    
    # Pick the best model based on F1 Score
    best_model_name = None
    best_f1 = -1
    best_pipeline = None
    
    for name, res in model_results.items():
        f1 = res['metrics']['f1_score']
        if f1 > best_f1:
            best_f1 = f1
            best_model_name = name
            best_pipeline = res['pipeline']
            
    print(f"\nBest Model selected: {best_model_name} with F1-Score: {best_f1:.4f}")
    
    # Save the best pipeline (preprocessor + classifier)
    # joblib handles serialization of composite scikit-learn pipelines perfectly
    os.makedirs("c:/Users/Arjun/CKD/ckd_backend/api/ml", exist_ok=True)
    model_save_path = "c:/Users/Arjun/CKD/ckd_backend/api/ml/ckd_model_pipeline.joblib"
    joblib.dump(best_pipeline, model_save_path)
    print(f"Saved best model pipeline to: {model_save_path}")
    
    # Save column lists for inference validation
    metadata = {
        'numerical_cols': numerical_cols,
        'categorical_cols': categorical_cols,
        'features': X.columns.tolist()
    }
    joblib.dump(metadata, "c:/Users/Arjun/CKD/ckd_backend/api/ml/model_metadata.joblib")
    print("Saved feature metadata.")

if __name__ == "__main__":
    main()
