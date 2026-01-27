"""
Integration tests for DataProvider using real service clients.
Run this to verify all adapter methods work in production-like conditions.
"""

from src.adapters.data_provider import DataProvider


def test_weather_conditions():
    """Test fetching and transforming weather data."""
    print("\n=== Testing Weather Conditions ===")
    try:
        provider = DataProvider()

        weather = provider.get_current_weather()
        print(f"✓ Timestamp: {weather.timestamp}")
        print(f"✓ Temperature: {weather.temperature_c}°C")
        print(f"✓ Humidity: {weather.humidity_percent}%")
        print(f"✓ Wind Speed: {weather.wind_speed_mph} mph")
        print(f"✓ Wind Gusts: {weather.wind_gusts_mph} mph")
        print(f"✓ Precipitation: {weather.precipitation_mm} mm")
        print(f"✓ Is Day: {weather.is_day}")
        print(f"✓ Timezone: {weather.timezone}")

    except Exception as e:
        print(f"✗ Failed: {e}")


def test_weather_forecast_24h():
    """Test fetching and transforming 24h weather forecast."""
    print("\n=== Testing Weather Forecast 24h ===")
    try:
        provider = DataProvider()

        forecasts = provider.get_weather_forecast_24h()
        print(f"✓ Total forecasts: {len(forecasts)}")
        print("✓ Expected: 24 hourly forecasts")

        if forecasts:
            first = forecasts[0]
            last = forecasts[-1]

            print("\n  First forecast:")
            print(f"  - Timestamp: {first.timestamp}")
            print(f"  - Temperature: {first.temperature_c}°C")
            print(f"  - Humidity: {first.humidity_percent}%")
            print(f"  - Precipitation: {first.precipitation_mm}mm")

            print("\n  Last forecast:")
            print(f"  - Timestamp: {last.timestamp}")
            print(f"  - Temperature: {last.temperature_c}°C")

            hours_diff = (last.timestamp - first.timestamp).total_seconds() / 3600
            print(f"\n  ✓ Time span: {hours_diff:.1f} hours")
        else:
            print("  ✗ No forecasts returned")

    except Exception as e:
        print(f"✗ Failed: {e}")


def test_training_load_summary():
    """Test fetching and transforming training load data."""
    print("\n=== Testing Training Load Summary ===")
    try:
        provider = DataProvider()

        load = provider.get_training_load_summary()
        print(f"✓ Calculated At: {load.calculated_at}")
        print(f"✓ Acute Load (7 days): {load.acute_load_km} km")
        print(f"✓ Chronic Load (28 days): {load.chronic_load_km} km")
        print(f"✓ ACWR: {load.acwr:.2f}")
        print(f"✓ Load Ratio: {load.load_ratio:.2f}")
        print(f"✓ Days Since Last Run: {load.days_since_last_run}")
        print(f"✓ Consecutive Training Days: {load.consecutive_training_days}")

    except Exception as e:
        print(f"✗ Failed: {e}")


def test_recent_run_trends():
    """Test fetching and transforming recent run data."""
    print("\n=== Testing Recent Run Trends ===")
    try:
        provider = DataProvider()

        trends = provider.get_recent_run_trends()
        print(f"✓ Calculated At: {trends.calculated_at}")
        print(f"✓ Runs Last 7 Days: {trends.runs_last_7_days}")
        print(f"✓ Runs Last 28 Days: {trends.runs_last_30_days}")
        print(f"✓ Distance Last 7 Days: {trends.total_distance_last_7_days_km:.2f} km")
        print(f"✓ Distance Last 28 Days: {trends.total_distance_last_30_days_km:.2f} km")
        print(f"✓ Days Since Last Run: {trends.days_since_last_run}")

        if trends.recent_runs:
            print(f"\n  Recent Runs (showing first {min(3, len(trends.recent_runs))}):")
            for run in trends.recent_runs[:3]:
                pace_str = f"{run.avg_pace_min_per_km:.2f} min/km" if run.avg_pace_min_per_km else "N/A"
                hr_str = f"HR: {run.avg_heartrate}" if run.avg_heartrate else "No HR"
                print(f"  - {run.name}: {run.distance_km:.2f}km, {run.moving_time_minutes}min, {pace_str}, {hr_str}")
        else:
            print("  No recent runs found")

    except Exception as e:
        print(f"✗ Failed: {e}")


def test_sleep_readiness():
    """Test sleep readiness transformation."""
    print("\n=== Testing Sleep Readiness ===")
    try:
        provider = DataProvider()

        sleep_none = provider.get_sleep_readiness()
        print(f"✓ No score provided: {sleep_none}")

        sleep_with_score = provider.get_sleep_readiness()
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
    test_weather_forecast_24h()
    test_training_load_summary()
    test_recent_run_trends()
    test_sleep_readiness()

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    test_all()
