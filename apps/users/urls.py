from django.conf.urls import url
from apps.users.views import AuthView, RegisterUser, RegisterGCM, ActivateUser, ChangeUserPassword, SessionExpired, GetUserInfo, AccountView, \
    DeleteUser, VerifyPhoneView, FacebookLoginView, ResetPasswordView, ReportAbusiveView, MailchimpView, TermsView, TermsVersionView, \
    TermsVersionUpdateView, VerifyCodeView, TestGCMView

urlpatterns = [
    url(r'^login', AuthView.as_view(), name='user_login'),
    url(r'^register', RegisterUser.as_view(), name='user_register'),
    url(r'^activate', ActivateUser.as_view(), name='user_activate'),
    url(r'^reset', ResetPasswordView.as_view(), name='user_reset'),
    url(r'^recover', ChangeUserPassword.as_view(), name='user_recover'),
    url(r'^user', GetUserInfo.as_view(), name='user_info'),
    url(r'^session', SessionExpired.as_view(), name='user_check_session'),
    url(r'^account', AccountView.as_view(), name='user_account'),
    url(r'^delete_account', DeleteUser.as_view(), name='user_account_delete'),
    url(r'^register_gcm', RegisterGCM.as_view(), name='user_register_gcm'),
    url(r'^new_verification_code', VerifyPhoneView.as_view(), name='user_verify_phone'),
    url(r'^verify_code', VerifyCodeView.as_view(), name='user_verify_code'),
    url(r'^facebook_login', FacebookLoginView.as_view(), name='user_facebook_login'),
    url(r'^report_abuse', ReportAbusiveView.as_view(), name='user_facebook_login'),
    url(r'^callback_mailchimp', MailchimpView.as_view(), name='user_mailchimp_callback'),
    url(r'^tos_version', TermsVersionView.as_view(), name='user_terms_version'),
    url(r'^update_tos_version', TermsVersionUpdateView.as_view(), name='user_terms_version_update'),
    url(r'^tos', TermsView.as_view(), name='user_terms'),
    url(r'^test_gcm_global', TestGCMView.as_view(), name='gcm_test'),
]
