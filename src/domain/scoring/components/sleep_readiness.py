"""Sleep readiness scoring component."""

from src.domain.models.sleep_readiness import SleepReadiness


class SleepReadinessScore(SleepReadiness):
    """Result of sleep readiness scoring (extends domain model)."""

    readiness_level: str
    interpretation: str
    warnings: list[str] = []


class SleepReadinessComponent:
    """
    Scores sleep readiness from raw sleep metrics.

    Philosophy:
    - Calculates score from available metrics (sleep stages, recovery, etc.)
    - If sleep_score_percent is provided, uses it as base; otherwise calculates
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
        Calculate sleep readiness score from raw metrics.

        If sleep_score_percent is provided, uses it as base.
        Otherwise, calculates from available metrics.
        Returns 0-1 scale for consistency.
        """
        self.warnings = []

        calculated_score = self._calculate_sleep_score(sleep_data)

        normalized_score = calculated_score / 100.0

        readiness_level, interpretation = self._interpret_score(normalized_score, sleep_data)

        self._add_warnings(sleep_data)
        self._add_missing_data_warnings(sleep_data)

        # Exclude 'score' from model_dump to avoid duplicate argument
        sleep_dict = sleep_data.model_dump(exclude={"score"})

        return SleepReadinessScore(
            **sleep_dict,
            score=normalized_score,
            readiness_level=readiness_level,
            interpretation=interpretation,
            warnings=self.warnings.copy(),
        )

    def _calculate_sleep_score(self, sleep_data: SleepReadiness) -> float:
        """
        Calculate sleep score from available metrics (0-100 scale).

        Uses weighted average of all available metrics.
        Matches original BaseSleepService scoring logic.
        """
        weights = {
            "sleep_score_percent": 0.5,
            "recovery_percent": 0.3,
            "deep_sleep_minutes": 0.2,
            "rem_sleep_minutes": 0.15,
            "core_sleep_minutes": 0.05,
            "time_awake_minutes": -0.2,
            "time_in_bed_minutes": 0.05,
        }

        total_weight = 0
        weighted_sum = 0

        for field, weight in weights.items():
            value = getattr(sleep_data, field, None)
            if value is not None:
                normalized = self._normalize_metric(field, value)
                weighted_sum += normalized * abs(weight)
                total_weight += abs(weight)

        # Return weighted average or default to 50
        return round(weighted_sum / total_weight, 2) if total_weight > 0 else 50.0

    @staticmethod
    def _normalize_metric(field: str, value: float) -> float:
        """
        Normalize sleep metrics to 0-100 scale.

        Research-backed thresholds:
        - Deep sleep: 60-120min optimal for athletes
        - REM sleep: 90-120min optimal
        - Core sleep: 180-270min optimal
        - Time in bed: 420-480min optimal
        - Time awake: <30min good, >60min poor
        """
        if field == "deep_sleep_minutes":
            # Optimal: 60-120min, normalize to 100 at 120min
            return min(value / 120 * 100, 100)

        elif field == "rem_sleep_minutes":
            # Optimal: 90-120min, normalize to 100 at 120min
            return min(value / 120 * 100, 100)

        elif field == "core_sleep_minutes":
            # Optimal: 180-270min, normalize to 100 at 270min
            return min(value / 270 * 100, 100)

        elif field == "time_in_bed_minutes":
            # Optimal: 420-480min (7-8hrs), normalize to 100 at 480min
            return min(value / 480 * 100, 100)

        elif field == "time_awake_minutes":
            # Penalty for wake time: >60min = 0 points, 0min = 100 points
            return max(100 - (value / 60 * 100), 0)

        elif field == "recovery_percent":
            # Already 0-100 scale
            return value

        return float(value)

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

        if sleep_data.time_awake_minutes and sleep_data.time_awake_minutes > 60:
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

        if sleep_data.time_awake_minutes is None:
            missing_fields.append("wake time data")

        if missing_fields:
            fields_str = ", ".join(missing_fields)
            self.warnings.append(f"Incomplete sleep data: missing {fields_str} - score may be less accurate")

        if sleep_data.data_source == "manual" and len(missing_fields) > 2:
            self.warnings.append(
                "Manual sleep entry with limited data - consider using sleep tracking device for better insights"
            )
