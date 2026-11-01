import os
import sys
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager

# Ensure safe console printing on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from sqlalchemy import (
    create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_SQLITE_PATH = DATA_DIR / 'yojnasetu.db'

# Check environment for PostgreSQL or default to SQLite
DEFAULT_DB_URL = os.environ.get('DATABASE_URL', f"sqlite:///{DEFAULT_SQLITE_PATH}")

# Fix postgres:// URL format if provided by some cloud providers (e.g. Render/Heroku)
if DEFAULT_DB_URL.startswith("postgres://"):
    DEFAULT_DB_URL = DEFAULT_DB_URL.replace("postgres://", "postgresql://", 1)

engine_kwargs = {}
if DEFAULT_DB_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20

engine = create_engine(DEFAULT_DB_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)
Base = declarative_base()


class Scheme(Base):
    __tablename__ = 'schemes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    scheme_id = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False, index=True)
    provider_type = Column(String(100), default='Government')
    scheme_type = Column(String(100), index=True, default='Central')
    category = Column(String(150), index=True, nullable=False)
    description = Column(Text, default='')
    benefit_amount = Column(String(255), default='Not Specified')
    min_age = Column(Integer, default=0)
    max_age = Column(Integer, default=100)
    gender = Column(String(50), default='All')
    caste_category = Column(String(100), default='All')
    min_income = Column(Integer, default=0)
    max_income = Column(Integer, default=10000000)
    occupation = Column(String(150), default='All')
    education_required = Column(String(150), default='None')
    documents_required = Column(Text, default='')
    application_mode = Column(String(100), default='Online')
    official_link = Column(String(500), default='#')
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_scheme_filter', 'scheme_type', 'category', 'gender'),
    )

    def to_dict(self):
        docs = [d.strip() for d in self.documents_required.split(',') if d.strip()] if self.documents_required else []
        return {
            'id': self.scheme_id,
            'scheme': self.name,
            'name': self.name,
            'type': 'central' if self.scheme_type.lower() in ('central', 'national') else ('private' if self.scheme_type.lower() == 'private' else 'state'),
            'scheme_type_raw': self.scheme_type,
            'provider_type': self.provider_type,
            'category': self.category,
            'desc': self.description or self.category,
            'benefit': self.benefit_amount,
            'minAge': self.min_age,
            'maxAge': self.max_age,
            'gender': self.gender,
            'occupation': self.occupation,
            'caste': self.caste_category,
            'minIncome': self.min_income,
            'maxIncome': self.max_income,
            'docs': docs if docs else ['Aadhaar Card', 'Income Certificate', 'Bank Account'],
            'link': self.official_link
        }


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(120), unique=True, index=True, nullable=False)
    identifier = Column(String(150), unique=True, index=True, nullable=False)
    auth_type = Column(String(20), default='phone')  # 'phone' or 'email'
    name = Column(String(150), default='Citizen')
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'identifier': self.identifier,
            'auth_type': self.auth_type,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class SavedScheme(Base):
    __tablename__ = 'saved_schemes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(120), index=True, nullable=False)
    scheme_id = Column(String(100), nullable=False)
    scheme_name = Column(String(255), nullable=False)
    category = Column(String(150))
    benefit = Column(String(255))
    link = Column(String(500))
    saved_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_user_saved_scheme', 'user_id', 'scheme_id', unique=True),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'scheme_id': self.scheme_id,
            'scheme_name': self.scheme_name,
            'category': self.category,
            'benefit': self.benefit,
            'link': self.link,
            'saved_at': self.saved_at.isoformat() if self.saved_at else None
        }


class SearchHistory(Base):
    __tablename__ = 'search_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(120), index=True, nullable=True)
    age = Column(Integer)
    gender = Column(String(50))
    income = Column(Integer)
    occupation = Column(String(100))
    state = Column(String(50))
    category = Column(String(100))
    recommended_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


@contextmanager
def get_db():
    """Transactional database session generator"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def seed_schemes_from_excel(db_session, excel_path=None):
    """Seed the schemes table if it is currently empty"""
    count = db_session.query(Scheme).count()
    if count > 0:
        return count

    if excel_path is None:
        excel_path = DATA_DIR / 'yojna_setu_ai_cleaned.xlsx'
    excel_path = Path(excel_path)

    if not excel_path.exists():
        print(f"⚠️ Seed file not found at {excel_path}")
        return 0

    print(f"🌱 Seeding schemes from {excel_path}...")
    df = pd.read_excel(excel_path)
    schemes_to_add = []

    for idx, row in df.iterrows():
        s_id = str(row.get('Scheme Id', f"scheme_{idx}")).strip()
        name = str(row.get('Scheme Name', f"Scheme {idx}")).strip()
        provider = str(row.get('Scheme Provider Type', 'Government')).strip()
        s_type = str(row.get('Scheme Type', 'Central')).strip()
        cat = str(row.get('Category', 'General Welfare')).strip()
        desc = str(row.get('Description', '')).strip() if pd.notna(row.get('Description')) else ''
        benefit = str(row.get('Benefit Amount', 'Not Specified')).strip() if pd.notna(row.get('Benefit Amount')) else 'Not Specified'

        min_age = int(row['Min Age']) if pd.notna(row.get('Min Age')) and str(row.get('Min Age')).isdigit() else 0
        max_age = int(row['Max Age']) if pd.notna(row.get('Max Age')) and str(row.get('Max Age')).isdigit() else 100
        min_inc = int(row['Min Income']) if pd.notna(row.get('Min Income')) and str(row.get('Min Income')).isdigit() else 0
        max_inc = int(row['Max Income']) if pd.notna(row.get('Max Income')) and str(row.get('Max Income')).isdigit() else 10000000

        gender = str(row.get('Gender', 'All')).strip() if pd.notna(row.get('Gender')) else 'All'
        caste = str(row.get('Caste Category', 'All')).strip() if pd.notna(row.get('Caste Category')) else 'All'
        occ = str(row.get('Occupation', 'All')).strip() if pd.notna(row.get('Occupation')) else 'All'
        edu = str(row.get('Education Required', 'None')).strip() if pd.notna(row.get('Education Required')) else 'None'
        docs = str(row.get('Documents Required', '')).strip() if pd.notna(row.get('Documents Required')) else ''
        app_mode = str(row.get('Application Mode', 'Online')).strip() if pd.notna(row.get('Application Mode')) else 'Online'
        link = str(row.get('Official Application Link', '#')).strip() if pd.notna(row.get('Official Application Link')) else '#'

        schemes_to_add.append(Scheme(
            scheme_id=s_id,
            name=name,
            provider_type=provider,
            scheme_type=s_type,
            category=cat,
            description=desc,
            benefit_amount=benefit,
            min_age=min_age,
            max_age=max_age,
            gender=gender,
            caste_category=caste,
            min_income=min_inc,
            max_income=max_inc,
            occupation=occ,
            education_required=edu,
            documents_required=docs,
            application_mode=app_mode,
            official_link=link
        ))

    db_session.bulk_save_objects(schemes_to_add)
    db_session.commit()
    print(f"✅ Successfully seeded {len(schemes_to_add)} schemes into the database.")
    return len(schemes_to_add)


def init_db():
    """Initialize schema and seed initial dataset"""
    Base.metadata.create_all(bind=engine)
    with get_db() as session:
        seed_schemes_from_excel(session)


if __name__ == '__main__':
    init_db()
