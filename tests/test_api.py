import pytest
import json
from backend.yojnasetu_api import app, generate_token


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    """Test health check returns status ok and database connected"""
    res = client.get('/api/health')
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'ok'
    assert data['database'] == 'connected'
    assert data['schemes_in_db'] >= 450
    assert data['model_loaded'] is True


def test_recommend_endpoint(client):
    """Test recommendation POST endpoint"""
    payload = {
        'name': 'Rahul Verma',
        'age': 29,
        'gender': 'Male',
        'income': 150000,
        'occupation': 'Farmer',
        'state': 'MH',
        'category': 'OBC',
        'limit': 15
    }
    res = client.post('/api/recommend', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'success'
    assert data['count'] > 0
    assert len(data['recommendations']) <= 15
    assert data['recommendations'][0]['score'] >= 50


def test_list_schemes_endpoint(client):
    """Test schemes list with pagination and filtering"""
    res = client.get('/api/schemes?page=1&limit=10&type=central')
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'success'
    assert data['page'] == 1
    assert data['limit'] == 10
    assert len(data['schemes']) <= 10


def test_scheme_detail_endpoint(client):
    """Test individual scheme detail fetch"""
    # Fetch list first to obtain a valid scheme_id
    list_res = client.get('/api/schemes?limit=1')
    first_scheme = list_res.get_json()['schemes'][0]
    scheme_id = first_scheme['id']

    res = client.get(f'/api/schemes/{scheme_id}')
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'success'
    assert data['scheme']['name'] == first_scheme['name']


def test_auth_otp_flow(client):
    """Test OTP sending and verification"""
    # 1. Send OTP
    send_res = client.post('/api/auth/send-otp', json={
        'type': 'phone',
        'identifier': '9123456789'
    })
    assert send_res.status_code == 200
    send_data = send_res.get_json()
    assert send_data['status'] == 'success'
    demo_otp = send_data.get('demo_otp', '123456')

    # 2. Verify with invalid OTP
    bad_verify = client.post('/api/auth/verify-otp', json={
        'type': 'phone',
        'identifier': '9123456789',
        'otp': '000000'
    })
    assert bad_verify.status_code == 401

    # 3. Verify with valid OTP
    good_verify = client.post('/api/auth/verify-otp', json={
        'type': 'phone',
        'identifier': '9123456789',
        'otp': demo_otp
    })
    assert good_verify.status_code == 200
    good_data = good_verify.get_json()
    assert 'token' in good_data
    assert good_data['user']['identifier'] == '9123456789'


def test_saved_schemes_requires_auth(client):
    """Test that saved schemes endpoints block unauthenticated requests"""
    res = client.get('/api/user/saved-schemes')
    assert res.status_code == 401


def test_saved_schemes_crud(client):
    """Test saved schemes adding, listing, and deletion with valid auth token"""
    token = generate_token("test_api_user_123")
    auth_header = {'Authorization': f'Bearer {token}'}

    # 1. Save scheme
    save_res = client.post('/api/user/saved-schemes', headers=auth_header, json={
        'scheme_id': 'test_api_scheme_01',
        'scheme_name': 'Test Scheme API',
        'category': 'Education',
        'benefit': 'Scholarship ₹10,000',
        'link': 'https://scholarships.gov.in'
    })
    assert save_res.status_code in (200, 201)

    # 2. List saved schemes
    list_res = client.get('/api/user/saved-schemes', headers=auth_header)
    assert list_res.status_code == 200
    list_data = list_res.get_json()
    assert list_data['count'] >= 1
    assert any(s['scheme_id'] == 'test_api_scheme_01' for s in list_data['saved_schemes'])

    # 3. Delete saved scheme
    del_res = client.delete('/api/user/saved-schemes/test_api_scheme_01', headers=auth_header)
    assert del_res.status_code == 200


def test_security_headers(client):
    """Ensure standard HTTP security headers are included on all responses"""
    res = client.get('/api/health')
    assert res.headers.get('X-Content-Type-Options') == 'nosniff'
    assert res.headers.get('X-Frame-Options') == 'SAMEORIGIN'
    assert res.headers.get('X-XSS-Protection') == '1; mode=block'
