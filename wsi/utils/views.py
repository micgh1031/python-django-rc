import json
from logging import debug as d, error as e
from datetime import datetime
from django.contrib.auth import get_user_model
from django.views.generic import View, TemplateView
from django.http import JsonResponse
from wsi.utils.auth import check_credential_session_key_rotation
from wsi.utils.exceptions import ErrorConvention
from django.utils.datastructures import MergeDict

from apps.users.models import UserBlocked

User = get_user_model()


class GeneralResponseMixin(object):
    @staticmethod
    def ok():
        return JsonResponse({"success": True, "message": "OK"}, status=200)

    @staticmethod
    def error(message, error_code=401):
        return JsonResponse({"success": False, "message": message}, status=200)

    @staticmethod
    def serve_result(obj):
        obj.update({"success": True, "message": "OK"})
        return JsonResponse(obj, status=200)


class AuthViewMixin(object):
    """
    Mixin intended to be used in combination with django.views.generic.View.
    Implements user or camera authorization on every request
    """
    auth = None
    auth_model = None
    token = None

    def dispatch(self, request, *args, **kwargs):
        # param method
        # self.auth = self._authorize(request)
        # http authorization method
        self.auth = self._header_authorize(request)

        return super(AuthViewMixin, self).dispatch(request, *args, **kwargs)

    def _header_authorize(self, request):
        auth_obj = None

        self.token = request.META.get('HTTP_TOKEN', None)

        if self.token is not None:
            e("-- auth -- key={0}".format(self.token))
            if self.token is '' and auth_obj is None:
                raise ErrorConvention('CREDENTIALS MISSING')

            if not auth_obj:
                auth_obj = self.get_auth_object(self.token)

            if not auth_obj:
                """
                print "\n\n " , "could not authorize key : " , _key + " DB returned : " , auth , \
                        " , all credentials : " , all_credentials , "\n\n"
                """
                raise ErrorConvention('IDENTITY ERROR')

            if auth_obj.session_created is None:
                auth_obj.session_created = datetime.now()
                auth_obj.save()
                # return auth_obj
            '''
            if check_credential_session_key_rotation(auth_obj):
                raise ErrorConvention('IDENTITY ERROR')
            else:
            '''
            if auth_obj:
                # check if user has been blocked
                blocked_user = UserBlocked.objects.filter(user=auth_obj)
                if blocked_user.__len__() > 0:
                   raise ErrorConvention('Blocked User')
                else:
                    return auth_obj
                # return auth_obj
            else:
                raise ErrorConvention('IDENTITY ERROR')
        else:
            raise ErrorConvention('Token is empty')

    def _authorize(self, request):
        auth_obj = None
        if "token" in request.REQUEST:
            _key = request.REQUEST.get("token")
            e(" --- auth --- key={0}".format(_key))
        else:
            raise ErrorConvention('CREDENTIALS MISSING')

        if _key == "" and auth_obj is None:
            raise ErrorConvention('IDENTITY ERROR')

        # auth_obj = self.get_auth_model().objects.filter(session_key=_key).first()
        if not auth_obj:
            auth_obj = self.get_auth_object(_key)

        self.token = _key

        if auth_obj.session_created is None:
            auth_obj.session_created = datetime.now()
            auth_obj.save()
            return auth_obj

        #if check_credential_session_key_rotation(auth_obj):
        #    raise ErrorConvention('IDENTITY ERROR')
        #else:
        if not auth_obj:
            raise ErrorConvention('IDENTITY ERROR')
        else:
            return auth_obj

    def get_auth_model(self):
        return self.auth_model

    def get_auth_object(self, session_key):
        return self.get_auth_model().objects.filter(session_key=session_key).first()


class WSITemplateViewMixin(TemplateView):
    json_params = dict()

    def dispatch(self, request, *args, **kwargs):
        raw_body = request.body.decode('utf-8')
        self.json_params = MergeDict(request.GET, request.POST)
        if raw_body:
            self.json_params = MergeDict(self.json_params, json.loads(raw_body))

        return super(WSITemplateViewMixin, self).dispatch(request, *args, **kwargs)


class GeneralWSIViewMixin(View, GeneralResponseMixin):
    json_params = dict()

    def dispatch(self, request, *args, **kwargs):
        raw_body = request.body.decode('utf-8')
        self.json_params = MergeDict(request.GET, request.POST)
        if raw_body:
            self.json_params = MergeDict(self.json_params, json.loads(raw_body))

        return super(GeneralWSIViewMixin, self).dispatch(request, *args, **kwargs)


class UserAuthView(AuthViewMixin, GeneralWSIViewMixin):
    """
    Class that implements user authorization on every request
    """
    def get_auth_model(self):
        return get_user_model()

    def get_auth_token(self):
        return self.token
