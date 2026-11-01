# 🇮🇳 YojnaSetu.AI — Connecting Citizens with Government Schemes

**YojnaSetu.AI** is an AI-powered, multilingual government scheme discovery platform designed to bridge the gap between Indian citizens and government welfare schemes.

The platform collects basic information through a guided questionnaire and uses a hybrid Machine Learning and rule-based recommendation engine to identify potentially relevant government schemes.

Its primary objective is simple:

**Help every eligible citizen discover government schemes without complicated searches, registration, or unnecessary paperwork.**

---

## 1. Project Overview

YojnaSetu.AI acts as a bridge between citizens and government welfare schemes.

Citizens provide basic information through a questionnaire. The system analyzes their responses, evaluates scheme eligibility criteria, and presents relevant government schemes with useful information.

### Core Principles

- No citizen registration or login.
- No permanent citizen profiles.
- Temporary, session-based information handling.
- AI and ML-based scheme recommendations.
- Multilingual accessibility.
- Transparent eligibility evaluation.
- Simple and accessible user experience.

---

## 2. Key Features

### 2.1 Smart Citizen Questionnaire
Collect basic information required to identify relevant government schemes, such as:

- Age
- Gender
- State
- Annual family income
- Social category
- Occupation
- Education and other relevant eligibility information

### 2.2 ML-Based Recommendation Engine

A hybrid recommendation engine combines:

- Rule-based eligibility verification.
- Machine Learning classification.
- TF-IDF-based text similarity.
- Scheme relevance scoring.

The engine evaluates questionnaire responses against available scheme information to identify potentially matching schemes.

### 2.3 Government Scheme Information

Display relevant information for each recommended scheme:

- Scheme name
- Scheme description
- Eligibility requirements
- Benefits
- Required documents
- Application procedure
- Official application link

### 2.4 Multilingual Support

The platform supports 10 Indian languages as specified in the current project implementation.

### 2.5 Privacy-First Architecture

- No registration or login.
- No permanent citizen profile creation.
- Questionnaire responses are maintained temporarily in a session.
- Session information expires after 30 minutes.
- Only the information necessary for scheme matching is collected.

---

## 3. System Architecture

The application follows a frontend-backend architecture.

**Frontend**
- React.js
- TypeScript
- Tailwind CSS

**Backend**
- Python
- FastAPI
- SQLAlchemy

**Database**
- PostgreSQL

**Machine Learning**
- Scikit-learn
- Random Forest Classifier
- TF-IDF
- Rule-based eligibility engine

**Dataset**
- Excel-based government scheme dataset.

---

## 4. Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React.js |
| Programming Language | TypeScript |
| Styling | Tailwind CSS |
| Backend | Python |
| API Framework | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Machine Learning | Scikit-learn |
| Data Processing | Pandas, NumPy |
| ML Model | Pretrained `.pkl` model |
| Dataset | Excel `.xlsx` |

---

## 5. Project Structure

```text
yojanasetu_v2/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── stores/
│   │   └── i18n/
│   ├── public/
│   ├── package.json
│   └── ...
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── services/
│   │   ├── models/
│   │   └── ...
│   │
│   ├── data/
│   │   └── yojna_setu_ai_cleaned.xlsx
│   │
│   ├── ml/
│   │   └── yojna_setu_ai_ml_model.pkl
│   │
│   ├── scripts/
│   ├── tests/
│   └── ...
│
└── README.md
```

---

## 6. How the System Works

1. Citizen opens the YojnaSetu.AI platform.
2. Citizen selects their preferred language.
3. Citizen completes the guided questionnaire.
4. The backend receives the questionnaire responses.
5. The recommendation engine evaluates eligibility criteria.
6. The ML engine analyzes scheme relevance.
7. The system generates ranked scheme recommendations.
8. Citizens view matching schemes and their details.
9. Citizens can proceed to the respective official government application websites.

---

## 7. Recommendation Engine

The recommendation engine uses a hybrid approach.

### Rule-Based Eligibility

Evaluates relevant eligibility conditions, including:

- Age requirements
- Income limits
- Gender restrictions
- State eligibility
- Social category
- Occupation
- Other scheme-specific requirements

### Machine Learning

Uses the pretrained ML model and text similarity techniques to support scheme matching and relevance evaluation.

### Recommendation Output

The system presents relevant schemes with:

- Scheme relevance score
- Eligibility information
- Matching reasons
- Scheme benefits
- Application information

Final eligibility and approval remain subject to the respective government department's rules.

---

## 8. Database and Data Management

PostgreSQL is used to manage government scheme information and other required application data.

The master Excel dataset acts as the source for scheme information.

The application must maintain a clear separation between:

**Scheme Data**
- Government scheme details
- Eligibility criteria
- Benefits
- Application information

**Citizen Questionnaire Data**
- Temporary session information
- No permanent citizen profiles
- Automatic session expiration after 30 minutes

---

## 9. Installation and Execution

### Prerequisites

- Python
- Node.js and npm
- PostgreSQL
- Git

### Backend Setup

Navigate to the backend directory.

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI server using the project's configured application entry point.

### Frontend Setup

Navigate to the frontend directory.

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

---

## 10. Testing and Validation

The following areas should be verified before release:

- Frontend functionality.
- Backend API functionality.
- PostgreSQL connectivity.
- Excel dataset loading.
- ML model loading.
- Recommendation engine accuracy.
- Eligibility verification.
- Multilingual functionality.
- Session expiration.
- Frontend-backend integration.
- Error handling and security.

Only verified test results should be reported as passed.

---

## 11. Project Objective

YojnaSetu.AI aims to make government welfare schemes easier to discover and understand.

Instead of requiring citizens to search through multiple government websites, the platform provides a single intelligent interface that connects citizens with potentially relevant schemes.

**YojnaSetu.AI — The Bridge Between People and Government Schemes.**
