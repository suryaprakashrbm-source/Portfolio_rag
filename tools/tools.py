import datetime
import json
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH = os.path.join(BASE_DIR, "token.json")
CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials.json")


def get_calendar_service():
    """Authenticates and returns the Google Calendar API service instance."""
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_PATH):
                raise FileNotFoundError(f"Missing credentials.json at {CREDENTIALS_PATH}")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())
    return build("calendar", "v3", credentials=creds)


def get_upcoming_events(max_results: int = 10) -> str:
    """Fetches upcoming events and availability from Surya's primary Google Calendar."""
    try:
        service = get_calendar_service()
        now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])
        if not events:
            return "Surya has no upcoming events scheduled on the calendar right now."

        formatted_events = []
        for i, event in enumerate(events, start=1):
            start = event["start"].get("dateTime", event["start"].get("date"))
            end = event["end"].get("dateTime", event["end"].get("date"))
            summary = event.get("summary", "(Busy / Scheduled)")
            location = event.get("location", "")
            details = f"{i}. Event: {summary} | From: {start} to {end}"
            if location:
                details += f" | Location: {location}"
            formatted_events.append(details)

        return "\n".join(formatted_events)
    except Exception as e:
        return f"Error retrieving calendar events: {str(e)}"


def book_meeting(
    summary: str,
    start_time: str,
    end_time: str,
    description: str = "",
    attendee_email: str = "",
    timezone: str = "Asia/Kolkata",
) -> str:
    """Schedules a new meeting on Surya's Google Calendar.

    Args:
        summary: Title/Topic of the meeting (e.g., 'Discussion with Recruiter').
        start_time: Start datetime in ISO 8601 format (e.g., '2026-10-05T15:00:00') or 'YYYY-MM-DD'.
        end_time: End datetime in ISO 8601 format (e.g., '2026-10-05T15:30:00') or 'YYYY-MM-DD'.
        description: Agenda, notes, or contact info.
        attendee_email: Email address of the person booking the meeting.
        timezone: Timezone string (default 'Asia/Kolkata').
    """
    try:
        service = get_calendar_service()
        event_body = {
            "summary": summary,
            "description": description,
        }

        if attendee_email:
            event_body["attendees"] = [{"email": attendee_email}]

        if "T" in start_time:
            event_body["start"] = {
                "dateTime": start_time if start_time.endswith("Z") or "+" in start_time else f"{start_time}+05:30",
                "timeZone": timezone,
            }
            event_body["end"] = {
                "dateTime": end_time if end_time.endswith("Z") or "+" in end_time else f"{end_time}+05:30",
                "timeZone": timezone,
            }
        else:
            event_body["start"] = {"date": start_time}
            event_body["end"] = {"date": end_time}

        created = service.events().insert(calendarId="primary", body=event_body).execute()
        return (
            f"Meeting booked successfully!\n"
            f"- Title: {created.get('summary')}\n"
            f"- Link: {created.get('htmlLink')}\n"
            f"- Event ID: {created.get('id')}"
        )
    except Exception as e:
        return f"Error booking meeting: {str(e)}"


# Groq / OpenAI compatible Tool Schemas
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_upcoming_events",
            "description": "Check Surya's upcoming schedule, meetings, or calendar availability.",
            "parameters": {
                "type": "object",
                "properties": {
                    "max_results": {
                        "type": "integer",
                        "description": "Number of upcoming events to retrieve (default is 10).",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "book_meeting",
            "description": "Book or schedule a meeting/call on Surya's Google Calendar with a visitor, client, or recruiter.",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": "Topic or title of the meeting (e.g. 'Intro Call with Surya').",
                    },
                    "start_time": {
                        "type": "string",
                        "description": "Start ISO 8601 datetime (e.g. '2026-10-02T15:00:00') or date 'YYYY-MM-DD'.",
                    },
                    "end_time": {
                        "type": "string",
                        "description": "End ISO 8601 datetime (e.g. '2026-10-02T15:30:00') or date 'YYYY-MM-DD'.",
                    },
                    "description": {
                        "type": "string",
                        "description": "Meeting agenda, notes, or purpose.",
                    },
                    "attendee_email": {
                        "type": "string",
                        "description": "Email of the attendee/visitor booking the meeting.",
                    },
                },
                "required": ["summary", "start_time", "end_time"],
            },
        },
    },
]


def execute_tool(tool_name: str, arguments: dict) -> str:
    """Executes the requested tool by name with arguments and returns string response."""
    if tool_name == "get_upcoming_events":
        max_results = arguments.get("max_results", 10)
        return get_upcoming_events(max_results=max_results)
    elif tool_name == "book_meeting":
        return book_meeting(**arguments)
    else:
        return f"Unknown tool: {tool_name}"
