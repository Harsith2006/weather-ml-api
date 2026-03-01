from flask import Flask, request, jsonify
import joblib
import pandas as pd

app = Flask(__name__)

# Load trained model
model = joblib.load("rain_model.pkl")

@app.route("/")
def home():
    return "Weather ML API is Running 🚀"

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        temperature = float(data["temperature"])
        humidity = float(data["humidity"])

        input_data = pd.DataFrame(
            [[temperature, humidity]],
            columns=["temperature", "humidity"]
        )

        prediction = model.predict(input_data)[0]

        result = "Rain Likely" if prediction == 1 else "Sunny"

        return jsonify({
            "temperature": temperature,
            "humidity": humidity,
            "prediction": result
        })

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)