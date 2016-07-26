from django.contrib.auth import get_user_model
from django.forms import ModelForm


class MessageForm(ModelForm):

    class Meta:
        model = get_user_model()
        fields = ('email', 'first_name', 'last_name', 'push_token')
