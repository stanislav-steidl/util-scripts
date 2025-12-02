import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import root_mean_squared_error

from ml.weather_forecast.load_weather_data import load_weather_data  # náš předchozí skript s funkcí load_weather_data
import joblib



# --- Definice jednoduché sítě ---
class WeatherNet(nn.Module):
    def __init__(self, input_dim: int):
        super(WeatherNet, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(input_dim, 2024),
            nn.Tanh(),
            nn.Linear(2024, 1)
        )

    def forward(self, x):
        return self.model(x)


def train_model(
    model,
    train_loader,
    val_loader,
    epochs=50,
    lr=1e-3,
    device="cpu",
    early_stopping=True,
    patience=5,
):
    """
    Trénuje model na datech.
    
    Args:
        model (nn.Module): PyTorch model
        train_loader (DataLoader): trénovací data
        val_loader (DataLoader): validační data
        epochs (int): počet epoch
        lr (float): learning rate
        device (str): "cpu" nebo "cuda"
        early_stopping (bool): jestli použít early stopping
        patience (int): počet epoch, po kterých se trénink zastaví,
                        pokud se nelepší validační loss
    """
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    model.to(device)
    best_val_loss = float("inf")
    patience_counter = 0

    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        for xb, yb in train_loader:
            xb, yb = xb.to(device), yb.to(device)
            optimizer.zero_grad()
            outputs = model(xb)
            loss = criterion(outputs, yb)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()

        # Validace
        model.eval()
        val_losses = []
        with torch.no_grad():
            for xb, yb in val_loader:
                xb, yb = xb.to(device), yb.to(device)
                outputs = model(xb)
                val_loss = criterion(outputs, yb)
                val_losses.append(val_loss.item())

        avg_train_loss = running_loss / len(train_loader)
        avg_val_loss = np.mean(val_losses)

        # Uložení nejlepšího modelu
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            torch.save(model.state_dict(), "best_model.pt")
            patience_counter = 0
        else:
            patience_counter += 1

        print(
            f"Epoch [{epoch+1}/{epochs}] Train Loss: {avg_train_loss:.4f} | Val Loss: {avg_val_loss:.4f}"
        )

        # Early stopping
        if early_stopping and patience_counter >= patience:
            print(f"⏹ Early stopping triggered after {epoch+1} epochs.")
            break

    print("Training complete. Best val loss:", best_val_loss)



if __name__ == "__main__":
    # --- Načtení dat ---
    X_train, X_val, X_test, y_train, y_val, y_test = load_weather_data("ml/weather_forecast/weather_dataset_large.csv")

    features = list(X_train.columns)  # X_train je ještě DataFrame, před scaler.transform()
    joblib.dump(features, "features.pkl")
    # --- Normalizace vstupů ---
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_val = scaler.transform(X_val)
    X_test = scaler.transform(X_test)
    joblib.dump(scaler, "scaler.pkl")

    # --- Konverze na tensory ---
    X_train_t = torch.tensor(X_train, dtype=torch.float32)
    y_train_t = torch.tensor(y_train.values, dtype=torch.float32).unsqueeze(1)
    X_val_t = torch.tensor(X_val, dtype=torch.float32)
    y_val_t = torch.tensor(y_val.values, dtype=torch.float32).unsqueeze(1)
    X_test_t = torch.tensor(X_test, dtype=torch.float32)
    y_test_t = torch.tensor(y_test.values, dtype=torch.float32).unsqueeze(1)

    # --- DataLoadery ---
    train_loader = DataLoader(TensorDataset(X_train_t, y_train_t), batch_size=32, shuffle=True)
    val_loader = DataLoader(TensorDataset(X_val_t, y_val_t), batch_size=32)

    # --- Model ---
    model = WeatherNet(input_dim=X_train.shape[1])


    train_model(
    model,
    train_loader,
    val_loader,
    epochs=5000,
    lr=1e-3,
    early_stopping=True,  # 🔧 nebo False pokud ho nechceš
    patience=500            # třeba delší patience
    )



    # train_model(model, train_loader, val_loader, epochs=50, lr=1e-3)

    # --- Testování nejlepšího modelu ---
    model.load_state_dict(torch.load("best_model.pt"))
    model.eval()
    with torch.no_grad():
        y_pred = model(X_test_t).numpy()
        rmse = root_mean_squared_error(y_test, y_pred)
        print(f"Test RMSE: {rmse:.2f} °C")
