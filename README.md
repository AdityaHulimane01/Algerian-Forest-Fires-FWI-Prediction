# 🔥 Forest Weather Index (FWI) Prediction System

A production-ready Machine Learning web application deployed on **AWS Elastic Beanstalk** that predicts the **Forest Weather Index (FWI)** from environmental and fire-weather indicator parameters. The model is trained on the Algerian Forest Fires dataset using a **Ridge Regression** ML pipeline with standardized scaling.

---

## 📋 Table of Contents
- [Project Overview](#-project-overview)
- [Machine Learning Pipeline](#-machine-learning-pipeline)
- [Input Features & Encoding](#-input-features--encoding)
- [Project Directory Structure](#-project-directory-structure)
- [Local Development & Testing](#-local-development--testing)
- [Vercel Deployment Guide (Zero Server Setup)](#-vercel-deployment-guide)
- [AWS Elastic Beanstalk Deployment Guide](#-aws-elastic-beanstalk-deployment-guide)
- [Production Architecture & EB Configurations](#-production-architecture--eb-configurations)
- [Troubleshooting & Common Deployment Issues](#-troubleshooting--common-deployment-issues)

---

## 🌲 Project Overview

The **Forest Weather Index (FWI)** is a meteorologically-based system used worldwide to estimate wildfire potential and fire danger behavior. This application provides a modern, responsive, and accessible dark-themed dashboard to compute real-time FWI predictions using an existing trained Machine Learning model.

### Key Highlights:
- **Clean ML Pipeline Preservation**: Exact 9-feature order maintained for `StandardScaler` and `Ridge Regression`.
- **Zero Frontend Framework Bloat**: Pure semantic HTML5, modern CSS custom properties, and vanilla JavaScript (no React, Tailwind, or Bootstrap required).
- **Dual-Layer Validation**: Strict client-side and server-side range and numeric validation with graceful user feedback.
- **AWS Elastic Beanstalk Ready**: Pre-configured WSGI entry point, Gunicorn process orchestration, `.ebextensions`, and `.ebignore`.

---

## ⚙️ Machine Learning Pipeline

The project implements the following training and inference pipeline:

```
Algerian Forest Fires Raw Dataset
       │
       ▼
Data Cleaning & Preprocessing (Date columns removed)
       │
       ▼
Binary Encoding of 'Classes' (0: Not Fire, 1: Fire)
Binary Encoding of 'Region' (0: Bejaia, 1: Sidi-Bel Abbes)
       │
       ▼
Multicollinearity Reduction (DC and BUI dropped)
       │
       ▼
StandardScaler Normalization (models/scaler.pkl)
       │
       ▼
Ridge Regression Inference (models/ridge.pkl)
       │
       ▼
Predicted FWI + Contextual Risk Interpretation
```

---

## 📊 Input Features & Encoding

The model requires exactly **9 features** passed in the following order:

| Index | Feature | Unit / Type | Allowable Range | Description |
|---|---|---|---|---|
| 1 | **Temperature** | °C | -20.0 to 60.0 | Ambient temperature (typical 22°C - 42°C) |
| 2 | **RH** | % | 0.0 to 100.0 | Relative atmospheric humidity |
| 3 | **Ws** | km/h | 0.0 to 120.0 | Wind velocity recorded at 10m height |
| 4 | **Rain** | mm | 0.0 to 300.0 | 24-hour accumulated precipitation |
| 5 | **FFMC** | Index (0–101) | 0.0 to 105.0 | Fine Fuel Moisture Code (surface litter moisture) |
| 6 | **DMC** | Index | 0.0 to 500.0 | Duff Moisture Code (loosely compacted organic layer) |
| 7 | **ISI** | Index | 0.0 to 150.0 | Initial Spread Index (rate of fire spread potential) |
| 8 | **Classes** | Categorical | `0` or `1` | `0`: Not Fire, `1`: Fire |
| 9 | **Region** | Categorical | `0` or `1` | `0`: Bejaia Region, `1`: Sidi-Bel Abbes Region |

### Contextual Risk Interpretation
Based on standard Canadian Forest Fire Weather Index rating bands:
- **Low**: FWI < 5.2
- **Moderate**: 5.2 &le; FWI < 11.2
- **High**: 11.2 &le; FWI < 21.3
- **Very High / Extreme**: FWI &ge; 21.3

---

## 📁 Project Directory Structure

```
Algeria_and_Bejai_Region_FWI_Prediction_Project/
│
├── api/
│   └── index.py               # Vercel serverless function entry point
├── application.py             # Main Flask WSGI application entry point
├── vercel.json                # Vercel serverless routes & bundle configurations
├── .vercelignore              # Excludes dev notebooks & test files from Vercel
├── requirements.txt           # Minimal production dependencies
├── Procfile                   # Process configuration for Gunicorn on AWS EB
├── test_app.py                # Automated test suite (12 unit & integration tests)
├── README.md                  # Complete documentation and deployment guide
│
├── .ebextensions/
│   └── python.config          # Elastic Beanstalk WSGI handler configuration
│
├── .ebignore                  # Prevents dev notebooks & datasets from being deployed to AWS EB
├── .gitignore                 # Standard Python git exclusions
│
├── models/
│   ├── ridge.pkl              # Pre-trained Ridge Regression model artifact
│   └── scaler.pkl             # Fitted StandardScaler artifact (9 features)
│
├── templates/
│   ├── index.html             # Prediction dashboard with presets & responsive form
│   └── predict.html           # Prediction result page with risk band & parameters
│
├── static/
│   ├── css/
│   │   └── style.css          # Dark forest aesthetic, accessible styles
│   └── js/
│       └── script.js          # Vanilla JS presets, validation & button states
│
└── notebooks/                 # ML research artifacts (excluded from production deployment)
    ├── 2.0-EDA And FE Algerian Forest Fires.ipynb
    ├── 3.0-Model Training.ipynb
    └── Algerian_forest_fires_cleaned_dataset.csv
```

---

## 💻 Local Development & Testing

### 1. Create and Activate Virtual Environment
```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Automated Tests
```bash
python test_app.py
```
Expected output:
```
Ran 12 tests in 0.086s
OK
```

### 4. Start Local Flask Server
```bash
python application.py
```
Open your browser at: `http://localhost:5000`

---

## ⚡ Vercel Deployment Guide

Deploying this Flask ML project to **Vercel** runs it as a serverless application with zero server maintenance.

### Method A: Deploy via GitHub (Recommended & Easiest)

1. **Push your code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Configure project for Vercel & AWS deployment"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo-name>.git
   git push -u origin main
   ```
2. **Go to [Vercel](https://vercel.com)**:
   - Log in and click **"Add New..."** > **"Project"**.
   - Import your GitHub repository.
3. **Configure & Deploy**:
   - Vercel automatically detects the Python runtime and reads `vercel.json` and `requirements.txt`.
   - Leave Framework Preset as **Other**.
   - Click **"Deploy"**.
4. **Access your application**:
   - Vercel will build the dependencies and provide an instant live URL: `https://<your-project>.vercel.app`.

---

### Method B: Deploy via Vercel CLI

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```
2. **Log in to Vercel**:
   ```bash
   vercel login
   ```
3. **Deploy from project root**:
   ```bash
   # Preview deployment
   vercel

   # Production deployment
   vercel --prod
   ```
4. Follow the brief interactive prompts (Accept default settings by pressing Enter).

---

## ☁️ AWS Elastic Beanstalk Deployment Guide

### Prerequisites
1. An active AWS Account.
2. AWS CLI installed and configured (`aws configure`).
3. AWS Elastic Beanstalk CLI (`awsebcli`) installed:
   ```bash
   pip install awsebcli
   ```

---

### Method A: Deploy via EB CLI (Recommended)

#### Step 1: Initialize Elastic Beanstalk Application
From the project root directory, run:
```bash
eb init -p python-3.11 fwi-prediction-app --region us-east-1
```
*(Select your preferred AWS region when prompted).*

#### Step 2: Create Environment and Deploy
```bash
eb create fwi-env --instance-type t3.micro --single
```
*Note: `--single` launches a single EC2 instance without an Application Load Balancer to minimize AWS costs.*

#### Step 3: Open the Deployed Application
```bash
eb open
```

#### Step 4: Subsequent Updates
Whenever you make updates to the code:
```bash
eb deploy
```

---

### Method B: Deploy via AWS Management Console (ZIP Upload)

If you prefer using the AWS Web Console:

1. **Create Deployment ZIP**:
   Package only the deployment files (excluding `notebooks/`, `.git/`, and virtual environments).
   ```bash
   # Windows PowerShell:
   Compress-Archive -Path application.py, requirements.txt, Procfile, .ebextensions, models, templates, static -DestinationPath fwi_deploy.zip
   ```
2. Navigate to **AWS Elastic Beanstalk Console**.
3. Click **Create application**.
4. Set Application name: `fwi-prediction-app`.
5. Platform: **Python** (Platform branch: **Python 3.11** or **Python 3.10** running on 64bit Amazon Linux 2023).
6. Under **Application code**, select **Upload your code** and choose `fwi_deploy.zip`.
7. Click **Create app**. Elastic Beanstalk will provision the EC2 instance, install `requirements.txt`, configure Gunicorn via `Procfile`, and display the live environment URL.

---

## 🛠️ Production Architecture & EB Configurations

### 1. `application.py`
- Exposes `application = Flask(__name__)` as required by AWS Elastic Beanstalk's Python WSGI container.
- Uses dynamic environment port resolution: `port = int(os.environ.get("PORT", 5000))`.
- Strictly sets `debug=False` for production security.
- Uses absolute path resolution relative to `__file__` to reliably locate `models/ridge.pkl` and `models/scaler.pkl` in containerized environments.

### 2. `.ebextensions/python.config`
```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: application:application
```

### 3. `Procfile`
```
web: gunicorn --bind 0.0.0.0:5000 --workers=2 --threads=4 --timeout=60 application:application
```

### 4. `.ebignore`
Ensures notebooks and training CSVs are excluded from the deployment archive, keeping bundle size under **100 KB** and deployment fast.

---

## 🔍 Verifying the Deployed Application

Once deployed, verify the system is operating normally:

1. **Health Check**:
   Visit the base URL `https://<your-env-domain>.elasticbeanstalk.com/`. Verify that the dashboard loads with all form fields and styling intact.
2. **Preset Verification**:
   Click **"🔥 High Fire Risk Sample"**. The fields should instantly populate with realistic parameters.
3. **Prediction Test**:
   Click **"Predict Forest Weather Index"**.
   - Button should display "Computing Prediction..." with an animated spinner.
   - You should be directed to `/predict` displaying a numeric FWI score (e.g. `~16.7` - High Fire Danger).
   - Click **"Make Another Prediction"** to confirm navigation returns cleanly to the form.
4. **Validation Test**:
   Clear the form and submit. Confirm client validation alerts you without crashing or showing internal Python tracebacks.

---

## ⚠️ Troubleshooting & Common Deployment Issues

| Issue / Error | Root Cause | Solution |
|---|---|---|
| **502 Bad Gateway** | Gunicorn process crashed or failed to bind to port 5000. | Check `Procfile`. Run `eb logs --web` to inspect Gunicorn stderr. Confirm dependencies in `requirements.txt` installed without compile errors. |
| **500 Internal Server Error** | Model pickle incompatibility or missing model files. | Verify `models/ridge.pkl` and `models/scaler.pkl` are included in deployment archive. Ensure `scikit-learn` in `requirements.txt` is compatible with the model serialization version (`>=1.2.0`). |
| **Health Degraded / Severe** | Insufficient memory on `t2.nano` / `t2.micro` during pip install. | Use `t3.micro` or `t3.small` instance type. Add `--instance-type t3.micro` when creating the environment. |
| **Static files 404** | Incorrect relative links. | Ensure templates reference static assets using Flask's `{{ url_for('static', filename='...') }}`. |
| **Logs Access** | Need to debug live issues. | Run `eb logs` from CLI or download full logs from AWS Elastic Beanstalk Console -> Logs. |

---

## 📄 License
This project is developed for educational and portfolio demonstration purposes based on the Algerian Forest Fires research dataset.
