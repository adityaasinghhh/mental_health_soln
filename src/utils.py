import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import numpy as np

def plot_model_comparison(results_sorted):
    """Plot accuracy comparison of models"""
    model_names = [r['name'] for r in results_sorted]
    accuracies = [r['accuracy'] for r in results_sorted]
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(model_names, accuracies)
    plt.xticks(rotation=45, ha='right')
    plt.title("Model Accuracy Comparison", fontsize=14)
    plt.xlabel("Models")
    plt.ylabel("Accuracy")
    
    # Add value labels on bars
    for bar, acc in zip(bars, accuracies):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005, 
                f'{acc:.3f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.show()

def plot_confusion_matrix(model, X_test, y_test, model_name, labels=None):
    """Plot confusion matrix"""
    y_pred = model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)
    
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
    disp.plot(cmap='Blues')
    plt.title(f"Confusion Matrix - {model_name}")
    plt.tight_layout()
    plt.show()

def plot_class_distribution(y_train):
    """Plot class distribution"""
    labels, counts = np.unique(y_train, return_counts=True)
    
    plt.figure(figsize=(10, 6))
    plt.bar(range(len(labels)), counts)
    plt.xticks(range(len(labels)), labels)
    plt.title("Class Distribution in Training Set")
    plt.xlabel("Classes")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.show()

def calculate_combined_severity(psychometric_scores, nlp_score):
    """Calculate combined severity score"""
    psychometric_total = sum(psychometric_scores.values())
    psychometric_percent = (psychometric_total / 80) * 100
    
    # Convert NLP score (-1 to +1) to percentage (0-100)
    if nlp_score < 0:
        nlp_severity_percent = abs(nlp_score) * 100
    else:
        nlp_severity_percent = 0
    
    # Combined score (60% psychometric, 40% NLP)
    combined_severity = (psychometric_percent * 0.6) + (nlp_severity_percent * 0.4)
    
    # Determine combined status
    if combined_severity < 40:
        combined_status = "Normal"
    elif combined_severity < 55:
        combined_status = "Mild"
    elif combined_severity < 70:
        combined_status = "Moderate"
    else:
        combined_status = "Severe"
    
    return combined_status, psychometric_percent, nlp_severity_percent