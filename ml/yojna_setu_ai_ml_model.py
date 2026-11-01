import os
import sys
import pickle
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.svm import SVC

warnings.filterwarnings('ignore')

# Set safe standard output encoding
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATA_PATH = BASE_DIR / 'data' / 'yojna_setu_ai_cleaned.xlsx'
DEFAULT_MODEL_PATH = BASE_DIR / 'ml' / 'models' / 'yojna_setu_ai_ml_model.pkl'


class YojnaSetuAIML:
    def __init__(self, data_path=None):
        if data_path is None:
            self.data_path = DEFAULT_DATA_PATH
        else:
            self.data_path = Path(data_path)

        self.df = None
        self.models = {}
        self.encoders = {}
        self.scaler = StandardScaler()
        self.vectorizer = TfidfVectorizer(max_features=100, stop_words='english')

    def load_data(self):
        """Load and preprocess the dataset"""
        print(f"Loading dataset from: {self.data_path}")
        if not self.data_path.exists():
            raise FileNotFoundError(f"Dataset not found at {self.data_path}")

        self.df = pd.read_excel(self.data_path)

        # Basic data cleaning
        self.df = self.df.dropna(subset=['Category'])
        self.df = self.df.fillna({
            'Min Age': self.df['Min Age'].median(),
            'Max Age': self.df['Max Age'].median(),
            'Min Income': 0,
            'Max Income': self.df['Max Income'].median(),
            'Description': '',
            'Benefit Amount': 'Not Specified',
            'Gender': 'All',
            'Occupation': 'All',
            'Caste Category': 'All'
        })

        print(f"Dataset loaded: {self.df.shape[0]} schemes, {self.df.shape[1]} features")
        return self.df

    def preprocess_features(self):
        """Preprocess and engineer features for ML"""
        print("Preprocessing features...")

        categorical_cols = [
            'Scheme Provider Type', 'Scheme Type', 'Gender',
            'Caste Category', 'Occupation', 'Education Required',
            'Application Mode'
        ]

        for col in categorical_cols:
            if col in self.df.columns:
                self.encoders[col] = LabelEncoder()
                self.df[f'{col}_encoded'] = self.encoders[col].fit_transform(
                    self.df[col].astype(str)
                )

        # Process text features
        if 'Description' in self.df.columns:
            desc_vectors = self.vectorizer.fit_transform(self.df['Description'])
            desc_df = pd.DataFrame(
                desc_vectors.toarray(),
                columns=[f'desc_{i}' for i in range(desc_vectors.shape[1])]
            )
            self.df = pd.concat([self.df, desc_df], axis=1)

        # Numerical features
        numerical_features = ['Min Age', 'Max Age', 'Min Income', 'Max Income']
        if all(col in self.df.columns for col in numerical_features):
            self.df[numerical_features] = self.scaler.fit_transform(self.df[numerical_features])

        return self.df

    def build_category_classifier(self):
        """Build a classifier to predict scheme categories"""
        print("Building category classification model...")

        feature_cols = [
            col for col in self.df.columns
            if col.endswith('_encoded') or col.startswith('desc_')
            or col in ['Min Age', 'Max Age', 'Min Income', 'Max Income']
        ]

        X = self.df[feature_cols]
        y = self.df['Category']

        self.encoders['Category'] = LabelEncoder()
        y_encoded = self.encoders['Category'].fit_transform(y)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42
        )

        models = {
            'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
            'SVM': SVC(kernel='rbf', random_state=42, probability=True)
        }

        best_model = None
        best_name = None
        best_score = -1.0

        for name, model in models.items():
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            print(f"{name} Accuracy: {accuracy:.3f}")

            if accuracy > best_score:
                best_score = accuracy
                best_model = model
                best_name = name

        self.models['category_classifier'] = {
            'model': best_model,
            'name': best_name,
            'encoder': self.encoders['Category'],
            'features': feature_cols,
            'accuracy': float(best_score)
        }

        print(f"Best model: {best_name} with accuracy {best_score:.3f}")
        return self.models['category_classifier']

    def build_eligibility_predictor(self):
        """Build a model to predict user eligibility for schemes"""
        print("Building eligibility prediction rule-checker...")

        def check_eligibility(user_profile, scheme):
            age = user_profile.get('age', 30)
            if not (scheme.get('Min Age', 0) <= age <= scheme.get('Max Age', 100)):
                return False

            user_gender = user_profile.get('gender', 'All')
            scheme_gender = scheme.get('Gender', 'All')
            if scheme_gender not in ('All', 'any') and user_gender not in ('All', 'Prefer Not To Say', 'prefer_not_to_say'):
                if scheme_gender.lower() != user_gender.lower():
                    return False

            user_income = user_profile.get('income', 50000)
            if not (scheme.get('Min Income', 0) <= user_income <= scheme.get('Max Income', 10000000)):
                return False

            return True

        self.models['eligibility_checker'] = check_eligibility
        return check_eligibility

    def predict_category(self, feature_dict):
        """Predict scheme category using the trained classification model"""
        if 'category_classifier' not in self.models:
            print("Category classifier not trained yet!")
            return None

        model_data = self.models['category_classifier']
        model = model_data['model']
        encoder = model_data['encoder']
        feature_cols = model_data['features']

        # Construct vector
        row = {}
        for col in feature_cols:
            row[col] = feature_dict.get(col, 0)
        input_df = pd.DataFrame([row])[feature_cols]

        pred_idx = model.predict(input_df)[0]
        return encoder.inverse_transform([pred_idx])[0]

    def save_model(self, filename=None):
        """Save the trained models and preprocessors"""
        if filename is None:
            filename = DEFAULT_MODEL_PATH
        else:
            filename = Path(filename)

        filename.parent.mkdir(parents=True, exist_ok=True)

        models_to_save = {}
        for key, value in self.models.items():
            if key != 'eligibility_checker':
                models_to_save[key] = value

        with open(filename, 'wb') as f:
            pickle.dump({
                'models': models_to_save,
                'encoders': self.encoders,
                'scaler': self.scaler,
                'vectorizer': self.vectorizer,
                'feature_columns': self.df.columns.tolist()
            }, f)
        print(f"Model saved to {filename}")


def train_and_export():
    ml = YojnaSetuAIML()
    ml.load_data()
    ml.preprocess_features()
    ml.build_category_classifier()
    ml.build_eligibility_predictor()
    ml.save_model()
    return ml


if __name__ == '__main__':
    train_and_export()
