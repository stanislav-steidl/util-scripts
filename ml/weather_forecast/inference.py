import torch
import pandas as pd
import joblib
import matplotlib.pyplot as plt
from ml.weather_forecast.model import WeatherNet  # definice sítě

MODEL_PATH = "best_model.pt"
SCALER_PATH = "scaler.pkl"
FEATURES_PATH = "features.pkl"


def load_artifacts():
    scaler = joblib.load(SCALER_PATH)
    features = joblib.load(FEATURES_PATH)
    return scaler, features


def prepare_input(city: str, month: int, features):
    df_input = pd.DataFrame([[city, month]], columns=["city", "month"])
    X_input = pd.get_dummies(df_input, columns=["city"], drop_first=True)

    for col in features:
        if col not in X_input.columns:
            X_input[col] = 0

    X_input = X_input[features]
    return X_input


def predict_year(city: str):
    """Vrátí predikované teploty pro všech 12 měsíců."""
    scaler, features = load_artifacts()
    predictions = []

    # Načteme model jen jednou
    model = WeatherNet(input_dim=len(features))
    model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    model.eval()

    for month in range(1, 13):
        X_input = prepare_input(city, month, features)
        X_scaled = scaler.transform(X_input)
        X_tensor = torch.tensor(X_scaled, dtype=torch.float32)

        with torch.no_grad():
            pred = model(X_tensor).numpy().flatten()[0]
            predictions.append(round(pred, 2))

    return predictions


def plot_predictions(city: str, predictions: list):
    months = list(range(1, 13))
    plt.figure(figsize=(10, 5))
    plt.plot(months, predictions, marker='o')
    plt.xticks(months)
    plt.xlabel("Měsíc")
    plt.ylabel("Predikovaná teplota (°C)")
    plt.title(f"Predikce teplot pro {city} za rok")
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    city = input("Zadejte město: ").strip()
    preds = predict_year(city)
    print(f"Odhadované teploty pro {city}:")
    for month, temp in enumerate(preds, start=1):
        print(f"Měsíc {month}: {temp} °C")

    plot_predictions(city, preds)
