import pytest
from datetime import datetime
from backend.database import get_db, Scheme, User, SavedScheme


def test_database_seeded():
    """Verify schemes table has been populated with all 459 schemes"""
    with get_db() as db:
        count = db.query(Scheme).count()
        assert count == 459, f"Expected 459 seeded schemes in database, found {count}"


def test_scheme_query_and_dict():
    """Test scheme model query and serialization"""
    with get_db() as db:
        scheme = db.query(Scheme).first()
        assert scheme is not None
        assert scheme.name
        assert scheme.category

        d = scheme.to_dict()
        assert 'id' in d
        assert 'scheme' in d
        assert 'category' in d
        assert 'benefit' in d
        assert 'docs' in d


def test_user_creation_and_retrieval():
    """Test user record creation and retrieval"""
    test_user_id = "test_user_phone_9999900000"
    with get_db() as db:
        # Clean up existing test user if present
        db.query(User).filter(User.user_id == test_user_id).delete()
        db.commit()

        user = User(
            user_id=test_user_id,
            identifier="9999900000",
            auth_type="phone",
            name="Test Citizen",
            last_active=datetime.utcnow()
        )
        db.add(user)
        db.commit()

        # Retrieve user
        retrieved = db.query(User).filter(User.user_id == test_user_id).first()
        assert retrieved is not None
        assert retrieved.name == "Test Citizen"
        assert retrieved.identifier == "9999900000"

        # Cleanup
        db.delete(retrieved)
        db.commit()


def test_saved_scheme_lifecycle():
    """Test bookmarking, querying, and deleting a saved scheme"""
    test_user_id = "test_user_bookmark_lifecycle"
    test_scheme_id = "test_scheme_001"

    with get_db() as db:
        # Clean up
        db.query(SavedScheme).filter(SavedScheme.user_id == test_user_id).delete()
        db.commit()

        saved = SavedScheme(
            user_id=test_user_id,
            scheme_id=test_scheme_id,
            scheme_name="Ayushman Bharat",
            category="Health",
            benefit="₹5 lakh health cover",
            link="https://pmjay.gov.in"
        )
        db.add(saved)
        db.commit()

        # Check retrieval
        items = db.query(SavedScheme).filter(SavedScheme.user_id == test_user_id).all()
        assert len(items) == 1
        assert items[0].scheme_name == "Ayushman Bharat"

        # Delete
        db.delete(items[0])
        db.commit()

        count_after = db.query(SavedScheme).filter(SavedScheme.user_id == test_user_id).count()
        assert count_after == 0
