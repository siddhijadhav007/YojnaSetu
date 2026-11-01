import os
import sys
import pickle
import re
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# Configure stdout safely for console encoding
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_MODEL_PATH = BASE_DIR / 'ml' / 'models' / 'yojna_setu_ai_ml_model.pkl'
DEFAULT_DATA_PATH = BASE_DIR / 'data' / 'yojna_setu_ai_cleaned.xlsx'

STATE_CODE_MAP = {
    'AN': 'Andaman and Nicobar Islands', 'AP': 'Andhra Pradesh', 'AR': 'Arunachal Pradesh',
    'AS': 'Assam', 'BR': 'Bihar', 'CH': 'Chandigarh', 'CG': 'Chhattisgarh',
    'DD': 'Dadra and Nagar Haveli and Daman and Diu', 'DL': 'Delhi', 'GA': 'Goa',
    'GJ': 'Gujarat', 'HR': 'Haryana', 'HP': 'Himachal Pradesh', 'JK': 'Jammu and Kashmir',
    'JH': 'Jharkhand', 'KA': 'Karnataka', 'KL': 'Kerala', 'LA': 'Ladakh',
    'LD': 'Lakshadweep', 'MP': 'Madhya Pradesh', 'MH': 'Maharashtra', 'MN': 'Manipur',
    'ML': 'Meghalaya', 'MZ': 'Mizoram', 'NL': 'Nagaland', 'OD': 'Odisha',
    'PY': 'Puducherry', 'PB': 'Punjab', 'RJ': 'Rajasthan', 'SK': 'Sikkim',
    'TN': 'Tamil Nadu', 'TS': 'Telangana', 'TR': 'Tripura', 'UP': 'Uttar Pradesh',
    'UK': 'Uttarakhand', 'WB': 'West Bengal'
}


class YojnaSetuAIPredictor:
    def __init__(self, model_path=None, dataset_path=None):
        self.model_path = Path(model_path) if model_path else Path(os.environ.get('MODEL_PATH', DEFAULT_MODEL_PATH))
        self.dataset_path = Path(dataset_path) if dataset_path else Path(os.environ.get('DATASET_PATH', DEFAULT_DATA_PATH))
        self.models = None
        self.encoders = None
        self.scaler = None
        self.vectorizer = None
        self.df = None
        self.tfidf_matrix = None

        self.load_model()
        self.load_dataset()

    def load_model(self):
        """Load trained ML artifacts"""
        candidates = [
            self.model_path,
            BASE_DIR / 'ml' / 'models' / 'yojna_setu_ai_ml_model.pkl',
            Path('ml/models/yojna_setu_ai_ml_model.pkl'),
            Path('yojna_setu_ai_ml_model.pkl')
        ]

        found_path = None
        for p in candidates:
            if p.exists():
                found_path = p
                break

        if not found_path:
            print(f"⚠️ Model file not found in candidates: {[str(p) for p in candidates]}")
            return False

        try:
            with open(found_path, 'rb') as f:
                model_data = pickle.load(f)
            self.models = model_data.get('models', {})
            self.encoders = model_data.get('encoders', {})
            self.scaler = model_data.get('scaler')
            self.vectorizer = model_data.get('vectorizer')
            self.model_path = found_path
            print(f"✅ Model loaded successfully from {found_path}")
            return True
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False

    def load_dataset(self):
        """Load and cache the scheme dataset"""
        candidates = [
            self.dataset_path,
            BASE_DIR / 'data' / 'yojna_setu_ai_cleaned.xlsx',
            Path('data/yojna_setu_ai_cleaned.xlsx'),
            Path('yojna_setu_ai_cleaned.xlsx')
        ]

        found_path = None
        for p in candidates:
            if p.exists():
                found_path = p
                break

        if not found_path:
            print(f"❌ Dataset file not found in: {[str(p) for p in candidates]}")
            return False

        try:
            df = pd.read_excel(found_path)
            # Ensure defaults for required columns
            df['Min Age'] = pd.to_numeric(df.get('Min Age', 0), errors='coerce').fillna(0)
            df['Max Age'] = pd.to_numeric(df.get('Max Age', 100), errors='coerce').fillna(100)
            df['Min Income'] = pd.to_numeric(df.get('Min Income', 0), errors='coerce').fillna(0)
            df['Max Income'] = pd.to_numeric(df.get('Max Income', 10000000), errors='coerce').fillna(10000000)
            df['Gender'] = df.get('Gender', 'All').fillna('All').astype(str)
            df['Occupation'] = df.get('Occupation', 'All').fillna('All').astype(str)
            df['Caste Category'] = df.get('Caste Category', 'All').fillna('All').astype(str)
            df['Scheme Type'] = df.get('Scheme Type', 'Central').fillna('Central').astype(str)
            df['Scheme Provider Type'] = df.get('Scheme Provider Type', 'Government').fillna('Government').astype(str)
            df['Description'] = df.get('Description', '').fillna('').astype(str)
            df['Benefit Amount'] = df.get('Benefit Amount', 'Not Specified').fillna('Not Specified').astype(str)
            df['Official Application Link'] = df.get('Official Application Link', '#').fillna('#').astype(str)

            self.df = df
            self.dataset_path = found_path

            # Pre-compute TF-IDF representation if vectorizer is available
            if self.vectorizer is not None and 'Description' in df.columns:
                try:
                    self.tfidf_matrix = self.vectorizer.transform(df['Description'])
                except Exception:
                    self.tfidf_matrix = None

            print(f"✅ Dataset cached: {len(self.df)} schemes from {found_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to load dataset: {e}")
            return False

    def check_eligibility(self, user_profile, scheme):
        """Check if user meets mandatory eligibility filters"""
        try:
            # 1. Age check
            user_age = user_profile.get('age', 30)
            if not (scheme['Min Age'] <= user_age <= scheme['Max Age']):
                return False

            # 2. Gender check
            scheme_gender = scheme['Gender'].strip().lower()
            user_gender = str(user_profile.get('gender', 'All')).strip().lower()
            if scheme_gender not in ('all', 'any'):
                if user_gender not in ('all', 'prefer not to say', 'prefer_not_to_say', ''):
                    if scheme_gender != user_gender:
                        return False

            # 3. Income check
            user_income = user_profile.get('income', 50000)
            if not (scheme['Min Income'] <= user_income <= scheme['Max Income']):
                return False

            # 4. State eligibility
            scheme_type = scheme['Scheme Type'].strip()
            user_state = user_profile.get('state', '').strip().upper()
            state_full_name = STATE_CODE_MAP.get(user_state, user_state).lower()

            if scheme_type.lower() not in ('central', 'private', 'all'):
                # If scheme is state-specific, verify it matches
                if user_state and state_full_name:
                    if scheme_type.lower() != state_full_name and scheme_type.lower() != user_state.lower():
                        return False

            return True
        except Exception:
            return False

    def calculate_relevance_score(self, user_profile, scheme, scheme_index=None):
        """Calculate composite relevance score and match reasons"""
        score = 30.0  # Base score for passing eligibility
        reasons = ['Meets basic eligibility criteria']

        try:
            # Age proximity score (up to 15 points)
            age_range = scheme['Max Age'] - scheme['Min Age']
            user_age = user_profile.get('age', 30)
            if age_range > 0:
                age_center = (scheme['Min Age'] + scheme['Max Age']) / 2.0
                dist = abs(user_age - age_center) / age_range
                age_points = max(0.0, (1.0 - dist) * 15.0)
                score += age_points
                if age_points > 10:
                    reasons.append('Ideal age bracket match')

            # Income score (up to 15 points)
            user_income = user_profile.get('income', 50000)
            inc_range = scheme['Max Income'] - scheme['Min Income']
            if inc_range > 0:
                income_center = (scheme['Min Income'] + scheme['Max Income']) / 2.0
                inc_dist = abs(user_income - income_center) / inc_range
                inc_points = max(0.0, (1.0 - inc_dist) * 15.0)
                score += inc_points
                if user_income <= 100000:
                    reasons.append('Eligible for low-income / BPL financial aid')

            # Occupation match (up to 20 points)
            user_occ = str(user_profile.get('occupation', 'Any')).lower()
            scheme_occ = str(scheme['Occupation']).lower()
            if scheme_occ in ('all', 'any'):
                score += 10.0
            elif user_occ in scheme_occ or scheme_occ in user_occ:
                score += 20.0
                reasons.append(f'Tailored for {scheme["Occupation"]}')
            else:
                # Related occupations matching
                occ_map = {
                    'student': ['youth', 'education', 'scholarship', 'student'],
                    'farmer': ['agri', 'farm', 'kisan', 'rural'],
                    'self-employed': ['business', 'entrepreneur', 'vendor', 'msme'],
                    'unemployed': ['youth', 'skill', 'training', 'job'],
                    'retired': ['senior', 'pension', 'elderly']
                }
                for k, synonyms in occ_map.items():
                    if k in user_occ and any(s in scheme_occ for s in synonyms):
                        score += 15.0
                        reasons.append('Directly matches employment profile')
                        break

            # State match (up to 10 points)
            user_state = user_profile.get('state', '').strip().upper()
            state_full = STATE_CODE_MAP.get(user_state, user_state).lower()
            scheme_type = scheme['Scheme Type'].strip().lower()
            if user_state and (scheme_type == state_full or scheme_type == user_state.lower()):
                score += 10.0
                reasons.append(f'Exclusive scheme for {STATE_CODE_MAP.get(user_state, user_state)}')
            elif scheme_type == 'central':
                score += 6.0
                reasons.append('Pan-India Central Government Scheme')

            # Caste / Category match (up to 10 points)
            user_caste = str(user_profile.get('caste', user_profile.get('category', 'all'))).lower()
            scheme_caste = str(scheme['Caste Category']).lower()
            if user_caste not in ('all', 'general', ''):
                if user_caste in scheme_caste:
                    score += 10.0
                    reasons.append(f'Special affirmative benefits for {user_caste.upper()}')

            # Semantic match with TF-IDF if available (up to 10 points)
            if self.vectorizer is not None and self.tfidf_matrix is not None and scheme_index is not None:
                query_text = f"{user_profile.get('occupation', '')} {user_profile.get('gender', '')} {' '.join(user_profile.get('preferred_categories', []))}"
                if query_text.strip():
                    query_vec = self.vectorizer.transform([query_text])
                    sim = cosine_similarity(query_vec, self.tfidf_matrix[scheme_index:scheme_index+1])[0][0]
                    score += min(10.0, sim * 15.0)

        except Exception:
            pass

        return min(99.0, max(40.0, score)), reasons

    def get_scheme_recommendations(self, user_profile, limit=25):
        """Generate ranked list of eligible and recommended schemes"""
        if self.df is None:
            if not self.load_dataset():
                return []

        results = []
        for idx, scheme in self.df.iterrows():
            if self.check_eligibility(user_profile, scheme):
                score, reasons = self.calculate_relevance_score(user_profile, scheme, scheme_index=idx)

                # Parse documents
                raw_docs = scheme.get('Documents Required', '')
                if pd.notna(raw_docs) and str(raw_docs).strip() and str(raw_docs).strip() != 'nan':
                    docs_list = [d.strip() for d in re.split(r'[,;]\s*', str(raw_docs)) if d.strip()]
                else:
                    docs_list = ['Aadhaar Card', 'Income Certificate', 'Bank Account Passbook']

                # Clean type
                scheme_type_raw = str(scheme.get('Scheme Type', 'Central')).strip()
                if scheme_type_raw.lower() in ('central', 'national'):
                    normalized_type = 'central'
                elif scheme_type_raw.lower() == 'private':
                    normalized_type = 'private'
                else:
                    normalized_type = 'state'

                results.append({
                    'id': str(scheme.get('Scheme Id', f"scheme_{idx}")),
                    'scheme': str(scheme['Scheme Name']).strip(),
                    'type': normalized_type,
                    'scheme_type_raw': scheme_type_raw,
                    'category': str(scheme['Category']).strip(),
                    'desc': str(scheme.get('Description', '')).strip() or str(scheme['Category']).strip(),
                    'benefit': str(scheme.get('Benefit Amount', 'Financial assistance / welfare support')).strip(),
                    'score': round(score, 1),
                    'link': str(scheme.get('Official Application Link', '#')).strip(),
                    'minAge': int(scheme['Min Age']),
                    'maxAge': int(scheme['Max Age']),
                    'gender': str(scheme['Gender']),
                    'occupation': str(scheme['Occupation']),
                    'caste': str(scheme['Caste Category']),
                    'docs': docs_list,
                    'reasons': reasons
                })

        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]

    def get_user_input(self):
        """CLI interactive input helper"""
        print("\n" + "="*50)
        print("YojnaSetu - Government Scheme Recommender")
        print("="*50)
        try:
            name = input("Your name: ").strip() or "Citizen"
            age = int(input("Your age (0-100): ") or "30")
            gender = input("Gender (Male/Female/Transgender/All): ").strip() or "All"
            income = int(input("Annual family income (₹): ") or "100000")
            state = input("State code (e.g. MH, DL, UP, KA, TN) or All: ").strip() or "all"
            occupation = input("Occupation (Student/Farmer/Salaried/Self-employed/Daily Wage/Homemaker/Retired/Unemployed): ").strip() or "Student"

            return {
                'name': name,
                'age': age,
                'gender': gender,
                'income': income,
                'state': state,
                'occupation': occupation,
                'preferred_categories': []
            }
        except (ValueError, KeyboardInterrupt):
            return None


def main():
    predictor = YojnaSetuAIPredictor()
    sample_user = {
        'name': 'Ramesh Kumar',
        'age': 28,
        'gender': 'Male',
        'income': 120000,
        'occupation': 'Farmer',
        'state': 'MH',
        'preferred_categories': ['Agriculture & Farming']
    }
    recs = predictor.get_scheme_recommendations(sample_user, limit=5)
    print(f"\nFound {len(recs)} top recommendations for sample user:")
    for r in recs:
        print(f"- [{r['score']}] {r['scheme']} ({r['category']}) - {r['benefit']}")


if __name__ == '__main__':
    main()
