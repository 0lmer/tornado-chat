# -*- coding: utf-8 -*-
import json
from core.handlers.base import BaseHandler, BaseSockJSHandler
from core.models import User
import tornado
import tornado.gen
from tornado.web import decode_signed_value
from settings import settings


class LoginHandler(BaseHandler):

    def get(self):
        self.render('core/login.html')

    @tornado.gen.coroutine
    def post(self):
        login = self.get_argument("login")
        password = self.get_argument("password")
        user = yield User.get_by_login_password(login=login, password=password)
        self.set_secure_cookie("user", self.get_argument("login"))
        self.get_user_from_cookies = lambda : self.get_argument("login")
        session = self.project_session
        session['current_user'] = user
        session.save()
        self.redirect(self.get_argument("next", default="/"))


class RegisterHandler(BaseHandler):

    def get(self):
        self.render('core/register.html')

    @tornado.gen.coroutine
    def post(self):
        login = self.get_argument("login")
        password = self.get_argument("password")
        password_confirm = self.get_argument("password_confirm")
        if len(password) >= 4 and (password == password_confirm):
            users = yield User.find(login=login)
            if len(users):
                self.write_error(500, "Already exist")
                return
            user = User(login=login)
            user.set_password(new_password=password)
            user.save()
            self.set_secure_cookie("user", login)
            self.get_user_from_cookies = lambda : login
            session = self.project_session
            session['current_user'] = user
            session.save()
            self.redirect("/")
        else:
            self.write_error(500, 'Incorrect password')


class AuthSockJSHandler(BaseSockJSHandler):

    def get_user_from_cookies(self):
        return decode_signed_value(secret=settings['cookie_secret'], name="user", value=self._user_login)

    def on_open(self, request):
        super(AuthSockJSHandler, self).on_open(request)
        # self.current_user = None

    def on_message(self, message):
        super(AuthSockJSHandler, self).on_message(message)
        data = self._message_json

        # Ignore all packets except of 'auth' if user is not yet authenticated
        auth_sid = data.get('sid') if data is not None else None
        if not self.project_session and not auth_sid:
            response = json.dumps({'user': 'system', 'status': 'error', 'text': 'Session id does not exist!'})
            self.send(response)
            self.close()
            raise ValueError(response)

        if auth_sid:
            self._user_login = auth_sid
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
