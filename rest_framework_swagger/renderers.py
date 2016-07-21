from coreapi.compat import force_bytes
from django.conf import settings
from django.shortcuts import render, resolve_url
from openapi_codec import OpenAPICodec
from rest_framework.renderers import BaseRenderer
import simplejson as json

from .settings import swagger_settings


class OpenAPIRenderer(BaseRenderer):
    media_type = 'application/openapi+json'
    charset = None
    format = 'openapi'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        data = self.get_openapi_specification(data)
        self.add_customizations(data)

        return self.dump(data)

    def dump(self, data):
        return force_bytes(json.dumps(data))

    def get_openapi_specification(self, data):
        """
        Converts data into OpenAPI specification.
        """
        codec = OpenAPICodec()
        return json.loads(codec.dump(data))

    def add_customizations(self, data):
        """
        Adds settings, overrides, etc. to the specification.
        """
        self.add_security_definitions(data)

    def add_security_definitions(self, data):
        if not swagger_settings.SECURITY_DEFINITIONS:
            return

        data['securityDefinitions'] = swagger_settings.SECURITY_DEFINITIONS


class SwaggerUIRenderer(BaseRenderer):
    media_type = 'text/html'
    format = 'swagger'
    template = 'rest_framework_swagger/index.html'
    charset = 'utf-8'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        self.set_context(renderer_context)
        return render(
            renderer_context['request'],
            self.template,
            renderer_context
        )

    def set_context(self, renderer_context):
        renderer_context['USE_SESSION_AUTH'] = \
            swagger_settings.USE_SESSION_AUTH
        self.set_session_auth_urls(renderer_context)

    def set_session_auth_urls(self, renderer_context):
        path = renderer_context['request'].path
        urls = {
            'LOGIN_URL': settings.LOGIN_URL,
            'LOGOUT_URL': settings.LOGOUT_URL
        }
        renderer_context.update({
            key: '%s?next=%s' % (resolve_url(val), path)
            for key, val in urls.items()
        })