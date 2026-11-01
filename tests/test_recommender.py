import pytest
from pathlib import Path
from backend.yojna_setu_ai_interactive import YojnaSetuAIPredictor


@pytest.fixture(scope="module")
def predictor():
    return YojnaSetuAIPredictor()


def test_model_and_dataset_loaded(predictor):
    """Ensure both the ML model and 459-scheme dataset load cleanly"""
    assert predictor.models is not None, "ML models dictionary should be loaded"
    assert predictor.df is not None, "Scheme dataset DataFrame should not be None"
    assert len(predictor.df) == 459, f"Expected 459 schemes, got {len(predictor.df)}"


def test_eligibility_age_filter(predictor):
    """Test age-based eligibility enforcement"""
    scheme = {
        'Min Age': 18,
        'Max Age': 35,
        'Gender': 'All',
        'Min Income': 0,
        'Max Income': 500000,
        'Scheme Type': 'Central'
    }

    assert predictor.check_eligibility({'age': 25, 'gender': 'Male', 'income': 100000}, scheme) is True
    assert predictor.check_eligibility({'age': 40, 'gender': 'Male', 'income': 100000}, scheme) is False
    assert predictor.check_eligibility({'age': 16, 'gender': 'Male', 'income': 100000}, scheme) is False


def test_eligibility_gender_filter(predictor):
    """Test gender restriction enforcement"""
    female_scheme = {
        'Min Age': 0,
        'Max Age': 100,
        'Gender': 'Female',
        'Min Income': 0,
        'Max Income': 10000000,
        'Scheme Type': 'Central'
    }

    assert predictor.check_eligibility({'age': 25, 'gender': 'Female', 'income': 50000}, female_scheme) is True
    assert predictor.check_eligibility({'age': 25, 'gender': 'Male', 'income': 50000}, female_scheme) is False


def test_eligibility_income_filter(predictor):
    """Test income bracket checking"""
    bpl_scheme = {
        'Min Age': 0,
        'Max Age': 100,
        'Gender': 'All',
        'Min Income': 0,
        'Max Income': 150000,
        'Scheme Type': 'Central'
    }

    assert predictor.check_eligibility({'age': 30, 'gender': 'All', 'income': 80000}, bpl_scheme) is True
    assert predictor.check_eligibility({'age': 30, 'gender': 'All', 'income': 300000}, bpl_scheme) is False


def test_recommendation_generation(predictor):
    """Verify end-to-end recommendation generation and ranking"""
    user_profile = {
        'name': 'Anita Roy',
        'age': 21,
        'gender': 'Female',
        'income': 90000,
        'occupation': 'Student',
        'state': 'WB',
        'category': 'General',
        'preferred_categories': ['Education & Scholarships']
    }

    recommendations = predictor.get_scheme_recommendations(user_profile, limit=10)
    assert len(recommendations) > 0
    assert len(recommendations) <= 10

    # Ensure items are ordered by score descending
    scores = [r['score'] for r in recommendations]
    assert scores == sorted(scores, reverse=True)

    # Check structure of each recommendation
    first = recommendations[0]
    required_keys = ['id', 'scheme', 'type', 'category', 'benefit', 'score', 'link', 'docs', 'reasons']
    for key in required_keys:
        assert key in first, f"Missing key '{key}' in recommendation"

    assert 40 <= first['score'] <= 100
    assert isinstance(first['docs'], list)
    assert len(first['docs']) > 0
