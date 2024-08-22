from flask_appbuilder.api import expose, BaseApi
from flask_appbuilder.security.decorators import protect
from db_service.app.helper_classes.return_responses import APIResponse
from db_service.app.helper_classes.zoom_helper_class import *
from flask import request, jsonify
from datetime import datetime
from db_service.app import appbuilder, db
from db_service.app.models.core_entities_models.meeting import Meeting


@expose("public")
class ZoomApi(BaseApi):
    resource_name = 'zoom'

    @protect()
    class Meta:
        pass

    @expose('/createMeeting', methods=['GET'])
    def createMeeting(self):
        token_response = get_access_token()
        access_token = token_response.get("access_token")
        data = request.get_json()

        if not access_token:
            print("Failed to get access token.")
            return self.response(500, **APIResponse.construct_response(500, 'Failed to get access token'))

        # Step 2: List users (and select one)
        users_info = list_zoom_users(access_token)
        user_id = users_info['users'][0]['id']  # Assuming you want the first user

        if not user_id:
            print("Failed to retrieve user information.")
            return self.response(500, **APIResponse.construct_response(500, 'Failed to retrieve user information'))

        topic = data.get('topic')
        start_time = data.get('start_time')
        duration = data.get('duration')

        # Step 3: Create a Zoom meeting
        meeting_info = create_zoom_meeting(access_token, user_id, topic, start_time, duration)
        print(meeting_info)
        meeting_data = {
            'meeting_id': meeting_info['id'],
            'uuid': meeting_info['uuid'],
            'topic': meeting_info['topic'],
            'start_time': datetime.fromisoformat(meeting_info['start_time'][:-1]),
            'duration': meeting_info['duration'],
            'timezone': meeting_info['timezone'],
            'agenda': meeting_info['agenda'],
            'created_at': datetime.fromisoformat(meeting_info['created_at'][:-1]),
            'start_url': meeting_info['start_url'],
            'join_url': meeting_info['join_url'],
            'encrypted_password': meeting_info['encrypted_password'],
        }

        # Create a new Meeting object
        new_meeting = Meeting(**meeting_data)

        # Save to the database
        db.session.add(new_meeting)
        db.session.commit()

        # Generate the URLs
        meeting_id = new_meeting.meeting_id
        url_one = f"jesica.ai/interview/{meeting_id}/1"
        url_zero = f"jesica.ai/interview/{meeting_id}/0"

        # Prepare the response with both URLs
        response_data = {
            "message": "meeting created successfully",
            "host": url_one,
            "candidate": url_zero
        }

        return self.response(200, **APIResponse.construct_response(200, response_data))

    @expose('/create/<int:meeting_id>/<int:role>', methods=['GET'])
    def get_meeting_info(self, meeting_id, role):
        # Query the meeting using the meeting_id from the URL
        meeting = db.session.query(Meeting.meeting_id, Meeting.encrypted_password).filter_by(
            meeting_id=meeting_id).first()

        if not meeting:
            return jsonify({"error": "Meeting not found"}), 404

        # Extract the meeting_id and encrypted_password from the result
        password = meeting.encrypted_password
        if role == 1:

            user_name = "interviewee"
        else:
            user_name = "candidate"

        user_email = ""

        response_data = construct_zoom_sdk_payload(meeting_id, role, user_name, password)

        return self.response(200, **APIResponse.construct_response(200, response_data))
