"""
Automated Test Suite for Forest Weather Index (FWI) Prediction Application
Verifies ML pipeline preservation, Flask endpoints, input validation, and static assets.
"""

import os
import unittest
import pickle
import numpy as np
from application import app, application, standard_scaler, ridge_regression, FEATURE_CONFIG


class TestFWIApplication(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    # -------------------------------------------------------------
    # 1. Model & Scaler Integrity Tests
    # -------------------------------------------------------------
    def test_model_and_scaler_loaded(self):
        """Verify model and scaler are loaded and feature dimensions match exactly 9 features."""
        self.assertIsNotNone(ridge_regression, "Ridge regression model should not be None")
        self.assertIsNotNone(standard_scaler, "Standard scaler should not be None")
        self.assertEqual(standard_scaler.n_features_in_, 9, "Scaler must expect exactly 9 features")
        self.assertEqual(ridge_regression.n_features_in_, 9, "Ridge model must expect exactly 9 features")

        expected_order = ['Temperature', 'RH', 'Ws', 'Rain', 'FFMC', 'DMC', 'ISI', 'Classes', 'Region']
        if hasattr(standard_scaler, 'feature_names_in_'):
            self.assertEqual(list(standard_scaler.feature_names_in_), expected_order)

    def test_pipeline_transformation_and_prediction(self):
        """Verify exact mathematical execution of scaler transform followed by ridge predict."""
        sample_input = [[32.0, 60.0, 15.0, 0.0, 85.0, 15.0, 5.0, 1.0, 0.0]]
        scaled = standard_scaler.transform(sample_input)
        pred = ridge_regression.predict(scaled)
        self.assertEqual(len(pred), 1)
        self.assertIsInstance(float(pred[0]), float)
        # Expected prediction for this input is approx 7.84
        self.assertAlmostEqual(float(pred[0]), 7.8424, places=2)

    # -------------------------------------------------------------
    # 2. Flask Route Tests: GET /
    # -------------------------------------------------------------
    def test_get_index(self):
        """GET / should render index.html with status code 200 and all 9 inputs."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)

        self.assertIn("FWI", html)
        self.assertIn("Predict Forest Weather Index", html)
        self.assertIn('action="/predict"', html)

        # Verify all 9 input field names are present
        for feat in FEATURE_CONFIG:
            self.assertIn(f'name="{feat["name"]}"', html, f"Field {feat['name']} must be in form")

    # -------------------------------------------------------------
    # 3. Flask Route Tests: GET /predict
    # -------------------------------------------------------------
    def test_get_predict_renders_index(self):
        """GET /predict should safely return index.html without errors."""
        response = self.client.get("/predict")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("FWI", html)
        self.assertIn("Environmental Conditions", html)

    # -------------------------------------------------------------
    # 4. Flask Route Tests: POST /predict with Valid Input
    # -------------------------------------------------------------
    def test_post_predict_valid_sample(self):
        """POST /predict with valid values returns 200 and renders predict.html with results."""
        payload = {
            "Temperature": "32.0",
            "RH": "60.0",
            "Ws": "15.0",
            "Rain": "0.0",
            "FFMC": "85.0",
            "DMC": "15.0",
            "ISI": "5.0",
            "Classes": "1",
            "Region": "0",
        }
        response = self.client.post("/predict", data=payload)
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)

        self.assertIn("Predicted Forest Weather Index", html)
        self.assertIn("7.84", html)
        self.assertIn("Moderate Fire Danger", html)
        self.assertIn("Model Input Parameters", html)
        self.assertIn("Make Another Prediction", html)

    def test_post_predict_high_risk_sample(self):
        """POST /predict with high risk values returns 200 and high danger level."""
        payload = {
            "Temperature": "38.0",
            "RH": "35.0",
            "Ws": "19.0",
            "Rain": "0.0",
            "FFMC": "89.5",
            "DMC": "26.0",
            "ISI": "9.8",
            "Classes": "1",
            "Region": "1",
        }
        response = self.client.post("/predict", data=payload)
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Predicted Forest Weather Index", html)
        self.assertIn("Fire Danger", html)

    # -------------------------------------------------------------
    # 5. Input Validation & Error Handling Tests
    # -------------------------------------------------------------
    def test_post_predict_missing_field(self):
        """POST /predict with a missing field returns status 400 with clean error."""
        payload = {
            # Temperature omitted
            "RH": "60.0",
            "Ws": "15.0",
            "Rain": "0.0",
            "FFMC": "85.0",
            "DMC": "15.0",
            "ISI": "5.0",
            "Classes": "1",
            "Region": "0",
        }
        response = self.client.post("/predict", data=payload)
        self.assertEqual(response.status_code, 400)
        html = response.get_data(as_text=True)
        self.assertIn("Input Error", html)
        self.assertIn("Missing required field: Temperature", html)

    def test_post_predict_invalid_numeric(self):
        """POST /predict with non-numeric text returns status 400 without traceback."""
        payload = {
            "Temperature": "not_a_number",
            "RH": "60.0",
            "Ws": "15.0",
            "Rain": "0.0",
            "FFMC": "85.0",
            "DMC": "15.0",
            "ISI": "5.0",
            "Classes": "1",
            "Region": "0",
        }
        response = self.client.post("/predict", data=payload)
        self.assertEqual(response.status_code, 400)
        html = response.get_data(as_text=True)
        self.assertIn("Input Error", html)
        self.assertIn("Invalid numeric value for Temperature", html)

    def test_post_predict_out_of_range(self):
        """POST /predict with out-of-range value returns status 400 with range hint."""
        payload = {
            "Temperature": "32.0",
            "RH": "150.0",  # Max allowable is 100
            "Ws": "15.0",
            "Rain": "0.0",
            "FFMC": "85.0",
            "DMC": "15.0",
            "ISI": "5.0",
            "Classes": "1",
            "Region": "0",
        }
        response = self.client.post("/predict", data=payload)
        self.assertEqual(response.status_code, 400)
        html = response.get_data(as_text=True)
        self.assertIn("Input Error", html)
        self.assertIn("outside allowable range", html)

    # -------------------------------------------------------------
    # 6. Static Asset Tests
    # -------------------------------------------------------------
    def test_static_css_exists_and_loads(self):
        """Verify static CSS stylesheet loads successfully."""
        response = self.client.get("/static/css/style.css")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Forest Weather Index", response.get_data(as_text=True))

    def test_static_js_exists_and_loads(self):
        """Verify static JavaScript script loads successfully."""
        response = self.client.get("/static/js/script.js")
        self.assertEqual(response.status_code, 200)
        self.assertIn("loadPreset", response.get_data(as_text=True))

    # -------------------------------------------------------------
    # 7. AWS Elastic Beanstalk WSGI Compatibility
    # -------------------------------------------------------------
    def test_wsgi_callable_application(self):
        """AWS Elastic Beanstalk expects a WSGI callable named 'application'."""
        self.assertTrue(callable(application), "'application' must be a callable WSGI instance")
        self.assertIs(app, application, "'app' and 'application' should reference the same instance")


if __name__ == "__main__":
    unittest.main()
