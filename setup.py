from setuptools import setup, find_packages

setup(
    name="mental_health_prediction",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "scikit-learn>=1.3.0",
        "xgboost>=1.7.0",
        "textblob>=0.17.0",
        "vaderSentiment>=3.3.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
        "joblib>=1.3.0",
        "imbalanced-learn>=0.11.0",
    ],
    author="Your Name",
    description="Mental Health Prediction using Machine Learning",
)