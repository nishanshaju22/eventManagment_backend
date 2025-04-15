from flask_jwt_extended import create_access_token


def test_create_event(client, db, create_user):
    admin = create_user("admin", "admin@example.com", "adminpass", is_admin=True)
    token = create_access_token(identity=admin.id)
    headers = {'Authorization': f'Bearer {token}'}
    
    res = client.post('/api/events/', headers=headers, json={
        "title": "Test Event",
        "description": "This is a test event.",
        "date": "2025-04-30 10:00",
        "location": "Online",
        "category": "Workshop",
        "max_attendees": 50
    })
    assert res.status_code == 201
    assert b'Event created' in res.data

def test_list_events(client):
    res = client.get('/api/events/')
    assert res.status_code == 200
    assert 'events' in res.json