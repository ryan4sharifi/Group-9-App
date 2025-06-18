from fastapi import APIRouter, HTTPException
from app.supabase_client import supabase

router = APIRouter()


def fetch_user_skills(user_id: str) -> set:
    """Fetches the skill set of a user based on user_id."""
    response = supabase.table("user_profiles").select("skills").eq("user_id", user_id).execute()
    if not response or not response.data:
        raise HTTPException(status_code=404, detail="User profile not found")

    skills_raw = response.data[0].get("skills", [])
    return set(skills_raw if isinstance(skills_raw, list) else [])


def fetch_all_events() -> list:
    """Fetches all events from the database."""
    response = supabase.table("events").select("*").execute()
    return response.data if response and response.data else []


@router.get("/match-and-notify/{user_id}")
async def match_and_notify(user_id: str) -> dict:
    """
    Matches a user to events based on skills and sends notifications if a new match is found.
    """
    try:
        user_skills = fetch_user_skills(user_id)
        all_events = fetch_all_events()

        matched_events = []

        for event in all_events:
            event_skills = set(event.get("required_skills", []))

            if user_skills.intersection(event_skills):
                matched_events.append(event)

                # Prevent duplicate notifications
                existing_notif = supabase.table("notifications") \
                    .select("id") \
                    .eq("user_id", user_id) \
                    .eq("event_id", event["id"]) \
                    .execute()

                if not existing_notif.data:
                    supabase.table("notifications").insert({
                        "user_id": user_id,
                        "event_id": event["id"],
                        "message": f"You've been matched with: {event['name']}",
                        "is_read": False
                    }).execute()

        return {"matched_events": matched_events}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/matched_events/{user_id}")
async def get_matched_events(user_id: str) -> dict:
    """
    Returns matched events for a user based on skill intersection. No notifications are sent.
    """
    try:
        user_skills = fetch_user_skills(user_id)
        all_events = fetch_all_events()

        matched_events = [
            event for event in all_events
            if user_skills.intersection(set(event.get("required_skills", [])))
        ]

        return {"matched_events": matched_events}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))