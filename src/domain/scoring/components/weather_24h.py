"""Weather scoring component for 24-hour forecast."""

from pydantic import BaseModel, Field

from src.domain.models.weather_conditions import WeatherConditions


class WeatherScore(BaseModel):
    """Result of weather scoring for 24-hour forecast."""

    hourly_scores: dict[str, float] = Field(..., description="Hour (e.g., '12am', '1pm') -> score (0-1)")
    warnings: list[str] = Field(default_factory=list, description="Weather warnings for poor conditions")
    average_score: float = Field(..., ge=0, le=1, description="Average score across all hours")
    best_hour: str = Field(..., description="Hour with best conditions")
    worst_hour: str = Field(..., description="Hour with worst conditions")


class WeatherScoringComponent:
    """
    Scores weather conditions for running over 24 hours.

    Philosophy:
    - 1.0 = Ideal running conditions
    - 0.5 = Acceptable conditions
    - 0.0 = Dangerous/unsuitable conditions

    Scoring factors:
    - Temperature: 4-15°C optimal (40-60°F)
    - Precipitation: Penalties for rain/snow
    - Wind: Penalties for high wind/gusts
    - Humidity: Moderate penalties for extremes
    """

    def __init__(self):
        self.warnings: list[str] = []

    def calculate(self, forecasts: list[WeatherConditions]) -> WeatherScore:
        """
        Calculate weather scores for each hour in forecast.

        Args:
            forecasts: List of hourly weather conditions (up to 24)

        Returns:
            WeatherScore with hourly scores and aggregate stats
        """
        self.warnings = []
        hourly_scores = {}
        scores_list = []

        for forecast in forecasts:
            hour_label = self._format_hour(forecast.timestamp)
            score = self._score_conditions(forecast)

            hourly_scores[hour_label] = round(score, 3)
            scores_list.append(score)

        # Find best and worst hours
        best_hour = max(hourly_scores, key=hourly_scores.get)
        worst_hour = min(hourly_scores, key=hourly_scores.get)
        avg_score = sum(scores_list) / len(scores_list) if scores_list else 0.5

        return WeatherScore(
            hourly_scores=hourly_scores,
            warnings=self.warnings.copy(),
            average_score=round(avg_score, 3),
            best_hour=best_hour,
            worst_hour=worst_hour,
        )

    def _score_conditions(self, weather: WeatherConditions) -> float:
        """
        Score individual weather conditions (0-1 scale).

        Combines temperature, precipitation, wind, and humidity scores.
        """
        temp_score = self._score_temperature(weather.temperature_c)
        precip_score = self._score_precipitation(weather.precipitation_mm)
        wind_score = self._score_wind(weather.wind_speed_mph, weather.wind_gusts_mph)
        humidity_score = self._score_humidity(weather.humidity_percent)

        # Weighted combination
        weights = {
            "temperature": 0.4,
            "precipitation": 0.3,
            "wind": 0.2,
            "humidity": 0.1,
        }

        final_score = (
            temp_score * weights["temperature"]
            + precip_score * weights["precipitation"]
            + wind_score * weights["wind"]
            + humidity_score * weights["humidity"]
        )

        # Add warnings for poor conditions
        self._add_condition_warnings(weather, temp_score, precip_score, wind_score)

        return final_score

    @staticmethod
    def _score_temperature(temp_c: float) -> float:
        """
        Score temperature for running comfort (0-1 scale).

        Optimal: 4-15°C (40-60°F)
        Acceptable: -5 to 25°C (23-77°F)
        Poor: <-5°C or >25°C
        """
        if 4 <= temp_c <= 15:
            return 1.0
        elif 0 <= temp_c < 4:
            return 0.8 + (temp_c / 4) * 0.2
        elif 15 < temp_c <= 20:
            return 1.0 - ((temp_c - 15) / 5) * 0.15
        elif 20 < temp_c <= 25:
            return 0.85 - ((temp_c - 20) / 5) * 0.35
        elif -5 <= temp_c < 0:
            return 0.6 + ((temp_c + 5) / 5) * 0.2
        elif temp_c < -5:
            penalty = min((abs(temp_c) - 5) * 0.1, 0.6)
            return max(0, 0.6 - penalty)
        else:  # > 25°C
            penalty = min((temp_c - 25) * 0.05, 0.5)
            return max(0, 0.5 - penalty)

    @staticmethod
    def _score_precipitation(precip_mm: float) -> float:
        """
        Score precipitation impact (0-1 scale).

        0mm = 1.0 (ideal)
        <2mm = 0.7 (light drizzle, acceptable)
        2-5mm = 0.4 (moderate rain, uncomfortable)
        >5mm = 0.1-0.3 (heavy rain, poor)
        """
        if precip_mm == 0:
            return 1.0
        elif precip_mm < 1:
            return 0.85
        elif precip_mm < 2:
            return 0.7
        elif precip_mm < 5:
            return 0.4
        else:
            penalty = min((precip_mm - 5) * 0.05, 0.3)
            return max(0.1, 0.4 - penalty)

    @staticmethod
    def _score_wind(wind_speed_mph: float, wind_gusts_mph: float | None) -> float:
        """
        Score wind conditions (0-1 scale).

        <10 mph = 1.0 (ideal)
        10-15 mph = 0.85 (noticeable)
        15-20 mph = 0.6 (challenging)
        20-25 mph = 0.3 (difficult)
        >25 mph = 0.1 (dangerous)

        Gusts penalize further if significantly higher than sustained.
        """
        # Base score from sustained wind
        if wind_speed_mph < 10:
            base_score = 1.0
        elif wind_speed_mph < 15:
            base_score = 0.85
        elif wind_speed_mph < 20:
            base_score = 0.6
        elif wind_speed_mph < 25:
            base_score = 0.3
        else:
            base_score = 0.1

        # Gust penalty if gusts are significantly higher
        if wind_gusts_mph and wind_gusts_mph > wind_speed_mph + 10:
            gust_penalty = min((wind_gusts_mph - wind_speed_mph - 10) * 0.02, 0.2)
            return max(0, base_score - gust_penalty)

        return base_score

    @staticmethod
    def _score_humidity(humidity_percent: int) -> float:
        """
        Score humidity impact (0-1 scale).

        40-60% = 1.0 (ideal)
        30-70% = 0.9 (comfortable)
        20-80% = 0.7 (noticeable)
        <20% or >80% = 0.5 (uncomfortable)
        """
        if 40 <= humidity_percent <= 60:
            return 1.0
        elif 30 <= humidity_percent <= 70:
            return 0.9
        elif 20 <= humidity_percent <= 80:
            return 0.7
        else:
            return 0.5

    def _add_condition_warnings(
        self, weather: WeatherConditions, temp_score: float, precip_score: float, wind_score: float
    ) -> None:
        """Add warnings for hazardous conditions."""
        hour_label = self._format_hour(weather.timestamp)

        if temp_score < 0.3:
            if weather.temperature_c < -10:
                self.warnings.append(f"{hour_label}: Extreme cold ({weather.temperature_c}°C) - frostbite risk")
            elif weather.temperature_c > 30:
                self.warnings.append(f"{hour_label}: Extreme heat ({weather.temperature_c}°C) - heat exhaustion risk")

        if precip_score < 0.4:
            self.warnings.append(
                f"{hour_label}: Heavy precipitation ({weather.precipitation_mm}mm) - slippery conditions"
            )

        if wind_score < 0.4:
            if weather.wind_gusts_mph and weather.wind_gusts_mph > 30:
                self.warnings.append(f"{hour_label}: Strong wind gusts ({weather.wind_gusts_mph}mph) - safety concern")
            else:
                self.warnings.append(f"{hour_label}: High winds ({weather.wind_speed_mph}mph) - challenging conditions")

    @staticmethod
    def _format_hour(timestamp) -> str:
        """Format timestamp to hour label (e.g., '12am', '1pm')."""
        hour = timestamp.hour

        if hour == 0:
            return "12am"
        elif hour < 12:
            return f"{hour}am"
        elif hour == 12:
            return "12pm"
        else:
            return f"{hour - 12}pm"
