import pandas as pd
from sklearn.model_selection import train_test_split

def load_weather_data(csv_path: str):
    """
    Načte dataset počasí, provede základní feature engineering a rozdělí data
    na trénovací, validační a testovací sady.

    Args:
        csv_path (str): cesta k CSV souboru s daty

    Returns:
        X_train, X_val, X_test, y_train, y_val, y_test (tuple)
    """
    # Načtení dat
    df = pd.read_csv(csv_path)

    # Feature engineering
    df['month'] = pd.to_datetime(df['date']).dt.month
    X = pd.get_dummies(df[['city', 'month']], drop_first=True)
    y = df['temperature']

    # Rozdělení na train / temp (80 % train, 20 % temp)
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Rozdělení temp na val / test (50:50 -> 10 % val, 10 % test celkem)
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.5, random_state=42
    )

    return X_train, X_val, X_test, y_train, y_val, y_test


# --- Příklad použití ---
if __name__ == "__main__":
    X_train, X_val, X_test, y_train, y_val, y_test = load_weather_data(
        "ml/weather_forecast/weather_dataset_large.csv"
    )
    print(f"Train samples: {len(X_train)}, Validation samples: {len(X_val)}, Test samples: {len(X_test)}")
