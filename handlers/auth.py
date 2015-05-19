# -*- coding: utf-8 -*-
from handlers.base import BaseHandler, BaseSockJSHandler
import json


class AuthSockJSHandler(BaseSockJSHandler):

    def on_open(self, request):
        super(AuthSockJSHandler, self).on_open(request)
        # self.current_user = None

    def on_message(self, message):
        super(AuthSockJSHandler, self).on_message(message)
        data = self._message_json

        # Ignore all packets except of 'auth' if user is not yet authenticated
        auth_sid = data.get('auth') if data is not None else None
        if not self.project_session and not auth_sid:
            response = json.dumps({'user': 'system', 'status': 'error', 'text': 'Session id does not exist!'})
            self.send(response)
            self.close()
            raise ValueError(message)

        if auth_sid:
            self._sid = auth_sid
            if not self.project_session:
                response = json.dumps({'user': 'system', 'status': 'error', 'text': 'Invalid session id!'})
                self.send(response)
                self.close()
                raise ValueError(response)
#             user = self.project_session.get('user')
# 1
#             if user is None or not user.is_active:
#                 self.send('error,Invalid user!')
#                 return
#                 self
#
#             self.current_user = user
