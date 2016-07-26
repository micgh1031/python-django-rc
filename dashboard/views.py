from django.contrib.auth import authenticate, login, logout
from django.views.generic import TemplateView, View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.db.models import Count

import json, csv

from gcm import *

from django.conf import settings

from apps.users.models import User, UserBlocked, UserPushToken
from apps.message.models import Messages, MessageReplies, AbusiveReport, MessageUsersAction
from wsi.utils.auth import report_block, IsMessageDeleted, reactive_user
from apps.vehicles.models import Vehicles
from dashboard.models import NoticeHistory


class AdminIndexView(TemplateView):
    template_name = 'dashboard/layout/dashboard.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        super(AdminIndexView, self).dispatch(request, *args, **kwargs)

        users = User.objects.filter(is_admin=False, is_staff=False, deleted=False)
        messages = Messages.objects.all()

        last_messages = Messages.objects.all().order_by('-id')[:3]
        ret_messages = list()
        for message in last_messages:
            replies = MessageReplies.objects.filter(message=message)
            ret_messages.append({
                'id': message.pk,
                'text': message.text,
                'sender': message.sender,
                'replies': replies.__len__()
            })

        unique_plates = Vehicles.objects.values('plate').annotate(Count('plate'))

        return self.render_to_response(context={
            'page': 'index',
            'user_count': users.__len__(),
            'plates': unique_plates.__len__(),
            'messages': ret_messages
        })


class AdminLogoutView(View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        super(AdminLogoutView, self).dispatch(request, *args, **kwargs)

        logout(request)

        return HttpResponseRedirect('/login/')


class AdminLoginView(TemplateView):
    template_name = 'dashboard/auth/login.html'
    success_url = '/users/'

    def dispatch(self, request, *args, **kwargs):
        super(AdminLoginView, self).dispatch(request, *args, **kwargs)

        if request.method == 'GET':
            if request.user.is_authenticated() and request.user.is_admin is True:
                return HttpResponseRedirect('/')
            else:
                return self.render_to_response(context={'page': 'login'})
        elif request.method == 'POST':
            form_data = json.loads(request.body)
            account = authenticate(
                username=form_data.get('username', ''),
                password=form_data.get('password', '')
            )

            if account is not None and account.is_admin and account.is_staff:
                if account.is_active:
                    login(request, account)

                    return JsonResponse({'success': True})
                else:
                    return JsonResponse({'success': False})
            else:
                return JsonResponse({'success': False})
        else:
            JsonResponse({'success': False})


class AdminMessagesView(TemplateView):
    template_name = 'dashboard/layout/messages.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        super(AdminMessagesView, self).dispatch(request, *args, **kwargs)

        if request.method == 'POST':
            form_data = json.loads(request.body, 'utf-8')
            if form_data['method'] == 'DELETE' and form_data['pk'] is not None:
                try:
                    message = Messages.objects.get(pk=int(form_data['pk']))
                    replies = MessageReplies.objects.filter(message=message)
                    replies.delete()
                    message.delete()
                except:
                    pass

                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False})
        else:
            messages = Messages.objects.all()
            dict_messages = list()
            for message in messages:
                dict_messages.append({
                    'pk': message.pk,
                    'sender': message.sender,
                    'plate': message.plate,
                    'origin': '{state} {country}'.format(state=message.state, country=message.country),
                    'is_deleted': IsMessageDeleted(message),
                    'text': message.text
                })

            return self.render_to_response(context={'page': 'messages', 'messages': dict_messages})


class AdminUsersView(TemplateView):
    template_name = 'dashboard/layout/users.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        super(AdminUsersView, self).dispatch(request, *args, **kwargs)

        if request.method == 'POST':
            form_data = json.loads(request.body, 'utf-8')
            if form_data.get('method', '') == 'delete':
                if form_data.get('type', '') == 'json':
                    try:
                        user = User.objects.get(challenge=form_data['user']['_id'])

                        blocked = UserBlocked.objects.filter(user=user)
                        blocked.delete()

                        user.deleted = True
                        user.save()
                    except:
                        pass
                else:
                    try:
                        user_id = int(form_data['user_id'])
                        user = User.objects.get(pk=user_id)

                        blocked = UserBlocked.objects.filter(user=user)
                        blocked.delete()

                        user.deleted = True
                        user.save()
                    except:
                        pass

                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False})
        else:
            users = User.objects.filter(is_admin=False, is_staff=False, deleted=False)

            if request.GET.get('method', '') == 'export':
                users = User.objects.filter(is_admin=False, is_staff=False).all()
                str_keys = request.GET.get('keys', '')

                export_keys = json.loads(str_keys, 'utf-8')

                export_keys.append('Status')

                response = HttpResponse(content_type='application/x-download')
                response['Content-Disposition'] = 'attachment; filename="users.csv"'

                csv_writer = csv.writer(response)
                csv_writer.writerow(export_keys)

                for user in users:
                    dict_row = list()
                    profile = user.get_profile()
                    if 'Email' in export_keys:
                        dict_row.append(user.email)

                    if 'Nick Name' in export_keys:
                        dict_row.append(user.display_name)

                    if 'City' in export_keys:
                        dict_row.append(profile.city)

                    if 'Phone' in export_keys:
                        dict_row.append(profile.valid_phone)

                    if 'Receiving Email' in export_keys:
                        dict_row.append('ON' if profile.send_email else 'OFF')

                    if 'Receiving Push' in export_keys:
                        dict_row.append('ON' if profile.send_push else 'OFF')

                    if 'Receiving SMS' in export_keys:
                        dict_row.append('ON' if profile.send_sms else 'OFF')

                    if 'Signature' in export_keys:
                        dict_row.append(profile.signature)

                    if user.deleted:
                        dict_row.append('DELETED')
                    elif user.is_blocked():
                        dict_row.append('BLOCKED')
                    elif user.abusive:
                        dict_row.append('ABUSIVE REPORTED')
                    elif user.is_active:
                        dict_row.append('ACTIVE')
                    else:
                        dict_row.append('PENDING')

                    csv_writer.writerow(dict_row)

                return response
            else:
                dict_users = list()

                for user in users:
                    dict_users.append(user.to_json())

                if request.GET.get('type', '') == 'json':
                    return JsonResponse({'users': dict_users})
                else:
                    return self.render_to_response(context={'page': 'users', 'dict_users': dict_users, 'users': users})


class AdminBlacklistView(TemplateView):
    template_name = 'dashboard/layout/blacklist.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        super(AdminBlacklistView, self).dispatch(request, *args, **kwargs)

        if request.method == 'POST':
            form_data = json.loads(request.body, 'utf-8')
            if form_data.get('pk', None) is not None:
                if form_data['method'] == 'block':
                    user = User.objects.filter(pk=form_data['pk']).first()
                    if user:
                        report_block(user)
                        return JsonResponse({'success': True})
                    else:
                        return JsonResponse({'success': False, 'message': 'Invalid User ID'})
                elif form_data['method'] == 'reactive':
                    try:
                        blocked = UserBlocked.objects.get(pk=int(form_data['pk']))
                        reactive_user(blocked.user)
                        blocked.delete()
                        return JsonResponse({'success': True})
                    except:
                        return JsonResponse({'success': False})
                elif form_data['method'] == 'delete':
                    try:
                        blocked = UserBlocked.objects.get(pk=int(form_data['pk']))
                        user = blocked.user

                        user.deleted = True
                        user.save()

                        blocked.delete()

                        return JsonResponse({'success': True})
                    except:
                        return JsonResponse({'success': False})
                else:
                    return JsonResponse({'success': False})
            elif form_data['_id'] is not None:
                user = User.objects.filter(challenge=form_data['_id']).first()
                if user:
                    report_block(user)
                    return JsonResponse({'success': True})
                else:
                    return JsonResponse({'success': False, 'message': 'Invalid User ID'})
            else:
                return JsonResponse({'success': False})
        else:
            blocked = UserBlocked.objects.all()

            return self.render_to_response(context={'page': 'blacklist', 'blocked': blocked})


class AdminAbusiveView(TemplateView):
    template_name = 'dashboard/layout/abusive_reports.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        super(AdminAbusiveView, self).dispatch(request, *args, **kwargs)

        if request.method == 'POST':
            form_data = json.loads(request.body, 'utf-8')
            if form_data['method'] == 'DELETE' and form_data['pk'] is not None:
                pk = int(form_data['pk'])
                try:
                    row = AbusiveReport.objects.filter(pk=pk)
                    row.delete()
                except:
                    pass
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False})
        else:
            rows = AbusiveReport.objects.all()

            return self.render_to_response(context={'page': 'abusive', 'reports': rows})


class AdminLicensePlatesView(TemplateView):
    template_name = 'dashboard/layout/license_plates.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        super(AdminLicensePlatesView, self).dispatch(request, *args, **kwargs)

        if request.method == 'POST':
            form_data = json.loads(request.body, 'utf-8')
            if form_data['method'] == 'DELETE' and form_data['pk'] is not None:
                try:
                    vehicle = Vehicles.objects.get(pk=int(form_data['pk']))
                    vehicle.delete()
                except:
                    pass
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': True})
        else:
            vehicles = Vehicles.objects.all()

            if request.GET.get('method', '') == 'EXPORT':
                str_keys = request.GET.get('keys', '')

                dict_keys = json.loads(str_keys, 'utf-8')

                response = HttpResponse(content_type='application/x-download')
                response['Content-Disposition'] = 'attachment; filename="vehicles.csv"'

                csv_writer = csv.writer(response)
                csv_writer.writerow(dict_keys)

                for vehicle in vehicles:
                    dict_row = list()
                    if 'Email' in dict_keys:
                        dict_row.append(vehicle.user.email)

                    if 'License' in dict_keys:
                        dict_row.append(vehicle.plate)

                    if 'Origin' in dict_keys:
                        dict_row.append(vehicle.formatted_address)

                    if 'Make' in dict_keys:
                        dict_row.append(vehicle.make)

                    if 'Model' in dict_keys:
                        dict_row.append(vehicle.model)

                    if 'Year' in dict_keys:
                        dict_row.append(vehicle.year)

                    csv_writer.writerow(dict_row)

                return response
            else:
                return self.render_to_response(context={'page': 'license_plates', 'data': vehicles})


class AdminNoticeView(TemplateView):
    template_name = 'dashboard/layout/notice.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        super(AdminNoticeView, self).dispatch(request, *args, **kwargs)

        if request.method == 'POST':
            form_data = request.POST

            if form_data['method'] == 'SEND':

                try:
                    # if profile.send_push:
                    gcm = GCM(settings.GCM_TOKEN, debug=False)
                    user_push_tokens = UserPushToken.objects.all()
                    data = {
                        'message': form_data['text'],
                        'sender': form_data['title'],
                        'type': 'global',
                    }

                    notice_history = NoticeHistory(
                        title=form_data['title'],
                        content=form_data['text']
                    )

                    notice_history.save()

                    notices = NoticeHistory.objects.all()

                    for user_push_token in user_push_tokens:
                        try:
                            response = gcm.plaintext_request(registration_id=user_push_token.push_token, data=data)
                        except:
                            # e("Failed to push to {token}".format(user_push_token.push_token))
                            pass
                except:
                    pass

                return self.render_to_response(
                    context={'page': 'notice', 'message': 'Sent notification successfully!', 'notices': notices})
            elif form_data['method'] == 'DELETE':
                try:
                    notice = NoticeHistory.objects.get(pk=int(form_data['pk']))
                    notice.delete()

                    notices = NoticeHistory.objects.all()
                except:
                    pass
                return self.render_to_response(
                    context={'page': 'notice', 'message': 'Deleted Successfully!', 'notices': notices})
        else:
            notices = NoticeHistory.objects.all()
            return self.render_to_response(context={'page': 'notice', 'message': None, 'notices': notices})
