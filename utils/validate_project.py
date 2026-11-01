#!/usr/bin/env python3
"""
YojnaSetu Comprehensive Health & Architecture Validation Suite
"""

import sys
import os
from pathlib import Path

# Ensure UTF-8 output encoding
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))


def run_validation():
    print("=" * 65)
    print("YOJNASETU SYSTEM ARCHITECTURE VALIDATION")
    print("=" * 65)

    all_passed = True

    # 1. Check Core Files
    print("\n[1] CHECKING CORE DIRECTORIES & FILES...")
    critical_files = [
        ('Frontend Template', BASE_DIR / 'frontend' / 'index.html'),
        ('Frontend Script', BASE_DIR / 'frontend' / 'script.js'),
        ('Frontend CSS', BASE_DIR / 'frontend' / 'styles.css'),
        ('Backend API', BASE_DIR / 'backend' / 'yojnasetu_api.py'),
        ('Interactive Predictor', BASE_DIR / 'backend' / 'yojna_setu_ai_interactive.py'),
        ('SQLAlchemy Database Layer', BASE_DIR / 'backend' / 'database.py'),
        ('ML Training Pipeline', BASE_DIR / 'ml' / 'yojna_setu_ai_ml_model.py'),
        ('ML Model Artifact', BASE_DIR / 'ml' / 'models' / 'yojna_setu_ai_ml_model.pkl'),
        ('Cleaned Scheme Dataset', BASE_DIR / 'data' / 'yojna_setu_ai_cleaned.xlsx'),
        ('Production WSGI Entrypoint', BASE_DIR / 'wsgi.py'),
        ('Dockerfile', BASE_DIR / 'Dockerfile'),
        ('Docker Compose Spec', BASE_DIR / 'docker-compose.yml'),
    ]

    for label, path in critical_files:
        if path.exists():
            size = path.stat().st_size
            print(f"   ✓ {label:<28}: {path.name} ({size:,} bytes)")
        else:
            print(f"   ✗ {label:<28}: {path.name} (MISSING)")
            all_passed = False

    # 2. Check Database & Schema
    print("\n[2] CHECKING DATABASE & SCHEMES REPOSITORY...")
    try:
        from backend.database import get_db, Scheme
        with get_db() as db:
            scheme_count = db.query(Scheme).count()
            if scheme_count == 459:
                print(f"   ✓ Schemes Table Verified: {scheme_count} schemes loaded.")
            else:
                print(f"   ⚠️ Schemes Table Count: {scheme_count} schemes (Expected: 459).")
    except Exception as e:
        print(f"   ✗ Database Check Failed: {e}")
        all_passed = False

    # 3. Check ML Model & Predictor
    print("\n[3] CHECKING ML PREDICTOR & HYBRID MATCHING...")
    try:
        from backend.yojna_setu_ai_interactive import YojnaSetuAIPredictor
        predictor = YojnaSetuAIPredictor()
        if predictor.models and predictor.df is not None:
            print(f"   ✓ ML Model & TF-IDF Vectorizer Loaded")
            print(f"   ✓ Cached Schemes in Memory: {len(predictor.df)}")

            # Quick prediction check
            recs = predictor.get_scheme_recommendations({
                'name': 'Validation User',
                'age': 25,
                'gender': 'Female',
                'income': 100000,
                'occupation': 'Student',
                'state': 'DL',
                'category': 'General'
            }, limit=3)
            if len(recs) > 0:
                print(f"   ✓ Recommendation Engine Active: Top match '{recs[0]['scheme']}' (Score: {recs[0]['score']})")
            else:
                print("   ✗ Recommendation returned 0 results")
                all_passed = False
        else:
            print("   ✗ Predictor initialization incomplete")
            all_passed = False
    except Exception as e:
        print(f"   ✗ ML Check Failed: {e}")
        all_passed = False

    # 4. Check REST API App
    print("\n[4] CHECKING REST API & STATIC SERVING...")
    try:
        from backend.yojnasetu_api import app
        client = app.test_client()

        # Health
        res_health = client.get('/api/health')
        assert res_health.status_code == 200
        print(f"   ✓ GET /api/health -> HTTP {res_health.status_code} OK")

        # Frontend Static
        res_ui = client.get('/')
        assert res_ui.status_code == 200
        assert b'YojnaSetu.ai' in res_ui.data
        print(f"   ✓ GET / (UI Static Serve) -> HTTP {res_ui.status_code} OK")

        # Security Headers
        assert res_health.headers.get('X-Content-Type-Options') == 'nosniff'
        print(f"   ✓ HTTP Security Headers Verified")
    except Exception as e:
        print(f"   ✗ API Check Failed: {e}")
        all_passed = False

    print("\n" + "=" * 65)
    if all_passed:
        print("ALL ARCHITECTURAL CHECKS PASSED - YOJNASETU IS HEALTHY & READY ✓")
    else:
        print("WARNINGS DETECTED DURING VALIDATION - PLEASE CHECK OUTPUT ABOVE")
    print("=" * 65)


if __name__ == '__main__':
    run_validation()
