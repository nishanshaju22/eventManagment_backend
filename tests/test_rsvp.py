from flask_jwt_extended import create_access_token


def test_rsvp_event(client, db, create_user):
    user = create_user("rsvpuser", "rsvp@example.com", "pass")
    token = create_access_token(identity=user.id)
    headers = {'Authorization': f'Bearer {token}'}

    # Create event manually
    from app.models import Event
    from datetime import datetime
    event = Event(
        title="Event A",
        description="Test RSVP",
        date=datetime.now(),
        location="Venue",
        category="Seminar",
        max_attendees=10,
        created_by=user.id
    )
    db.session.add(event)
    db.session.commit()

    res = client.post(f'/api/events/{event.id}/rsvp', headers=headers)
    assert res.status_code == 201
    assert b'Successfully registered' in res.data