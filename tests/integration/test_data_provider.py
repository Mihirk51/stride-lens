"""
Integration tests for DataProvider using real service clients.
Run this to verify all adapter methods work in production-like conditions.
"""

from src.adapters.data_provider import DataProvider
from src.api.dependencies import (
    get_lat_lon_service,
    get_strava_client,
    get_training_load_service,
    get_weather_client,
)


def test_weather_conditions():
    """Test fetching and transforming weather data."""
    print("\n=== Testing Weather Conditions ===")
    try:
        provider = DataProvider(
            strava_client=get_strava_client(),
            weather_client=get_weather_client(),
            training_load_service=get_training_load_service(),
            lat_lon_service=get_lat_lon_service(),
        )

        weather = provider.get_weather_conditions()
        print(f"✓ Timestamp: {weather.timestamp}")
        print(f"✓ Temperature: {weather.temperature_c}°C")
        print(f"✓ Humidity: {weather.humidity_percent}%")
        print(f"✓ Wind Speed: {weather.wind_speed_mph} mph")
        print(f"✓ Precipitation: {weather.precipitation_mm} mm")
        print(f"✓ Is Day: {weather.is_day}")
        print(f"✓ Timezone: {weather.timezone}")

    except Exception as e:
        print(f"✗ Failed: {e}")


def test_training_load_summary():
    """Test fetching and transforming training load data."""
    print("\n=== Testing Training Load Summary ===")
    try:
        provider = DataProvider(
            strava_client=get_strava_client(),
            weather_client=get_weather_client(),
            training_load_service=get_training_load_service(),
            lat_lon_service=get_lat_lon_service(),
        )

        load = provider.get_training_load_summary()
        print(f"✓ Calculated At: {load.calculated_at}")
        print(f"✓ Last 7 Days: {load.last_7_days_km} km")
        print(f"✓ Last 28 Days: {load.last_28_days_km} km")
        print(f"✓ Baseline Weekly: {load.baseline_weekly_km} km")
        print(f"✓ ACWR: {load.acwr:.2f}")
        print(f"✓ Load Ratio: {load.load_ratio:.2f}")
        print(f"✓ Days Since Last Run: {load.days_since_last_run}")
        print(f"✓ Consecutive Days: {load.consecutive_training_days}")

    except Exception as e:
        print(f"✗ Failed: {e}")


def test_recent_run_trends():
    """Test fetching and transforming recent run data."""
    print("\n=== Testing Recent Run Trends ===")
    try:
        provider = DataProvider(
            strava_client=get_strava_client(),
            weather_client=get_weather_client(),
            training_load_service=get_training_load_service(),
            lat_lon_service=get_lat_lon_service(),
        )

        trends = provider.get_recent_run_trends(limit=5)
        print(f"✓ Calculated At: {trends.calculated_at}")
        print(f"✓ Runs Last 7 Days: {trends.runs_last_7_days}")
        print(f"✓ Runs Last 30 Days: {trends.runs_last_30_days}")
        print(f"✓ Distance Last 7 Days: {trends.total_distance_last_7_days_km:.2f} km")
        print(f"✓ Distance Last 30 Days: {trends.total_distance_last_30_days_km:.2f} km")
        print(f"✓ Days Since Last Run: {trends.days_since_last_run}")
        print("\n  Recent Runs (showing first 3):")
        for run in trends.recent_runs[:3]:
            print(f"  - {run.name}: {run.distance_km:.2f}km at {run.avg_pace_min_per_km:.2f} min/km")

    except Exception as e:
        print(f"✗ Failed: {e}")


def test_sleep_readiness():
    """Test sleep readiness transformation."""
    print("\n=== Testing Sleep Readiness ===")
    try:
        provider = DataProvider(
            strava_client=get_strava_client(),
            weather_client=get_weather_client(),
            training_load_service=get_training_load_service(),
            lat_lon_service=get_lat_lon_service(),
        )

        sleep_none = provider.get_sleep_readiness(sleep_score=None)
        print(f"✓ No score provided: {sleep_none}")

        sleep_with_score = provider.get_sleep_readiness(sleep_score=75.0)
        print(f"✓ Score provided: {sleep_with_score.score}")
        print(f"✓ Data Source: {sleep_with_score.data_source}")
        print(f"✓ Date: {sleep_with_score.date}")

    except Exception as e:
        print(f"✗ Failed: {e}")


def test_all():
    """Run all tests."""
    print("=" * 60)
    print("DataProvider Integration Tests")
    print("=" * 60)

    test_weather_conditions()
    test_training_load_summary()
    test_recent_run_trends()
    test_sleep_readiness()

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    test_all()
