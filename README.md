# StrideLens

> **The Run Feeling App** - An AI-powered tool that predicts how your run will feel based on factors like weather, sleep, recovery, and training load. Outputs a simple 0–100 score to guide your daily runs.

---

## 🎯 Overview

StrideLens is a Python-based REST API backend that integrates multiple data sources to help runners make informed decisions about their training. By analyzing your Strava activities, sleep/recovery data, current weather conditions, and training load metrics, StrideLens provides insights to optimize your running performance and reduce injury risk.

## ✨ Features

- **🏃 Strava Integration**: Fetch athlete profiles, recent runs, and activity data
- **🌤️ Weather Data**: Real-time weather and forecasts using Open-Meteo API
- **😴 Sleep & Recovery**: Track sleep quality and recovery metrics (subjective and objective)
- **📊 Training Load Analysis**: Calculate training load ratios and Acute:Chronic Workload Ratio (ACWR)
- **🔄 Automatic Token Management**: Handles Strava OAuth token refresh automatically

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- Strava API credentials (Client ID, Client Secret)
- A Strava account with activity data

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Mihirk51/stride-lens.git
   cd stride-lens
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   Create a `.env` file in the project root:
   ```bash
   touch .env
   ```

   Add the following environment variables:
   ```env
   STRAVA_CLIENT_ID=your_client_id_here
   STRAVA_CLIENT_SECRET=your_client_secret_here
   STRAVA_REFRESH_TOKEN=your_refresh_token_here
   STRAVA_ACCESS_TOKEN=your_initial_access_token_here
   STRAVA_ACCESS_TOKEN_EXPIRY=2024-01-01T00:00:00
   ```

   > **Note**: To get Strava API credentials, visit the [Strava API Settings](https://www.strava.com/settings/api) page and create an application.

5. **Load environment variables (optional)**
   ```bash
   source load_env.sh
   ```

---

## 🏃‍♂️ Running the API

### Start the Development Server

Run the FastAPI application using uvicorn:

```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Options:**
- `--reload`: Enable auto-reload on code changes (development only)
- `--host 0.0.0.0`: Make the server accessible from any network interface
- `--port 8000`: Specify the port (default: 8000)

### Access the API

Once the server is running, you can access:

- **API Base URL**: `http://localhost:8000`
- **Interactive API Documentation (Swagger UI)**: `http://localhost:8000/docs`
- **Alternative API Documentation (ReDoc)**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

---

## 📡 API Endpoints

### Strava Endpoints

#### Get Recent Runs
```http
GET /v1/recent-runs
```
Fetches recent running activities from Strava.

**Response:**
```json
{
  "success": true,
  "message": "Recent runs retrieved successfully",
  "athlete_profile": { ... },
  "activity_units": "imperial",
  "activities": [ ... ]
}
```

#### Get Recent Activities
```http
GET /v1/recent-activites
```
Fetches all recent activities (runs, rides, etc.) from Strava.

#### Get Athlete Profile
```http
GET /v1/athlete-profile
```
Retrieves the authenticated athlete's Strava profile.

---

### Weather Endpoints

#### Get Current Weather
```http
GET /v1/current-weather
```
Fetches current weather conditions based on your location (determined automatically via IP geolocation).

**Response:**
```json
{
  "success": true,
  "message": "Current weather retrieved successfully",
  "weather_data": {
    "temperature_2m": 72.5,
    "wind_speed_10m": 8.2,
    "apparent_temperature": 70.1,
    ...
  }
}
```

#### Get Weather Forecast
```http
GET /v1/weather-forecast?forecast_days=3
```
Retrieves weather forecast for the specified number of days.

**Query Parameters:**
- `forecast_days` (optional): Number of days to forecast (default: 3, max: 7)

---

### Sleep & Recovery Endpoints

#### Record Subjective Sleep
```http
GET /v1/manual/subjective?subjective_rating=7
```
Records subjective sleep quality rating (1-10 scale).

**Query Parameters:**
- `subjective_rating` (required): Integer from 1-10

**Response:**
```json
{
  "success": true,
  "message": "Subjective sleep data recorded successfully",
  "score": 70,
  "method": "subjective",
  "sleep_id": "sleep_a1b2c3d4"
}
```

#### Record Objective Sleep
```http
POST /v1/manual/objective
```
Records detailed sleep metrics from wearable devices or manual entry.

**Query Parameters (all optional):**
- `time_in_bed_minutes`: Total time in bed
- `time_awake_minutes`: Time spent awake
- `rem_sleep_minutes`: REM sleep duration
- `core_sleep_minutes`: Core sleep duration
- `deep_sleep_minutes`: Deep sleep duration
- `recovery_percent`: Recovery percentage (0-100)
- `sleep_score_percent`: Overall sleep score (0-100)

---

### Training Load Endpoints

#### Get Training Load Analysis
```http
GET /v1/training-load?weeks_baseline=4
```
Compares recent 7-day running volume to personal baseline average.

**Query Parameters:**
- `weeks_baseline` (optional): Number of weeks for baseline (default: 4, range: 1-12)

**Response:**
```json
{
  "success": true,
  "message": "Training load analysis retrieved successfully",
  "data": {
    "acute_load": 45.2,
    "chronic_load": 42.8,
    "ratio": 1.06,
    "status": "normal"
  }
}
```

**Interpretation:**
- **0.9-1.1**: Normal range (within 10% of baseline)
- **1.1-1.3**: Moderate increase (monitor fatigue)
- **>1.3**: High increase (elevated injury risk)
- **<0.9**: Below baseline (recovery/taper)

#### Get ACWR (Acute:Chronic Workload Ratio)
```http
GET /v1/acwr
```
Calculates injury risk by comparing recent training (7 days) to long-term fitness (4 weeks).

**Response:**
```json
{
  "success": true,
  "message": "ACWR analysis retrieved successfully",
  "data": {
    "acute_workload": 45.2,
    "chronic_workload": 38.5,
    "acwr": 1.17,
    "risk_level": "optimal"
  }
}
```

**Research-backed thresholds:**
- **0.8-1.3**: Sweet spot (optimal adaptation, low injury risk)
- **1.3-1.5**: Moderate injury risk
- **>1.5**: High injury risk
- **<0.8**: Detraining risk

---

## 🛠️ Development

### Project Structure

```
stride-lens/
├── src/
│   ├── api/                    # FastAPI application
│   │   ├── main.py            # API entry point
│   │   ├── dependencies.py    # Dependency injection
│   │   └── v1/                # API version 1
│   │       ├── routers/       # Endpoint definitions
│   │       └── schemas/       # Response models
│   ├── core/                  # Core utilities
│   │   ├── config.py          # Configuration
│   │   ├── constants.py       # Constants
│   │   └── clients/           # HTTP clients
│   ├── services/              # Business logic
│   │   ├── strava/            # Strava integration
│   │   ├── weather/           # Weather services
│   │   ├── sleep_and_recovery/# Sleep tracking
│   │   └── training_load/     # Training analysis
│   ├── schemas/               # Data models
│   └── interfaces/            # Abstract interfaces
├── tests/                     # Test suite
├── requirements.txt           # Python dependencies
└── .env                       # Environment variables
```

### Running Tests

```bash
pytest tests/
```

### Code Style

This project follows PEP 8 guidelines. Format your code with:

```bash
black src/
```

---

## 🔐 Authentication

StrideLens uses OAuth 2.0 to authenticate with the Strava API. The access token is automatically refreshed when expired using the refresh token stored in your `.env` file.

**Token refresh flow:**
1. On API startup, the system checks if the access token is valid
2. If expired, it automatically uses the refresh token to get a new access token
3. The new tokens are saved back to the `.env` file
4. All subsequent requests use the updated access token

---

## 🌍 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `STRAVA_CLIENT_ID` | Your Strava application client ID | Yes |
| `STRAVA_CLIENT_SECRET` | Your Strava application client secret | Yes |
| `STRAVA_REFRESH_TOKEN` | OAuth refresh token from Strava | Yes |
| `STRAVA_ACCESS_TOKEN` | Current OAuth access token | Yes |
| `STRAVA_ACCESS_TOKEN_EXPIRY` | Token expiry timestamp (ISO format) | Yes |

---

## 📚 API Documentation

When the server is running, visit `http://localhost:8000/docs` for interactive API documentation with:
- Complete endpoint descriptions
- Request/response schemas
- Try-it-out functionality
- Authentication details

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📝 License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.

---

## 🔮 Future Roadmap

- [ ] Implement the AI prediction model (0-100 run feeling score)
- [ ] Add support for additional sleep tracking devices (Oura, Whoop, Apple Watch)
- [ ] Database integration for historical data storage
- [ ] User authentication and multi-user support
- [ ] Mobile app integration
- [ ] Advanced analytics and visualizations
- [ ] Machine learning model for personalized predictions

---

## 📧 Support

For questions or issues, please open an issue on GitHub or contact the maintainers.

---

**Built with ❤️ for runners, by runners**