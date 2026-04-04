import pandas as pd
import numpy as np
import lightgbm as lgb
import mlflow
import mlflow.lightgbm
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error

# 1. Generate Synthetic Training Data (500 days of workouts)
np.random.seed(42)
data_size = 500
hours_slept = np.random.normal(7, 1.5, data_size)
rpe = np.random.uniform(4, 10, data_size) # Rate of Perceived Exertion (1-10)
workout_duration = np.random.uniform(30, 120, data_size) # In minutes
calories_consumed = np.random.normal(2500, 300, data_size)

# The Target: Readiness Score (0-100%). Higher sleep = higher readiness. High RPE = lower readiness.
readiness_score = (hours_slept * 10) - (rpe * 3) - (workout_duration * 0.1) + (calories_consumed * 0.005)
readiness_score = np.clip(readiness_score, 0, 100) # Keep between 0 and 100

df = pd.DataFrame({
    'hours_slept': hours_slept,
    'rpe': rpe,
    'workout_duration': workout_duration,
    'calories_consumed': calories_consumed,
    'readiness_score': readiness_score
})

X = df.drop('readiness_score', axis=1)
y = df['readiness_score']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 2. Configure MLflow Tracking
mlflow.set_tracking_uri("sqlite:///mlruns.db")
mlflow.set_experiment("Aura_AI_Fatigue_Forecaster")

# 3. Train LightGBM & Log Experiment
print("Starting Aura AI Training Protocol...")
with mlflow.start_run(run_name="LGBM_Baseline"):
    # Enable automatic logging of parameters and metrics
    mlflow.lightgbm.autolog()
    
    # Define model parameters
    params = {
        "objective": "regression",
        "metric": "rmse",
        "learning_rate": 0.05,
        "max_depth": 5,
        "n_estimators": 100
    }
    
    # Train the model
    model = lgb.LGBMRegressor(**params)
    model.fit(X_train, y_train, eval_set=[(X_test, y_test)])
    
    # Evaluate
    predictions = model.predict(X_test)
    mse = mean_squared_error(y_test, predictions)
    mae = mean_absolute_error(y_test, predictions)
    
    print(f"Model Training Complete.")
    print(f"Mean Absolute Error (Readiness Score diff): {mae:.2f}%")
    print(f"To view the MLOps Dashboard, run: mlflow ui --backend-store-uri sqlite:///mlruns.db")

    # Save a test prediction for a user who slept 5 hours and trained hard
    test_user = pd.DataFrame([[5.0, 9.0, 90.0, 2200]], columns=X.columns)
    pred_readiness = model.predict(test_user)[0]
    print(f"\n--- INFERENCE TEST ---")
    print(f"User State: 5hrs sleep, High Exertion (9/10), 90min workout, 2200cals")
    print(f"Aura AI Predicted Readiness: {pred_readiness:.2f}%")
