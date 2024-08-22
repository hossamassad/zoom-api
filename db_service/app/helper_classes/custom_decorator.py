import functools
import logging
from typing import Callable, List, Optional, TypeVar, Union

from flask import (
    current_app,
    flash,
    jsonify,
    make_response,
    redirect,
    request,
    Response,
    url_for,
)
from flask_appbuilder._compat import as_unicode
from flask_appbuilder.const import (
    FLAMSG_ERR_SEC_ACCESS_DENIED,
    LOGMSG_ERR_SEC_ACCESS_DENIED,
    PERMISSION_PREFIX,
)
from flask_appbuilder.utils.limit import Limit
from flask_jwt_extended import verify_jwt_in_request
from flask_limiter.wrappers import RequestLimit
from flask_login import current_user
from typing_extensions import ParamSpec

log = logging.getLogger(__name__)

R = TypeVar("R")
P = ParamSpec("P")

import asyncio
def protect_async(allow_browser_login=False):
    """
    Use this decorator to enable granular security permissions
    to your API methods (BaseApi and child classes).
    Permissions will be associated to a role, and roles are associated to users.

    allow_browser_login will accept signed cookies obtained from the normal MVC app::

        class MyApi(BaseApi):
            @expose('/dosonmething', methods=['GET'])
            @protect(allow_browser_login=True)
            @safe
            def do_something(self):
                ....

            @expose('/dosonmethingelse', methods=['GET'])
            @protect()
            @safe
            def do_something_else(self):
                ....

    By default the permission's name is the methods name.
    """

    def _protect(f):
        if hasattr(f, "_permission_name"):
            permission_str = f._permission_name
        else:
            permission_str = f.__name__

        async def wraps(self, *args, **kwargs):
            # Apply method permission name override if exists
            permission_str = f"{PERMISSION_PREFIX}{f._permission_name}"
            if self.method_permission_name:
                _permission_name = self.method_permission_name.get(f.__name__)
                if _permission_name:
                    permission_str = f"{PERMISSION_PREFIX}{_permission_name}"
            class_permission_name = self.class_permission_name
            # Check if permission is allowed on the class
            if permission_str not in self.base_permissions:
                return self.response_403()
            # Check if the resource is public
            if current_app.appbuilder.sm.is_item_public(
                    permission_str, class_permission_name
            ):
                return await f(self, *args, **kwargs)
            # if no browser login then verify JWT
            if not (self.allow_browser_login or allow_browser_login):
                verify_jwt_in_request()
            # Verify resource access
            if current_app.appbuilder.sm.has_access(
                    permission_str, class_permission_name
            ):
                return await f(self, *args, **kwargs)
            # If browser login?
            elif self.allow_browser_login or allow_browser_login:
                # no session cookie (but we allow it), then try JWT
                if not current_user.is_authenticated:
                    verify_jwt_in_request()
                if current_app.appbuilder.sm.has_access(
                        permission_str, class_permission_name
                ):
                    return await f(self, *args, **kwargs)
            log.warning(
                LOGMSG_ERR_SEC_ACCESS_DENIED.format(
                    permission_str, class_permission_name
                )
            )
            return self.response_403()

        f._permission_name = permission_str
        return functools.update_wrapper(wraps, f)

    return _protect
