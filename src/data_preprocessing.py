import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder, StandardScaler
from scipy.sparse import hstack
from imblearn.over_sampling import SMOTE
import joblib
import os

def load_data(file_path):
    """Load the mental health dataset"""
    df = pd.read_csv(file_path)
    print(f"File loaded successfully. Shape: {df.shape}")
    return df

def extract_text_features(text):
    """Extract additional features from text"""
    text = str(text)
    return {
        'text_length': len(text),
        'word_count': len(text.split()),
        'avg_word_len': len(text) / max(len(text.split()), 1),
        'exclamation_count': text.count('!'),
        'question_count': text.count('?'),
        'capital_ratio': sum(1 for c in text if c.isupper()) / max(len(text), 1)
    }

def prepare_features(df, text_column='text', label_column='status'):
    """Prepare features and labels for training"""
    X = df[text_column]
    y = df[label_column]
    
    # Encode labels
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    # Print label mapping
    print("\nLabel Encoding:")
    for i, label in enumerate(le.classes_):
        print(f"  {label} -> {i}")
    
    # TF-IDF Vectorization
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        stop_words='english',
        sublinear_tf=True
    )
    X_tfidf = vectorizer.fit_transform(X)
    print(f"TF-IDF features: {X_tfidf.shape}")
    
    # Extract text features
    text_features = df['text'].apply(extract_text_features).apply(pd.Series)
    
    # Scale numeric features
    scaler = StandardScaler()
    X_numeric = scaler.fit_transform(text_features)
    print(f"Numeric features: {X_numeric.shape}")
    
    # Combine features
    X_combined = hstack([X_tfidf, X_numeric])
    print(f"Combined features: {X_combined.shape}")
    
    return X_combined, y_encoded, le, vectorizer, scaler

def split_and_balance_data(X, y, test_size=0.2, random_state=42):
    """Split data and handle class imbalance"""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    print(f"\nTraining set: {X_train.shape[0]:,} samples")
    print(f"Test set: {X_test.shape[0]:,} samples")
    
    # Check class imbalance
    class_counts = pd.Series(y_train).value_counts()
    imbalance_ratio = class_counts.max() / class_counts.min()
    print(f"Imbalance Ratio: {imbalance_ratio:.2f}:1")
    
    # Apply SMOTE if needed
    if imbalance_ratio > 1.5:
        print("Applying SMOTE for class balancing...")
        smote = SMOTE(random_state=random_state)
        X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)
        print(f"Balanced training set: {X_train_balanced.shape[0]:,} samples")
    else:
        print("Class imbalance is minimal. Using original training set.")
        X_train_balanced, y_train_balanced = X_train, y_train
    
    return X_train_balanced, X_test, y_train_balanced, y_test

def save_preprocessing_artifacts(vectorizer, scaler, label_encoder, save_dir='models/'):
    """Save preprocessing objects for later use"""
    os.makedirs(save_dir, exist_ok=True)
    joblib.dump(vectorizer, f'{save_dir}/vectorizer.pkl')
    joblib.dump(scaler, f'{save_dir}/scaler.pkl')
    joblib.dump(label_encoder, f'{save_dir}/label_encoder.pkl')
    print(f"Preprocessing artifacts saved to {save_dir}")