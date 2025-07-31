import pytest
from app.routes.match import (
    calculate_distance,
    calculate_skill_match,
    calculate_match_score,
    calculate_urgency_score
)

# Mock Google Maps API key
import os
os.environ["GOOGLE_MAPS_API_KEY"] = "mock_key"

def test_calculate_distance():
    # Mock distance calculation
    origin = "123 Main St, CityA"
    destination = "456 Elm St, CityB"
    distance = calculate_distance(origin, destination)
    assert isinstance(distance, float)
    assert 0.0 <= distance <= 50.0  # Mocked distance should be within range

def test_calculate_skill_match():
    user_skills = ["Python", "FastAPI", "SQL"]
    event_skills = ["Python", "SQL", "Docker"]
    skill_match = calculate_skill_match(user_skills, event_skills)
    assert round(skill_match, 2) == 66.67  # Adjusted for floating-point precision

def test_calculate_urgency_score():
    assert calculate_urgency_score("high") == 1.0
    assert calculate_urgency_score("medium") == 0.6
    assert calculate_urgency_score("low") == 0.3
    assert calculate_urgency_score("unknown") == 0.0

def test_calculate_match_score():
    skill_match = 80.0
    distance = 10.0
    urgency = "high"
    skill_weight = 0.5
    distance_weight = 0.3
    urgency_weight = 0.2

    match_score = calculate_match_score(
        skill_match, distance, urgency, skill_weight, distance_weight, urgency_weight
    )

    assert isinstance(match_score, float)
    assert 0 <= match_score <= 100
