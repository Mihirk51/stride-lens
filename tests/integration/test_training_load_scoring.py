"""
Integration test for TrainingLoadComponent using real data from DataProvider.
"""

from datetime import datetime, timezone

from src.adapters.data_provider import DataProvider
from src.domain.models.training_load_summary import TrainingLoadSummary
from src.domain.scoring.components.training_load import TrainingLoadComponent


def test_training_load_component():
    """Test training load scoring with real data."""
    print("\n=== Testing Training Load Component ===")

    try:
        provider = DataProvider()

        load_summary = provider.get_training_load_summary()
        print("\n--- Input Data ---")
        print(f"✓ Acute Load (7 days): {load_summary.acute_load_km} km")
        print(f"✓ Chronic Load (28 days): {load_summary.chronic_load_km} km")
        print(f"✓ ACWR: {load_summary.acwr:.2f}")
        print(f"✓ Load Ratio: {load_summary.load_ratio:.2f}")
        print(f"✓ Days Since Last Run: {load_summary.days_since_last_run}")
        print(f"✓ Consecutive Training Days: {load_summary.consecutive_training_days}")

        component = TrainingLoadComponent()
        result = component.calculate(load_summary)

        print("\n--- Scoring Results ---")
        print(f"✓ Score: {result.score:.3f} (0-1 scale)")
        print(f"✓ Fatigue Level: {result.fatigue_level}")
        print(f"✓ Interpretation: {result.interpretation}")

        if result.warnings:
            print(f"\n--- Warnings ({len(result.warnings)}) ---")
            for i, warning in enumerate(result.warnings, 1):
                print(f"  {i}. {warning}")
        else:
            print("\n✓ No warnings")

        print("\n--- Embedded Summary ---")
        print(f"✓ Summary contains all original data: {result.summary.acwr == load_summary.acwr}")

    except Exception as e:
        print(f"✗ Failed: {e}")
        raise


def test_training_load_edge_cases():
    """Test various ACWR/load_ratio combinations."""
    print("\n=== Testing Edge Cases ===")

    component = TrainingLoadComponent()

    test_cases = [
        {
            "name": "Optimal Load",
            "acwr": 1.0,
            "load_ratio": 1.0,
            "days_since": 2,
            "consecutive": 3,
        },
        {
            "name": "High Injury Risk",
            "acwr": 1.6,
            "load_ratio": 1.5,
            "days_since": 1,
            "consecutive": 15,
        },
        {
            "name": "Detraining",
            "acwr": 0.6,
            "load_ratio": 0.7,
            "days_since": 15,
            "consecutive": 0,
        },
        {
            "name": "Controlled Progression",
            "acwr": 1.2,
            "load_ratio": 1.2,
            "days_since": 2,
            "consecutive": 5,
        },
    ]

    for case in test_cases:
        summary = TrainingLoadSummary(
            calculated_at=datetime.now(timezone.utc),
            acute_load_km=40.0,
            chronic_load_km=40.0,
            acwr=case["acwr"],
            load_ratio=case["load_ratio"],
            days_since_last_run=case["days_since"],
            consecutive_training_days=case["consecutive"],
        )

        result = component.calculate(summary)

        print(f"\n{case['name']}:")
        print(f"  ACWR: {case['acwr']:.2f}, Load Ratio: {case['load_ratio']:.2f}")
        print(f"  → Score: {result.score:.3f}")
        print(f"  → Level: {result.fatigue_level}")
        print(f"  → Warnings: {len(result.warnings)}")


def test_all():
    """Run all integration tests."""
    print("=" * 60)
    print("Training Load Component Integration Tests")
    print("=" * 60)

    test_training_load_component()
    test_training_load_edge_cases()

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    test_all()
