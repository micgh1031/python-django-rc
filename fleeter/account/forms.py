from django import forms

from apps.users.models import User as Account


class CustomUserCreationForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email', 'required': True, 'class': 'form-control'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username', 'required': True, 'class': 'form-control'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'required': True, 'class': 'form-control'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password (again)', 'required': True, 'class': 'form-control'}))

    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'password1', 'password2', 'email', 'username',)

    def clean(self):
        cleaned_data = super(CustomUserCreationForm, self).clean()
        # Email validation
        emails = Account.objects.filter(email__iexact=cleaned_data['email'])
        if emails:
            raise forms.ValidationError('Email is already registered')

        # Username validation
        usernames = Account.objects.filter(username__iexact=cleaned_data['username'])
        if usernames:
            raise forms.ValidationError('This username already exist')

        # Password validation
        if 'password1' in cleaned_data and 'password2' in cleaned_data:
            if cleaned_data['password1'] != cleaned_data['password2']:
                raise forms.ValidationError('The two password fields did not match')
        return cleaned_data

    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()

        return user


class CustomUserLoginForm(forms.Form):
    username = forms.CharField(widget=forms.EmailInput)
    password = forms.CharField(widget=forms.PasswordInput)
