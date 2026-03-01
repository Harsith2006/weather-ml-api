from flask import Flask, request, jsonify
import joblib
import pandas as pd

app = Flask(__name__)

# ==============================
# Load Trained ML Model
# ==============================
model = joblib.load("rain_model.pkl")

# ==============================
# Store Last 50 Readings
# ==============================
data_log = []


# ==============================
# Home Route
# ==============================
@app.route("/")
def home():
    return "Weather ML API is Running 🚀"


# ==============================
# Prediction Route
# ==============================
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        temperature = float(data["temperature"])
        humidity = float(data["humidity"])

        # Create DataFrame for model
        input_data = pd.DataFrame(
            [[temperature, humidity]],
            columns=["temperature", "humidity"]
        )

        # ML Prediction
        prediction = model.predict(input_data)[0]
        result = "Rain Likely" if prediction == 1 else "Sunny"

        # Store Data in Memory
        data_log.append({
            "temperature": temperature,
            "humidity": humidity,
            "prediction": result
        })

        # Keep Only Last 50 Entries
        if len(data_log) > 50:
            data_log.pop(0)

        return jsonify({
            "temperature": temperature,
            "humidity": humidity,
            "prediction": result
        })

    except Exception as e:
        return jsonify({"error": str(e)})


# ==============================
# Data Endpoint (For Graph)
# ==============================
@app.route("/data")
def get_data():
    return jsonify(data_log)


# ==============================
# Dashboard Route (Live Graph)
# ==============================
@app.route("/dashboard")
def dashboard():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Live Weather Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
        <h2>Real-Time Temperature & Humidity</h2>
        <canvas id="chart" width="600" height="300"></canvas>

        <script>
            const ctx = document.getElementById('chart').getContext('2d');

            const chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        {
                            label: 'Temperature (°C)',
                            data: [],
                            borderColor: 'red',
                            fill: false
                        },
                        {
                            label: 'Humidity (%)',
                            data: [],
                            borderColor: 'blue',
                            fill: false
                        }
                    ]
                },
                options: {
                    responsive: true
                }
            });

            async function fetchData() {
                const response = await fetch('/data');
                const data = await response.json();

                chart.data.labels = data.map((_, index) => index + 1);
                chart.data.datasets[0].data = data.map(d => d.temperature);
                chart.data.datasets[1].data = data.map(d => d.humidity);

                chart.update();
            }

            setInterval(fetchData, 5000);
        </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)