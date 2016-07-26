import time
from logging import error as e
from datetime import datetime, timedelta

from annoying.functions import get_object_or_None
from django.conf import settings
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate
from validate_email import validate_email
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from twilio.rest import TwilioRestClient
from gcm import GCM

from apps.users.models import User, ClientSession, UserProfile, UserTerms, UserPushToken, UserPhoneVerify
from wsi.utils.auth import generate_challange
from wsi.utils.views import UserAuthView, GeneralWSIViewMixin, WSITemplateViewMixin
from wsi.utils import generate_session_key
from apps.users.utils import generate_rand_string, generate_rand_number, send_mail_template, newsletter_subscribe, newsletter_unscribe
from apps.message.models import Messages, AbusiveReport

from wsi.utils import load_apn
from apns import Payload


class AuthView(GeneralWSIViewMixin):
    http_method_names = ['POST', 'OPTIONS']

    def dispatch(self, request, *args, **kwargs):
        super(AuthView, self).dispatch(request, *args, **kwargs)

        params = self.json_params

        name = params.get('email', '').lower()
        response = params.get('password', '')
        device_token = params.get('push_device_token', '')

        if not name:
            self.error('Invalid credentials')

        auth = authenticate(username=name, password=str(response))

        if auth:
            if auth.deleted:
                return self.error('User has been deleted')

            if auth.is_active is False:
                return self.error('User is not activated')

            if auth.is_blocked():
                return self.error('This user has been blocked.')

            if not auth.session_key:
                auth.session_key = generate_session_key()
                auth.session_created = datetime.now()
                auth.save()

            auth.last_login = datetime.now()
            auth.save()

            # add new device token
            if device_token:
                e("device_token: {}".format(device_token))
                device = params.get('device', None)
                is_android = False
                if device is None or device == 'Android':
                    is_android = True
                user_push_token = UserPushToken(user=auth, push_token=device_token, device=is_android)
                user_push_token.save()

            # else:
            #     check_credential_session_key_rotation(auth)
            return self.serve_result({
                '_id': auth.challenge,
                'display_name': auth.display_name,
                'active': auth.is_active,
                'nonce': auth.challenge,
                'token': auth.session_key,
                'push_device_token': device_token,
                'tos_version': auth.tos,
                'created': int(time.mktime(auth.created.timetuple()))
            })
        else:
            return self.error('Invalid credentials')


class RegisterGCM(UserAuthView):
    http_method_names = ['POST', 'OPTIONS']

    def dispatch(self, request, *args, **kwargs):
        super(RegisterGCM, self).dispatch(request, *args, **kwargs)

        user = self.auth
        if user is None:
            return self.error("NOT REGISTERED")

        if user.is_active is False:
            return self.error('NOT APPLICABLE')

        params = self.json_params

        return self.ok()


class ClientLoggedInView(UserAuthView):
    http_method_names = ['POST']

    def dispatch(self, request, *args, **kwargs):
        super(ClientLoggedInView, self).dispatch(request, *args, **kwargs)

        user = self.auth

        if user is None:
            return self.error("NOT REGISTERED")

        if not isinstance(user, get_user_model()):
            return self.error("NOT APPLICABLE")

        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')

        session = ClientSession()
        session.owner = user
        session.logged_in = datetime.fromtimestamp(float(time.time()))
        session.session_key = user.session_key
        session.expires_at = user.session_created + timedelta(0, settings.SESSION_KEY_ROTATION_TIME_INTERVAL)
        session.user_agent = user_agent
        session.save()

        return self.ok()


class ClientLoggedOutView(UserAuthView):
    http_method_names = ['GET', 'POST', 'OPTIONS']

    def dispatch(self, request, *args, **kwargs):
        super(ClientLoggedOutView, self).dispatch(request, *args, **kwargs)

        user = self.auth
        if user is None:
            return self.error("NOT REGISTERED")
        if not isinstance(user, get_user_model()):
            return self.error("NOT APPLICABLE")

        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')

        session = ClientSession.objects.filter(user_agent=user_agent, owner=user, logged_out=None).order_by(
            "-logged_out")

        if (len(session) == 0):
            return self.error("TOKEN NOT FOUND")

        session = session[0]

        session.logged_out = datetime.fromtimestamp(float(time.time()))
        session.save()
        return self.ok()


class GetUserInfo(UserAuthView):
    http_method_names = ['GET', 'POST', 'OPTIONS']

    def dispatch(self, request, *args, **kwargs):
        super(GetUserInfo, self).dispatch(request, *args, **kwargs)

        user = self.auth

        return self.serve_result({"result": user.to_json()})


class UsernameAvailable(GeneralWSIViewMixin):
    http_method_names = ['GET', 'POST', 'OPTIONS']

    def dispatch(self, request, *args, **kwargs):
        super(UsernameAvailable, self).dispatch(request, *args, **kwargs)

        params = self.json_params
        email = str(params.get('email', '')).lower()

        if not email:
            return self.error('Email address can not be blank')

        if not validate_email(email):
            return self.error("Invalid email address")

        user = get_object_or_None(get_user_model(), email=email)

        if user:
            return self.error('Email address is duplicated')

        return self.ok()


class DeleteUser(UserAuthView):
    http_method_names = ['DELETE', 'OPTIONS']

    def dispatch(self, request, *args, **kwargs):
        super(DeleteUser, self).dispatch(request, *args, **kwargs)

        auth = self.auth

        auth.deleted = True
        auth.save()
        return self.ok()


class RegisterUser(GeneralWSIViewMixin):
    http_method_names = ['POST', 'OPTIONS']

    def dispatch(self, request, *args, **kwargs):
        super(RegisterUser, self).dispatch(request, *args, **kwargs)

        if request.method == 'OPTIONS':
            return self.ok()
        elif request.method == 'POST':
            params = self.json_params

            if params.get('endpoint', '') == 'register':
                email = str(params.get('email', '')).lower()
                if not email:
                    return self.error('Email address can not be blank.')

                e("Email address is {0}".format(email))

                password = str(params.get('password', ''))

                if not password:
                    return self.error('Password can not be blank')

                push_token = str(params.get('push_device_token', ''))
                display_name = str(params.get('display_name', ''))

                if not validate_email(email):
                    return self.error("Invalid email address, Please use valid email address.")

                # check for duplicate name
                # if get_object_or_None(get_user_model(), email=email):
                #    return self.error('Email is duplicated')
                user = User.objects.filter(email=email).first()
                if user:
                    if user.deleted:
                        user.deleted = False
                    else:
                        return self.error('Email is duplicated')
                else:
                    user = User()

                user.email = email
                user.display_name = display_name
                user.username = email
                user.challenge = generate_challange()
                user.date_joined = datetime.utcnow()
                user.set_password(password)
                user.is_staff = False
                user.is_active = False
                user.tos = params.get('tos', '1.0')
                user.save()
                profile = UserProfile(user=user)
                profile.city = params.get('city', '')
                profile.country = params.get('country', '')
                profile.province = params.get('province', '')
                profile.formatted_user_address = params.get('formatted_user_address', '')
                profile.save()

                # add device token
                if push_token:
                    user_push_token = UserPushToken(user=user, push_token=push_token)
                    user_push_token.save()

                try:
                    send_mail_template(
                        'admin@windshieldink.com',
                        email,
                        "Activate Your Windshieldink Account",
                        "email_template/user/register",
                        {
                            'server_addr': settings.SERVER_HOST_NAME,
                            'challenge': user.challenge,
                            'display_name': user.display_name
                        })
                except:
                    e("Register User - Error to send email to {0}".format(email))
                    pass

                return self.serve_result(user.to_json())
            else:
                return self.error('Invalid endpoint')

        else:
            return self.error('Invalid Method')


class ResetPasswordView(GeneralWSIViewMixin):
    http_method_names = ['POST', 'OPTIONS']

    def dispatch(self, request, *args, **kwargs):
        super(ResetPasswordView, self).dispatch(request, *args, **kwargs)

        params = self.json_params

        try:
            email = params.get('email', '')

            if email:
                user = User.objects.filter(username=email).first()
                if user is not None and not user.is_blocked():
                    new_pwd = generate_rand_string(4)
                    user.set_password(new_pwd)
                    user.save()
                    send_mail_template(
                        settings.ADMIN_EMAIL,
                        user.email,
                        'Windshieldink Password Reset',
                        'email_template/user/resetpassword',
                        {
                            'new_password': new_pwd,
                            'display_name': user.display_name
                        })
                    return self.ok()
                else:
                    return self.error('Email does not exist!')
            else:
                return self.error('Email address is empty!')
        except:
            return self.error('Invalid email address')


class ChangeUserPassword(UserAuthView):
    http_method_names = ['POST', 'OPTIONS']

    def dispatch(self, request, *args, **kwargs):
        super(ChangeUserPassword, self).dispatch(request, *args, **kwargs)

        auth = self.auth
        params = self.json_params

        old_pwd = params.get('cur_pwd', '')
        new_pwd = params.get('new_pwd', '')

        if old_pwd and new_pwd:
            auth_user = authenticate(username=auth.username, password=str(old_pwd))
            if auth_user and auth_user.is_active:
                auth.set_password(new_pwd)
                auth.save()
                return self.ok()

        return self.error('The current password is incorrect')


# def session_expired(self):
class SessionExpired(GeneralWSIViewMixin):
    http_method_names = ['GET', 'POST']

    def dispatch(self, request, *args, **kwargs):
        super(SessionExpired, self).dispatch(request, *args, **kwargs)

        params = self.json_params

        challenge = params.get('nonce', '')
        userdata = User.objects.filter(challenge=challenge).first()

        if userdata:
            if not userdata.session_key:
                userdata.session_key = generate_session_key()
                userdata.session_created = datetime.now()
                userdata.save()
            # else:
            #    check_credential_session_key_rotation(userdata)

            return self.serve_result({'token': userdata.session_key})
        else:
            return self.error('Bad Request', 400)


class SendCommandToClient(UserAuthView):
    """
        Arguments required :
        camera session key as key
        time to live as expire_in_seconds
        collapse key as collapse_key, not used currently
        message payload in json format as payload
    """
    http_method_names = ['get', 'post']

    def dispatch(self, request, *args, **kwargs):
        super(SendCommandToClient, self).dispatch(request, *args, **kwargs)

        expiry_in_seconds = 300
        if request.REQUEST.has_key('expiry_in_seconds'):
            expiry_in_seconds = float(request.REQUEST.get('expiry_in_seconds'))

        collapse_key = None

        if not request.REQUEST.has_key('payload'):
            return self.error("NOT APPLICABLE")

        user = self.auth

        if not user:
            # you must own that camera
            return self.error("IDENTITY ERROR")

        e("send_command to client: {0}, payload : {1}".format(user.email, repr(request.REQUEST.get('payload'))))
        user.send_gcm_message(request.REQUEST.get('payload'), collapse_key, expiry_in_seconds)
        return self.ok()


class ActivateUser(WSITemplateViewMixin):
    template_name = 'activated.html'

    def dispatch(self, request, *args, **kwargs):
        super(ActivateUser, self).dispatch(request, *args, **kwargs)

        challenge = self.json_params.get('challenge', '')

        if not challenge:
            return render_to_response(self.template_name, {'message': 'Identity error'})
        else:
            user = User.objects.filter(challenge=challenge).first()

            if user:
                user.is_active = True
                user.save()
                send_mail_template(
                    'admin@windshieldink.com',
                    user.email,
                    'Welcome to Windshieldink!',
                    'email_template/user/welcome',
                    {
                        'display_name': user.display_name
                    })
                return render_to_response(self.template_name, {'message': 'Your Windshieldink account has been successfully activated!'})
            else:
                return render_to_response(self.template_name, {'message': 'Identity error'})


class AccountView(UserAuthView):
    http_method_names = ['GET', 'POST']

    def dispatch(self, request, *args, **kwargs):
        super(AccountView, self).dispatch(request, *args, **kwargs)

        auth = self.auth
        profile = UserProfile.objects.filter(user=auth).first()

        if profile is None:
            profile = UserProfile(user=auth)
            profile.save()

        if request.method == 'POST':
            params = self.json_params
            auth.phone_number = params.get('number', '')
            profile.send_sms = bool(params.get('send_sms', 0))
            profile.send_email = bool(params.get('send_mail', 0))
            profile.send_push = bool(params.get('send_push', 0))
            profile.signature = str(params.get('signature', ''))
            profile.send_newsletter = bool(params.get('send_newsletter', 0))

            auth.display_name = params.get('display_name', '')

            profile.city = params.get('city', '')
            profile.country = params.get('country', '')
            profile.province = params.get('province', '')
            profile.formatted_user_address = params.get('formatted_user_address', '')

            profile.user_place_id = params.get('user_place_id', '')

            auth.save()
            profile.save()

            try:
                if auth.phone_number and profile.send_sms and profile.valid_phone != auth.phone_number:
                    # Send sms with activation code
                    verify_code = generate_rand_number(6)
                    auth.phone_verified = False
                    auth.save()

                    twilio_client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                    twilio_client.messages.create(
                        to=auth.phone_number,
                        from_=settings.TWILIO_DEFAULT_CALLERID,
                        body="Your verification code is {code}".format(code=verify_code)
                    )

                    verification = UserPhoneVerify(user=auth)
                    verification.verify_code = verify_code
                    verification.save()

                    profile.valid_phone = ''
                    profile.save()
            except:
                return self.error('The phone number is invalid')
                pass

                # newsletter subscribe
                # if profile.send_newsletter:
                #   newsletter_subscribe(auth)
            # else:
            #    newsletter_unscribe(auth)

            data = {
                'nonce': auth.challenge,
                'active': auth.is_active,
                'created': auth.date_created,
                'roles': auth.roles,
                'display_name': auth.display_name,
                'send_newsletter': params.get('send_newsletter', False),
                'send_sms': params.get('send_sms', False),
                'send_mail': params.get('send_mail', False),
                'send_push': params.get('send_push', False),
                'number': params.get('number', ''),
                'signature': params.get('signature', ''),
                'email': auth.email,
                'city': params.get('city', ''),
                'province': params.get('province', ''),
                'country': params.get('country', ''),
                'formatted_user_address': params.get('formatted_user_address', ''),
                'user_place_id': params.get('user_place_id', ''),
                'tos': auth.tos,
                'phone_verified': auth.phone_verified
            }
            return self.serve_result({'result': data})
        elif request.method == 'GET':
            data = {
                'nonce': auth.challenge,
                'active': auth.is_active,
                'created': auth.date_created,
                'roles': auth.roles,
                'display_name': auth.display_name,
                'send_newsletter': profile.send_newsletter,
                'send_sms': profile.send_sms,
                'send_mail': profile.send_email,
                'send_push': profile.send_push,
                'number': auth.phone_number,
                'signature': profile.signature,
                'email': auth.email,
                'city': profile.city,
                'province': profile.province,
                'country': profile.country,
                'formatted_user_address': profile.formatted_user_address,
                'user_place_id': profile.user_place_id,
                'tos': auth.tos,
                'phone_verified': auth.phone_verified
            }
            return self.serve_result({'result': data})
        else:
            return self.error('NOT APPLICABLE')


class VerifyCodeView(UserAuthView):
    http_method_names = ['GET', 'POST', 'OPTIONS']

    def dispatch(self, request, *args, **kwargs):
        super(VerifyCodeView, self).dispatch(request, *args, **kwargs)

        auth = self.auth
        params = self.json_params

        verify_code = params.get('code', '')

        verification = UserPhoneVerify.objects.filter(user=auth).last()

        if verification is not None and not verification.has_expired() and auth.phone_number:
            if verification.verify_code == verify_code:
                profile = UserProfile.objects.get(user=auth)
                profile.valid_phone = auth.phone_number
                profile.save()

                auth.phone_verified = True
                auth.save()

                data = {
                    'nonce': auth.challenge,
                    'active': auth.is_active,
                    'created': auth.date_created,
                    'roles': auth.roles,
                    'display_name': auth.display_name,
                    'send_newsletter': profile.send_newsletter,
                    'send_sms': profile.send_sms,
                    'send_mail': profile.send_email,
                    'send_push': profile.send_push,
                    'number': auth.phone_number,
                    'signature': profile.signature,
                    'email': auth.email,
                    'city': profile.city,
                    'province': profile.province,
                    'country': profile.country,
                    'formatted_user_address': profile.formatted_user_address,
                    'user_place_id': profile.user_place_id,
                    'tos': auth.tos,
                    'phone_verified': auth.phone_verified
                }
                return self.serve_result({'result': data})
            else:
                return self.error('Invalid verification code')
        else:
            return self.error('Session has been expired')


class VerifyPhoneView(UserAuthView):
    http_method_names = ['GET', 'POST', 'OPTIONS']

    def dispatch(self, request, *args, **kwargs):
        super(VerifyPhoneView, self).dispatch(request, *args, **kwargs)

        auth = self.auth
        params = self.json_params

        auth.phone_number = params.get('phone', '')
        auth.phone_verified = False
        auth.save()

        if auth.phone_number:
            verify_code = generate_rand_number(6)

            try:
                twilio_client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                twilio_client.messages.create(
                    to=auth.phone_number,
                    from_=settings.TWILIO_DEFAULT_CALLERID,
                    body="Your verification code is {code}".format(code=verify_code)
                )

                verification = UserPhoneVerify(user=auth)
                verification.verify_code = verify_code
                verification.save()

                return self.ok()
            except:
                return self.error('Invalid phone number')
        else:
            return self.error('Invalid phone number')


class FacebookLoginView(GeneralWSIViewMixin):
    http_method_names = ['POST', 'OPTIONS']

    def dispatch(self, request, *args, **kwargs):
        super(FacebookLoginView, self).dispatch(request, *args, **kwargs)

        params = self.json_params

        fb_id = params.get('fb_id', '')

        if not fb_id:
            self.error('Invalid facebook id')

        fb_user = User.objects.get(fb_id=fb_id)

        if not fb_user:
            fb_user = User()
            fb_user.fb_id = fb_id
            fb_user.fb_token = params.get('fb_token', '')
            fb_user.email = params.get('email', '')
            fb_user.first_name = params.get('first_name', '')
            fb_user.last_name = params.get('last_name', '')
            fb_user.is_active = True
            fb_user.session_key = generate_session_key()
            fb_user.session_created = datetime.now()
            fb_user.challenge = generate_challange()

            fb_user.save()

        return self.serve_result({'result': fb_user.to_fb_json()})


class ReportAbusiveView(UserAuthView):
    http_method_names = ['POST', 'OPTIONS']

    def dispatch(self, request, *args, **kwargs):
        super(ReportAbusiveView, self).dispatch(request, *args, **kwargs)

        auth = self.auth
        params = self.json_params

        mid = params.get('mid', None)

        if request.method == 'POST':
            if not mid:
                return self.error('Invalid message id')

            message = Messages.objects.get(pk=int(mid))

            if message:
                abuser = message.sender
                abuser.abusive = True
                abuser.save()

                report_abusive = AbusiveReport(reporter=auth, message=message, status='Pending')
                report_abusive.save()

                # send email notification to abuse user
                send_mail_template(
                    settings.ADMIN_ABUSE_EMAIL,
                    abuser.email,
                    'Report Of Abusive Behavior',
                    'email_template/user/abusive',
                    {
                        'to_name': abuser.display_name,
                        'abusive_date': datetime.now().strftime('%d/%m/%Y')
                    })

                # report email notification to abuse admmin
                send_mail_template(
                    settings.ADMIN_NOREPLY_EMAIL,
                    settings.ADMIN_ABUSE_EMAIL,
                    'Report Of Abusive Behavior',
                    'email_template/user/report_abusive',
                    {
                        'abusive_email': abuser.email,
                        'from_email': auth.email,
                        'message': message.text,
                        'abusive_date': datetime.now().strftime('%d/%m/%Y')
                    })
                return self.ok()
            else:
                return self.error('Invalid message id')
        else:
            return self.error('Invalid http request')


class MailchimpView(GeneralWSIViewMixin):
    http_method_names = ['GET', 'POST', 'OPTIONS']

    def dispatch(self, request, *args, **kwargs):
        super(MailchimpView, self).dispatch(request, *args, **kwargs)
        params = self.json_params

        return self.serve_result({'result': params})


class TermsView(GeneralWSIViewMixin):
    http_method_names = ['GET', 'OPTIONS']

    def dispatch(self, request, *args, **kwargs):
        super(TermsView, self).dispatch(request, *args, **kwargs)
        tversion = UserTerms.objects.last()
        tos = render_to_string('terms/tos.html',
                               {
                                   'tos_version': tversion.version if tversion else '1.0'
                               })
        pp = render_to_string('terms/pp.html')
        abp = render_to_string('terms/abp.html')
        tversion = UserTerms.objects.last()

        return self.serve_result({'version': tversion.version if tversion else '1.0', 'tos': tos, 'pp': pp, 'abp': abp})


class TermsVersionView(GeneralWSIViewMixin):
    http_method_names = ['GET', 'OPTIONS']

    def dispatch(self, request, *args, **kwargs):
        super(TermsVersionView, self).dispatch(request, *args, **kwargs)

        if request.method == 'OPTIONS':
            return self.ok()
        elif request.method == 'GET':
            tversion = UserTerms.objects.last()
            return self.serve_result({
                'tos_version': tversion.version if tversion else '1.0'
            })
        else:
            return self.error('Not supported')


class TermsVersionUpdateView(UserAuthView):
    http_method_names = ['POST', 'OPTIONS']

    def dispatch(self, request, *args, **kwargs):
        super(TermsVersionUpdateView, self).dispatch(request, *args, **kwargs)

        auth = self.auth
        params = self.json_params

        if request.method == 'OPTIONS':
            return self.ok()
        elif request.method == 'POST':
            auth.tos = params.get('tos', '1.0')
            auth.save()
            return self.serve_result({
                'tos_version': auth.tos
            })
        else:
            return self.error('Not supported')


class TestGCMView(GeneralWSIViewMixin):
    http_method_names = ['GET', 'POST', 'DELETE']

    def dispatch(self, request, *args, **kwargs):
        super(TestGCMView, self).dispatch(request, *args, **kwargs)

        succeed = 0
        try:
            # if profile.send_push:
            test_gcm = GCM(settings.GCM_TOKEN, debug=False)
            user_push_tokens = UserPushToken.objects.all()

            data = {
                'message': request.GET.get('text', ''),
                'sender': request.GET.get('title', ''),
                'type': 'global',
            }
            e("Trying to send push notification for {} tokens".format(user_push_tokens.__len__()))

            try:
                apn = load_apn()
            except:
                apn = None
                pass

            for user_push_token in user_push_tokens:
                if user_push_token.device:
                    try:
                        response = test_gcm.plaintext_request(registration_id=user_push_token.push_token, data=data)
                        succeed += 1
                    except:
                        # e("Failed to push to {token}".format(user_push_token.push_token))
                        pass
                else:
                    try:
                        payload = Payload(alert='Test APN', custom=data)
                        apn.gateway_server.send_notification(user_push_token.push_token, payload)
                    except:
                        pass
        except:
            pass

        return self.serve_result({'succeed': succeed})

