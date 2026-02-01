"""
Integration test for WeatherScoringComponent using real data from DataProvider.
"""

from src.adapters.data_provider import DataProvider
from src.domain.scoring.components.weather_24h import WeatherScoringComponent


def test_weather_scoring_component():
    """Test weather scoring with real 24h forecast data."""
    print("\n=== Testing Weather Scoring Component ===")

    try:
        provider = DataProvider()

        forecasts = provider.get_weather_forecast_24h()

        if not forecasts:
            print("✗ No weather forecast data available - skipping test")
            return

        print("\n--- Input Data ---")
        print(f"✓ Total forecasts: {len(forecasts)}")
        print(f"✓ First: {forecasts[0].timestamp} - {forecasts[0].temperature_c}°C")
        print(f"✓ Last: {forecasts[-1].timestamp} - {forecasts[-1].temperature_c}°C")

        component = WeatherScoringComponent()
        result = component.calculate(forecasts)

        print("\n--- Scoring Results ---")
        print(f"✓ Hours scored: {len(result.hourly_scores)}")
        print(f"✓ Average score: {result.average_score:.3f} (0-1 scale)")
        print(f"✓ Best hour: {result.best_hour} (score: {result.hourly_scores[result.best_hour]:.3f})")
        print(f"✓ Worst hour: {result.worst_hour} (score: {result.hourly_scores[result.worst_hour]:.3f})")

        if result.warnings:
            print(f"\n--- Warnings ({len(result.warnings)}) ---")
            for i, warning in enumerate(result.warnings[:5], 1):  # Show first 5
                print(f"  {i}. {warning}")
            if len(result.warnings) > 5:
                print(f"  ... and {len(result.warnings) - 5} more")
        else:
            print("\n✓ No warnings - good conditions throughout")

        # Show sample hourly scores
        print("\n--- Sample Hourly Scores ---")
        sample_hours = list(result.hourly_scores.keys())[:5]
        for hour in sample_hours:
            score = result.hourly_scores[hour]
            print(f"  {hour}: {score:.3f}")

    except Exception as e:
        print(f"✗ Failed: {e}")
        raise


def test_weather_scoring_edge_cases():
    """Test weather scoring with various conditions."""
    print("\n=== Testing Edge Cases ===")

    from datetime import datetime, timedelta

    from src.domain.models.weather_conditions import WeatherConditions

    component = WeatherScoringComponent()

    # Test 1: Ideal conditions
    print("\nTest 1: Ideal Running Conditions")
    ideal_forecasts = [
        WeatherConditions(
            timestamp=datetime.now() + timedelta(hours=i),
            temperature_c=10.0,
            humidity_percent=50,
            wind_speed_mph=5.0,
            wind_gusts_mph=7.0,
            precipitation_mm=0.0,
            is_day=True,
            timezone="America/New_York",
        )
        for i in range(6)
    ]

    result = component.calculate(ideal_forecasts)
    print(f"✓ Average score: {result.average_score:.3f} (expected: close to 1.0)")
    print(f"✓ Warnings: {len(result.warnings)}")

    # Test 2: Poor conditions (cold, rain, wind)
    print("\nTest 2: Poor Conditions (Cold, Rain, Wind)")
    poor_forecasts = [
        WeatherConditions(
            timestamp=datetime.now() + timedelta(hours=i),
            temperature_c=-12.0,
            humidity_percent=85,
            wind_speed_mph=22.0,
            wind_gusts_mph=35.0,
            precipitation_mm=8.0,
            is_day=False,
            timezone="America/New_York",
        )
        for i in range(6)
    ]

    result = component.calculate(poor_forecasts)
    print(f"✓ Average score: {result.average_score:.3f} (expected: low)")
    print(f"✓ Warnings: {len(result.warnings)}")
    for warning in result.warnings[:3]:
        print(f"  - {warning}")

    # Test 3: Mixed conditions
    print("\nTest 3: Mixed Conditions")
    mixed_forecasts = [
        WeatherConditions(
            timestamp=datetime.now() + timedelta(hours=i),
            temperature_c=5 + i * 2,  # Gradually warming
            humidity_percent=60,
            wind_speed_mph=10 - i,  # Decreasing wind
            precipitation_mm=max(0, 3 - i * 0.5),  # Clearing up
            is_day=i >= 3,
            timezone="America/New_York",
        )
        for i in range(6)
    ]

    result = component.calculate(mixed_forecasts)
    print(f"✓ Average score: {result.average_score:.3f}")
    print(f"✓ Best hour: {result.best_hour} (score: {result.hourly_scores[result.best_hour]:.3f})")
    print(f"✓ Worst hour: {result.worst_hour} (score: {result.hourly_scores[result.worst_hour]:.3f})")


def test_all():
    """Run all integration tests."""
    print("=" * 60)
    print("Weather Scoring Component Integration Tests")
    print("=" * 60)

    test_weather_scoring_component()
    test_weather_scoring_edge_cases()

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    test_all()
