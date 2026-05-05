import numpy as np
import time
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from xgboost import XGBClassifier
from scipy.sparse import issparse
import joblib
import os

def get_models():
    """Define the models to train"""
    return {
        'Logistic Regression': LogisticRegression(max_iter=500, random_state=42),
        'Multinomial NB': MultinomialNB(),
        'Linear SVM': LinearSVC(max_iter=2000, random_state=42, dual='auto'),
        'Random Forest': RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1),
        'XGBoost': XGBClassifier(n_estimators=50, random_state=42, eval_metric='mlogloss')
    }

def train_and_evaluate_models(X_train, y_train, X_test, y_test, sample_size=None):
    """Train and evaluate all models"""
    results = []
    
    # Sample data if needed for faster training
    if sample_size and sample_size < X_train.shape[0]:
        indices = np.random.choice(X_train.shape[0], sample_size, replace=False)
        X_train_sample = X_train[indices]
        y_train_sample = y_train[indices]
        X_test_sample = X_test[:3000]
        y_test_sample = y_test[:3000]
        print(f"Using sample: {sample_size} training samples, 3000 test samples")
    else:
        X_train_sample = X_train
        y_train_sample = y_train
        X_test_sample = X_test
        y_test_sample = y_test
    
    models = get_models()
    
    print("\n" + "="*70)
    print("MODEL EVALUATION (ALL MODELS)")
    print("="*70)
    
    for name, model in models.items():
        print(f"\nTraining: {name}")
        start_time = time.time()
        
        try:
            # Handle different model requirements
            if name == "Multinomial NB" and issparse(X_train_sample):
                # Convert to dense for Naive Bayes
                X_train_dense = X_train_sample.toarray()
                X_test_dense = X_test_sample.toarray()
                model.fit(X_train_dense, y_train_sample)
                y_pred = model.predict(X_test_dense)
            elif name in ["Linear SVM", "Logistic Regression"] and issparse(X_train_sample):
                # These work with sparse matrices
                model.fit(X_train_sample, y_train_sample)
                y_pred = model.predict(X_test_sample)
            else:
                model.fit(X_train_sample, y_train_sample)
                y_pred = model.predict(X_test_sample)
            
            # Calculate metrics
            acc = accuracy_score(y_test_sample, y_pred)
            f1 = f1_score(y_test_sample, y_pred, average='weighted')
            
            training_time = time.time() - start_time
            
            results.append({
                'name': name,
                'model': model,
                'accuracy': acc,
                'f1_score': f1,
                'training_time': training_time
            })
            
            print(f"  Accuracy: {acc:.4f}")
            print(f"  F1 Score: {f1:.4f}")
            print(f"  Time: {training_time:.2f}s")
            
        except Exception as e:
            print(f"  Failed: {str(e)[:100]}")
    
    # Sort by accuracy
    results_sorted = sorted(results, key=lambda x: x['accuracy'], reverse=True)
    
    print("\n" + "="*70)
    print("FINAL RANKING")
    print("="*70)
    
    for rank, result in enumerate(results_sorted, 1):
        print(f"\n{rank}. {result['name']}")
        print(f"   Accuracy: {result['accuracy']:.4f}")
        print(f"   F1 Score: {result['f1_score']:.4f}")
    
    best_model = results_sorted[0]
    print("\n" + "="*70)
    print("BEST MODEL")
    print("="*70)
    print(f"Model: {best_model['name']}")
    print(f"Accuracy: {best_model['accuracy']:.4f}")
    print(f"F1 Score: {best_model['f1_score']:.4f}")
    
    return best_model, results_sorted

def save_model(model, model_name, save_dir='models/'):
    """Save the trained model"""
    os.makedirs(save_dir, exist_ok=True)
    joblib.dump(model, f'{save_dir}/best_model.pkl')
    print(f"Model saved to {save_dir}/best_model.pkl")

def load_model(model_path='models/best_model.pkl'):
    """Load a saved model"""
    return joblib.load(model_path)