import requests
import requests.auth
import jwt
import time
import hashlib
import hmac
import base64
from db_service.app.config import ZoomConfig

CLIENT_ID = ZoomConfig.CLIENT_ID
CLIENT_SECRET = ZoomConfig.CLIENT_SECRET
ACCOUNT_ID = ZoomConfig.ACCOUNT_ID
SDK_KEY = ZoomConfig.SDK_KEY  # Ensure this key is valid and correct length
SDK_SECRET = ZoomConfig.SDK_SECRET  # Ensure this secret is valid

def generate_jwt_token():
    """
    Generate a JWT token for server-to-server OAuth flow.
    """
    header = {
        "alg": "HS256",
        "typ": "JWT"
    }

    payload = {
        "iss": CLIENT_ID,
        "exp": int(time.time()) + 3600,  # Token expires in 1 hour
        "aud": "https://api.zoom.us"
    }

    token = jwt.encode(payload, CLIENT_SECRET, algorithm="HS256", headers=header)
    return token if isinstance(token, str) else token.decode('utf-8')  # Ensure it's a string


def get_access_token():
    """
    Use the JWT token to get an access token from Zoom's server-to-server OAuth endpoint.
    """
    token_url = "https://zoom.us/oauth/token"
    headers = {
        "Authorization": f"Bearer {generate_jwt_token()}",  # Use Bearer instead of Basic
    }
    data = {
        "grant_type": "account_credentials",
        "account_id": ACCOUNT_ID
    }
    response = requests.post(token_url, headers=headers, data=data)

    # Debugging output
    print(f"Response Status Code: {response.status_code}")
    print(f"Response Content: {response.text}")

    return response.json()


def get_zoom_user_info(access_token, user_id):
    """
    Retrieve user information from Zoom using the access token.
    """
    user_info_url = f"https://api.zoom.us/v2/users/{user_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    response = requests.get(user_info_url, headers=headers)
    print(f"User Info Status Code: {response.status_code}")  # Debugging
    return response.json()


def list_zoom_users(access_token):
    """
    List users in the Zoom account.
    """
    users_url = "https://api.zoom.us/v2/users"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    response = requests.get(users_url, headers=headers)
    print(f"List Users Status Code: {response.status_code}")  # Debugging
    return response.json()


def create_zoom_meeting(access_token, user_id, topic, start_time, duration):
    """
    Create a Zoom meeting for the authenticated user.
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    meeting_details = {
        "topic": topic,
        "type": 2,  # Scheduled meeting
        "start_time": start_time,  # Example start time in UTC
        "duration": duration,  # Duration in minutes
        "timezone": "UTC",
        "agenda": "Test Agenda",
        "settings": {
            "host_video": True,
            "participant_video": True,
            "mute_upon_entry": False,
            "waiting_room": False,
            "join_before_host": True,  # Allow participants to join before the host
            "jbh_time": 0,
            "auto_recording": "cloud",
        }
    }

    response = requests.post(f"https://api.zoom.us/v2/users/{user_id}/meetings",
                             headers=headers,
                             json=meeting_details)

    return response.json()


def generate_zoom_sdk_signature(meeting_number, role):
    """
    Generate a JWT signature for Zoom Meeting SDK.
    """
    iat = int(time.time()) - 30  # Issued at time, 30 seconds in the past
    exp = iat + 60 * 60 * 2  # Expiration time (2 hours from iat)

    # Payload for the JWT
    payload = {
        "sdkKey": SDK_KEY,
        "mn": meeting_number,
        "role": role,
        "iat": iat,
        "exp": exp,
        "appKey": SDK_KEY,
        "tokenExp": exp
    }

    try:
        # Encode the JWT with the given secret
        sdk_jwt = jwt.encode(payload, SDK_SECRET, algorithm='HS256')
        return sdk_jwt
    except Exception as e:
        print(f"Error generating JWT signature: {e}")
        return None


def construct_zoom_sdk_payload(meeting_number, role, user_name="Default Name", password=""):
    """
    Constructs the payload required for the Zoom Web SDK to join a meeting.

    Parameters:
        meeting_number (str): The Zoom meeting number (ID).
        role (int): Role of the user (0 for participant, 1 for host).
        user_name (str): The name of the user joining the meeting.
        user_email (str): The email of the user (optional).
        password (str): The meeting password (if any).

    Returns:
        dict: A dictionary containing the payload.
    """

    # Generate the meeting signature
    signature = generate_zoom_sdk_signature(meeting_number, role)

    # Construct the payload
    payload = {
        "sdkKey": SDK_KEY,
        "signature": signature,
        "meetingNumber": meeting_number,
        "userName": user_name,
        "passWord": password,
    }

    return payload
