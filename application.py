import os
import pickle
import warnings
import numpy as np
from flask import Flask, request, render_template, redirect, url_for

# Suppress cosmetic unpickle version and feature name warnings for clean production logs
warnings.filterwarnings("ignore")

# Determine base directory anchored to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Flask application instance (both 'application' for AWS Elastic Beanstalk and 'app' for Vercel)
application = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)
app = application

# Load model and scaler using absolute path relative to this file
RIDGE_MODEL_PATH = os.path.join(BASE_DIR, "models", "ridge.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "models", "scaler.pkl")

with open(RIDGE_MODEL_PATH, "rb") as f:
    ridge_regression = pickle.load(f)

with open(SCALER_PATH, "rb") as f:
    standard_scaler = pickle.load(f)

# The 9 expected features in exact order required by the scaler and ridge model
FEATURE_CONFIG = [
    {"name": "Temperature", "label": "Temperature", "unit": "°C", "min": -20.0, "max": 60.0},
    {"name": "RH", "label": "Relative Humidity", "unit": "%", "min": 0.0, "max": 100.0},
    {"name": "Ws", "label": "Wind Speed", "unit": "km/h", "min": 0.0, "max": 120.0},
    {"name": "Rain", "label": "Rainfall", "unit": "mm", "min": 0.0, "max": 300.0},
    {"name": "FFMC", "label": "Fine Fuel Moisture Code", "unit": "index", "min": 0.0, "max": 105.0},
    {"name": "DMC", "label": "Duff Moisture Code", "unit": "index", "min": 0.0, "max": 500.0},
    {"name": "ISI", "label": "Initial Spread Index", "unit": "index", "min": 0.0, "max": 150.0},
    {"name": "Classes", "label": "Fire Classification", "unit": "class", "min": 0.0, "max": 1.0},
    {"name": "Region", "label": "Region", "unit": "region", "min": 0.0, "max": 1.0},
]


def interpret_fwi(fwi_value):
    """
    Informational UI interpretation based on standard Canadian Forest Fire Weather Index (FWI) ranges.
    This provides user-facing context and does not alter the underlying model prediction.
    """
    if fwi_value < 5.2:
        return {
            "level": "Low",
            "badge_class": "risk-low",
            "color": "#10b981",
            "description": "Fires are unlikely to start or spread quickly. Routine vigilance is recommended.",
        }
    elif fwi_value < 11.2:
        return {
            "level": "Moderate",
            "badge_class": "risk-moderate",
            "color": "#38bdf8",
            "description": "Surface fires may ignite in cured fuels. Spread rate remains moderate.",
        }
    elif fwi_value < 21.3:
        return {
            "level": "High",
            "badge_class": "risk-high",
            "color": "#f59e0b",
            "description": "Fires start readily and may spread rapidly. Heightened fire alert advised.",
        }
    else:
        return {
            "level": "Very High / Extreme",
            "badge_class": "risk-very-high",
            "color": "#ef4444",
            "description": "High-intensity wildfire behavior potential with fast rate of spread and challenging containment.",
        }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["GET", "POST"])
def predict():
    if request.method == "POST":
        form_data = request.form
        errors = []
        parsed_values = []

        # Validate each of the 9 required features in exact order
        for feat in FEATURE_CONFIG:
            field_name = feat["name"]
            val_raw = form_data.get(field_name)

            if val_raw is None or val_raw.strip() == "":
                errors.append(f"Missing required field: {feat['label']} ({field_name}).")
                continue

            try:
                val_float = float(val_raw)
            except (ValueError, TypeError):
                errors.append(f"Invalid numeric value for {feat['label']}: '{val_raw}'.")
                continue

            if val_float < feat["min"] or val_float > feat["max"]:
                errors.append(
                    f"{feat['label']} value ({val_float}) is outside allowable range "
                    f"[{feat['min']} to {feat['max']}]."
                )
                continue

            parsed_values.append(val_float)

        # If any validation errors exist, render index.html with clean error messages
        if errors:
            return (
                render_template(
                    "index.html",
                    error="; ".join(errors),
                    form_data=form_data,
                ),
                400,
            )

        # Extract features preserving exact model input order:
        # [Temperature, RH, Ws, Rain, FFMC, DMC, ISI, Classes, Region]
        Temperature = parsed_values[0]
        RH = parsed_values[1]
        Ws = parsed_values[2]
        Rain = parsed_values[3]
        FFMC = parsed_values[4]
        DMC = parsed_values[5]
        ISI = parsed_values[6]
        Classes = parsed_values[7]
        Region = parsed_values[8]

        # Apply the existing StandardScaler and Ridge Regression model
        new_data_scaled = standard_scaler.transform(
            [[Temperature, RH, Ws, Rain, FFMC, DMC, ISI, Classes, Region]]
        )

        result = ridge_regression.predict(new_data_scaled)
        raw_fwi = float(result[0])
        formatted_fwi = round(raw_fwi, 2)
        risk_info = interpret_fwi(raw_fwi)

        # Summary of inputs for display on the result page
        inputs_summary = {
            "Temperature": f"{Temperature:.1f} °C",
            "RH": f"{RH:.1f} %",
            "Ws": f"{Ws:.1f} km/h",
            "Rain": f"{Rain:.2f} mm",
            "FFMC": f"{FFMC:.1f}",
            "DMC": f"{DMC:.1f}",
            "ISI": f"{ISI:.1f}",
            "Classes": "Fire (1)" if int(Classes) == 1 else "Not Fire (0)",
            "Region": "Sidi-Bel Abbes (1)" if int(Region) == 1 else "Bejaia (0)",
        }

        # Keep 'results' argument for complete backwards compatibility with templates
        return render_template(
            "predict.html",
            results=formatted_fwi,
            raw_fwi=raw_fwi,
            risk=risk_info,
            inputs=inputs_summary,
        )

    else:
        return render_template("index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)