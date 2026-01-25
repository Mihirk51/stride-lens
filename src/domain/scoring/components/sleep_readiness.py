"""Sleep readiness scoring component."""

from src.domain.models.sleep_readiness import SleepReadiness


class SleepReadinessScore(SleepReadiness):
    """Result of sleep readiness scoring (extends domain model)."""

    readiness_level: str
    interpretation: str
    warnings: list[str] = []


class SleepReadinessComponent:
    """
    Scores sleep readiness.

    Philosophy:
    - Uses pre-calculated sleep score from provider (Oura, Whoop, manual, etc.)
    - Normalizes to 0-1 scale for consistency with other components
    - Provides interpretation and warnings based on score thresholds

    Score interpretation (0-1 scale):
    - 0.8-1.0: Excellent recovery
    - 0.6-0.8: Good recovery
    - 0.4-0.6: Fair recovery
    - 0.0-0.4: Poor recovery
    """

    def __init__(self):
        self.warnings: list[str] = []

    def calculate(self, sleep_data: SleepReadiness) -> SleepReadinessScore:
        """
        Calculate sleep readiness interpretation from pre-scored data.

        Note: Sleep score comes in 0-100 scale from data provider.
        This component normalizes to 0-1 scale for consistency.
        """
        self.warnings = []

        sleep_data.score = sleep_data.score / 100.0

        readiness_level, interpretation = self._interpret_score(sleep_data.score, sleep_data)

        self._add_warnings(sleep_data)
        self._add_missing_data_warnings(sleep_data)

        return SleepReadinessScore(
            **sleep_data.model_dump(),
            readiness_level=readiness_level,
            interpretation=interpretation,
            warnings=self.warnings.copy(),
        )

    def _interpret_score(self, score: float, sleep_data: SleepReadiness) -> tuple[str, str]:
        """Provide human-readable interpretation of sleep score (0-1 scale)."""
        if score >= 0.8:
            return "Excellent", "Well-rested and fully recovered. Ideal for hard training or long runs."
        elif score >= 0.6:
            if sleep_data.deep_sleep_minutes and sleep_data.deep_sleep_minutes < 60:
                return (
                    "Good (Low Deep Sleep)",
                    "Good recovery but limited deep sleep. Consider moderate intensity training.",
                )
            return "Good", "Good recovery. Ready for normal training load."
        elif score >= 0.4:
            return "Fair", "Moderate recovery. Prioritize easy runs or consider active recovery."
        else:
            return "Poor", "Insufficient recovery. Rest day or very light activity recommended."

    def _add_warnings(self, sleep_data: SleepReadiness) -> None:
        """Add warnings based on sleep metrics (uses original 0-100 scale for thresholds)."""
        if sleep_data.score < 0.4:
            self.warnings.append("Very poor sleep quality - high injury risk if training hard")

        if sleep_data.deep_sleep_minutes and sleep_data.deep_sleep_minutes < 45:
            self.warnings.append("Limited deep sleep - muscle recovery may be compromised")

        if sleep_data.rem_sleep_minutes and sleep_data.rem_sleep_minutes < 60:
            self.warnings.append("Low REM sleep - cognitive function and coordination may be affected")

        if sleep_data.awake_minutes and sleep_data.awake_minutes > 60:
            self.warnings.append("High wake time - sleep quality disrupted")

        if sleep_data.total_sleep_minutes:
            if sleep_data.total_sleep_minutes < 360:
                self.warnings.append("Less than 6 hours sleep - insufficient for athletic recovery")
            elif sleep_data.total_sleep_minutes < 420:
                self.warnings.append("Less than 7 hours sleep - recovery may be suboptimal")

        if sleep_data.recovery_percent and sleep_data.recovery_percent < 50:
            self.warnings.append("Low recovery score - accumulated fatigue detected")

    def _add_missing_data_warnings(self, sleep_data: SleepReadiness) -> None:
        """Add warnings for missing critical sleep metrics."""
        missing_fields = []

        if sleep_data.total_sleep_minutes is None:
            missing_fields.append("total sleep duration")

        if sleep_data.deep_sleep_minutes is None:
            missing_fields.append("deep sleep data")

        if sleep_data.rem_sleep_minutes is None:
            missing_fields.append("REM sleep data")

        if sleep_data.awake_minutes is None:
            missing_fields.append("wake time data")

        if missing_fields:
            fields_str = ", ".join(missing_fields)
            self.warnings.append(f"Incomplete sleep data: missing {fields_str} - score may be less accurate")

        if sleep_data.data_source == "manual" and len(missing_fields) > 2:
            self.warnings.append(
                "Manual sleep entry with limited data - consider using sleep tracking device for better insights"
            )
