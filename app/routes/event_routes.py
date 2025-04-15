from flask import Blueprint, jsonify, request
from app.models import Event, EventRegistration, User, db
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils import admin_required, send_confirmation_email
from datetime import datetime

events_bp = Blueprint('events', __name__, url_prefix="/api/events")

# Create Event (Admin)
@events_bp.route("/", methods=["POST"])
@jwt_required()
@admin_required
def create_event():
    data = request.get_json()
    event = Event(
        title=data["title"],
        description=data["description"],
        date=datetime.strptime(data["date"], "%Y-%m-%d %H:%M"),
        location=data["location"],
        category=data["category"],
        max_attendees=data["max_attendees"],
        created_by=get_jwt_identity()
    )
    db.session.add(event)
    db.session.commit()
    return {"message": "Event created", "id": event.id}, 201

# List Events with Filters
@events_bp.route("/", methods=["GET"])
def list_events():
    query = Event.query
    category = request.args.get("category")
    location = request.args.get("location")
    date = request.args.get("date")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))

    if category:
        query = query.filter_by(category=category)
    if location:
        query = query.filter_by(location=location)
    if date:
        query = query.filter(Event.date >= datetime.strptime(date, "%Y-%m-%d"))

    events = query.order_by(Event.date.asc()).paginate(page=page, per_page=per_page)
    result = [{
        "id": e.id,
        "title": e.title,
        "description": e.description,
        "date": e.date.strftime("%Y-%m-%d %H:%M"),
        "location": e.location,
        "category": e.category,
        "max_attendees": e.max_attendees
    } for e in events.items]

    return {
        "events": result,
        "total": events.total,
        "page": page,
        "pages": events.pages
    }

# Get Event by ID
@events_bp.route("/<int:event_id>", methods=["GET"])
def get_event(event_id):
    event = Event.query.get_or_404(event_id)
    return {
        "id": event.id,
        "title": event.title,
        "description": event.description,
        "date": event.date.strftime("%Y-%m-%d %H:%M"),
        "location": event.location,
        "category": event.category,
        "max_attendees": event.max_attendees
    }

# Update Event (Admin)
@events_bp.route("/<int:event_id>", methods=["PUT"])
@jwt_required()
@admin_required
def update_event(event_id):
    data = request.get_json()
    event = Event.query.get_or_404(event_id)
    event.title = data.get("title", event.title)
    event.description = data.get("description", event.description)
    event.date = datetime.strptime(data["date"], "%Y-%m-%d %H:%M") if "date" in data else event.date
    event.location = data.get("location", event.location)
    event.category = data.get("category", event.category)
    event.max_attendees = data.get("max_attendees", event.max_attendees)
    db.session.commit()
    return {"message": "Event updated"}

# Delete Event (Admin)
@events_bp.route("/<int:event_id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return {"message": "Event deleted"}

@events_bp.route("/<int:event_id>/rsvp", methods=["POST"])
@jwt_required()
def rsvp_event(event_id):
    user_id = get_jwt_identity()  # Get the user ID from the JWT token
    user = User.query.get(user_id)  # Fetch the user from the database

    if not user:
        return jsonify({"message": "User not found"}), 404

    event = Event.query.get(event_id)  # Fetch the event from the database
    if not event:
        return jsonify({"message": "Event not found"}), 404

    # Check if the user has already RSVPed to the event
    if event in user.events:
        return jsonify({"message": "You have already RSVPed to this event"}), 400

    # Add the user to the event's attendee list
    event.attendees.append(user)
    db.session.commit()

    # Send a confirmation email (make sure you're passing the event here)
    send_confirmation_email(user, event)

    return jsonify({"message": "RSVP successful!"}), 200

