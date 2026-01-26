"""
Integration test for SleepReadinessComponent using real data from DataProvider.
"""

from datetime import datetime, timezone

from src.adapters.data_provider import DataProvider
from src.domain.models.sleep_readiness import SleepReadiness
from src.domain.scoring.components.sleep_readiness import SleepReadinessComponent


def test_sleep_readiness_component():
    """Test sleep readiness scoring with real data."""
    print("\n=== Testing Sleep Readiness Component ===")

    try:
        provider = DataProvider()

        sleep_data = provider.get_sleep_readiness()

        if not sleep_data:
            print("✗ No sleep data available - skipping test")
            return

        print("\n--- Input Data ---")
        print(f"✓ Sleep Score (input): {sleep_data.score} (0-100 scale)")
        print(f"✓ Data Source: {sleep_data.data_source}")
        if sleep_data.total_sleep_minutes:
            print(f"✓ Total Sleep: {sleep_data.total_sleep_minutes} min")
        if sleep_data.deep_sleep_minutes:
            print(f"✓ Deep Sleep: {sleep_data.deep_sleep_minutes} min")
        if sleep_data.rem_sleep_minutes:
            print(f"✓ REM Sleep: {sleep_data.rem_sleep_minutes} min")
        if sleep_data.time_awake_minutes:
            print(f"✓ Time Awake: {sleep_data.time_awake_minutes} min")

        component = SleepReadinessComponent()
        result = component.calculate(sleep_data)

        print("\n--- Scoring Results ---")
        print(f"✓ Score (normalized): {result.score} (0-1 scale)")
        print(f"✓ Readiness Level: {result.readiness_level}")
        print(f"✓ Interpretation: {result.interpretation}")

        if result.warnings:
            print(f"\n--- Warnings ({len(result.warnings)}) ---")
            for i, warning in enumerate(result.warnings, 1):
                print(f"  {i}. {warning}")
        else:
            print("\n✓ No warnings")

        print("\n--- Normalization Check ---")
        expected_normalized = round(sleep_data.score / 100.0, 3)
        print(f"✓ Expected: {expected_normalized}, Got: {result.score}, Match: {result.score == expected_normalized}")

    except Exception as e:
        print(f"✗ Failed: {e}")
        raise


def test_sleep_readiness_edge_cases():
    """Test various sleep score and metric combinations."""
    print("\n=== Testing Edge Cases ===")

    component = SleepReadinessComponent()

    test_cases = [
        {
            "name": "Excellent Recovery",
            "score": 85,
            "total_sleep": 480,
            "deep_sleep": 90,
            "rem_sleep": 120,
            "awake": 20,
        },
        {
            "name": "Good but Low Deep Sleep",
            "score": 70,
            "total_sleep": 420,
            "deep_sleep": 40,
            "rem_sleep": 90,
            "awake": 30,
        },
        {
            "name": "Poor Recovery",
            "score": 35,
            "total_sleep": 300,
            "deep_sleep": 30,
            "rem_sleep": 45,
            "awake": 90,
        },
        {
            "name": "Incomplete Data (Manual Entry)",
            "score": 60,
            "total_sleep": None,
            "deep_sleep": None,
            "rem_sleep": None,
            "awake": None,
        },
    ]

    for case in test_cases:
        sleep_data = SleepReadiness(
            date=datetime.now(timezone.utc),
            score=case["score"],
            total_sleep_minutes=case["total_sleep"],
            deep_sleep_minutes=case["deep_sleep"],
            rem_sleep_minutes=case["rem_sleep"],
            awake_minutes=case["awake"],
            data_source="manual",
        )

        result = component.calculate(sleep_data)

        print(f"\n{case['name']}:")
        print(f"  Input Score: {case['score']} (0-100)")
        print(f"  → Normalized Score: {result.score} (0-1)")
        print(f"  → Readiness: {result.readiness_level}")
        print(f"  → Warnings: {len(result.warnings)}")
        if result.warnings:
            for warning in result.warnings:
                print(f"    - {warning}")


def test_all():
    """Run all integration tests."""
    print("=" * 60)
    print("Sleep Readiness Component Integration Tests")
    print("=" * 60)

    test_sleep_readiness_component()
    test_sleep_readiness_edge_cases()

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    test_all()
