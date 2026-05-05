@echo off
echo Setting up Mental Health Prediction System...

:: Create virtual environment
python -m venv venv
call venv\Scripts\activate.bat

:: Install requirements
pip install -r requirements.txt

:: Run the application
python app.py --mode predict