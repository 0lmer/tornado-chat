# -*- coding: utf-8 -*-
import json

from core.session import Session
import tornado.web
import sockjs.tornado
import os
from jinja2 import Environment, FileSystemLoader, TemplateNotFound


class ProjectSessionHandler(object):
    _sid = None
    application = None

    @property
    def project_session(self):
        if self._sid:
            return Session(self.application.session_store, self._sid)
        else:
            return None


class JinjaTemplateRendering:
    """
    A simple class to hold methods for rendering templates.
    """
    def render_template(self, template_name, **kwargs):
        template_dirs = []
        template_dirs += (os.path.join(app, 'templates') for app in self.settings.get('apps', []))
        env = Environment(loader=FileSystemLoader(template_dirs))

        try:
            template = env.get_template(template_name)
        except TemplateNotFound:
            raise TemplateNotFound(template_name)
        content = template.render(kwargs)
        return content


class BaseHandler(JinjaTemplateRendering, ProjectSessionHandler, tornado.web.RequestHandler):

    # def render(self, template_name, **kwargs):
    #     """
    #         For Tornado templates
    #     """
    #     path_chain = template_name.split('/')
    #     if len(path_chain) > 1:
    #         app_name = path_chain[0]
    #         path_chain.pop(0)
    #     else:
    #         app_name = 'core'
    #     relative_template_name = os.path.join(app_name, 'templates', app_name)
    #     relative_template_name = os.path.join(relative_template_name, os.path.join(*path_chain))
    #     super(BaseHandler, self).render(relative_template_name, **kwargs)

    def render(self, template_name, **kwargs):
        """
        This is for making some extra context variables available to
        the template
        """
        kwargs.update({
            'settings': self.settings,
            'STATIC_URL': self.settings.get('static_path', '/static/'),
            'request': self.request,
            'xsrf_token': self.xsrf_token,
            'xsrf_form_html': self.xsrf_form_html,
        })
        content = self.render_template(template_name, **kwargs)
        self.write(content)


class BaseSockJSHandler(sockjs.tornado.SockJSConnection, ProjectSessionHandler):
    application = None

    def __init__(self, session):
        super(BaseSockJSHandler, self).__init__(session)
        self._message_json = None

    def on_open(self, request):
        super(BaseSockJSHandler, self).on_open(request)

    def on_message(self, message):
        try:
            self._message_json = json.loads(message)
        except ValueError, ex:
            pass
        print(message)