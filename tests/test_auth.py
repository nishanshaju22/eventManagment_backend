def test_register_user(client):
    res = client.post('/api/auth/register', json={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123'
    })
    assert res.status_code == 201
    assert b'registered successfully' in res.data

def test_login_user(client, create_user):
    create_user("loginuser", "login@example.com", "mypassword")
    res = client.post('/api/auth/login', json={
        'email': 'login@example.com',
        'password': 'mypassword'
    })
    assert res.status_code == 200
    assert b'access_token' in res.data