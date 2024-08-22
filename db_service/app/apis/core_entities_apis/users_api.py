from flask_appbuilder.api import expose, BaseApi
from flask_appbuilder.security.decorators import protect
from db_service.app import appbuilder, db
from flask import g
from db_service.app.helper_classes.return_responses import APIResponse
from flask import request, jsonify
from flask_appbuilder.security.sqla.models import User, Role
from sqlalchemy.exc import IntegrityError
from db_service.app.models.core_entities_models.user_extend import Supervisor

@expose("public")
class CustomSecurityApi(BaseApi):
    resource_name = 'users'

    @protect()
    class Meta:
        pass

    @expose('/current_user', methods=['GET'])
    @protect()
    def get_current_user(self):
        logged_in_user = g.user
        user_dict = {
            'id': logged_in_user.id,
            'username': logged_in_user.username,
            'email': logged_in_user.email
        }
        return self.response(200,
                         **APIResponse.construct_response(200, 'User retrieved successfully', user_dict))

    @expose('/get_users', methods=['GET'])
    @protect()
    def get_all_users(self):
        session = db.session
        query_result = session.query(User.id, User.username, User.email).all()
        users = [user._asdict() for user in query_result]
        session.close()
        return self.response(200,
                             **APIResponse.construct_response(200, 'Users retrieved successfully', users))

    @expose('/register_user', methods=['POST'])
    def create_user(self):
        data = request.get_json()
        role_name = data.get('role_name')
        role_public = appbuilder.sm.find_role(role_name)
        role = db.session.query(Role).filter_by(name=role_name).first()
        if role is None:
            return jsonify({'error': 'Role not found'}), 404

        supervisor_username = data.get('supervisor_username')
        supervisor = db.session.query(User).filter_by(username=supervisor_username).first()
        if supervisor is None:
            return jsonify({'error': 'Supervisor not found'}), 404

        try:
            # Use appbuilder.sm.add_user to create the user
            new_user = appbuilder.sm.add_user(
            data.get("username"), data.get("first_name"), data.get("last_name"),
            data.get("email"), role_public, data.get("password")
        )

            if new_user is None or not new_user:
                return jsonify({'error': 'Username already exists'}), 400

            new_supervisor = Supervisor(user=new_user, supervisor=supervisor)
            db.session.add(new_supervisor)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({'error': 'An error occurred while creating the user'}), 400

        return self.response(200, **APIResponse.construct_response(200, 'User created successfully'))

    @expose('/remove_user', methods=['POST'])
    def remove_user(self):
        data = request.get_json()
        username = data.get('username')

        # Query the user
        user = db.session.query(User).filter_by(username=username).first()
        if user is None:
            return jsonify({'error': 'User not found'}), 404

        try:
            # Use appbuilder.sm.del_register_user to delete the user
            if not appbuilder.sm.del_register_user(user):
                return jsonify({'error': 'An error occurred while deleting the user'}), 400

            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({'error': 'An error occurred while deleting the user'}), 400

        return self.response(200, **APIResponse.construct_response(200, 'User deleted successfully'))
