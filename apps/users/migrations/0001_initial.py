# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.auth.models
import django.utils.timezone
from django.conf import settings
import django.core.validators
import annoying.fields


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, max_length=30, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, verbose_name='username')),
                ('first_name', models.CharField(max_length=30, verbose_name='first name', blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='last name', blank=True)),
                ('email', models.EmailField(max_length=254, verbose_name='email address', blank=True)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('phone_number', models.CharField(max_length=20, blank=True)),
                ('challenge', models.CharField(max_length=100, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('abusive', models.BooleanField(default=False)),
                ('display_name', models.CharField(max_length=64, null=True, blank=True)),
                ('roles', models.CharField(max_length=127, null=True, blank=True)),
                ('plan', models.CharField(default=b'first', max_length=30, null=True, blank=True)),
                ('tos', models.CharField(default=b'1.0', max_length=32, blank=True)),
                ('phone_verified', models.BooleanField(default=False)),
                ('is_admin', models.BooleanField(default=False)),
                ('fb_id', models.CharField(max_length=256, null=True, blank=True)),
                ('fb_token', models.CharField(max_length=256, null=True, blank=True)),
                ('session_key', models.CharField(max_length=100, blank=True)),
                ('session_created', models.DateTimeField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='ClientSession',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_agent', models.CharField(max_length=255, null=True, blank=True)),
                ('session_key', models.CharField(max_length=100, blank=True)),
                ('expires_at', models.DateTimeField(null=True, blank=True)),
                ('logged_in', models.DateTimeField(null=True, blank=True)),
                ('logged_out', models.DateTimeField(null=True, blank=True)),
                ('owner', models.ForeignKey(related_name='client_session', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserAudit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('audit_type', models.CharField(default=b'Custom', max_length=10, null=True, blank=True)),
                ('detail', models.CharField(max_length=1024, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='UserBlocked',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserCommand',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('utc_expiry', models.DateTimeField()),
                ('payload', annoying.fields.JSONField(null=True, blank=True)),
                ('user', models.ForeignKey(related_name='gcm_command', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserPhoneVerify',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('verify_code', models.CharField(max_length=10, null=True, blank=True)),
                ('last_time', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(related_name='phone_verify_user', to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('send_sms', models.BooleanField(default=False)),
                ('send_email', models.BooleanField(default=False)),
                ('send_newsletter', models.BooleanField(default=False)),
                ('valid_phone', models.CharField(default=b'', max_length=100, null=True, blank=True)),
                ('city', models.CharField(max_length=255, null=True, blank=True)),
                ('country', models.CharField(max_length=255, null=True, blank=True)),
                ('province', models.CharField(max_length=255, null=True, blank=True)),
                ('formatted_user_address', models.CharField(max_length=255, null=True, blank=True)),
                ('send_push', models.BooleanField(default=False)),
                ('signature', models.CharField(default=b'', max_length=255, null=True, blank=True)),
                ('user_place_id', models.CharField(max_length=255, null=True, blank=True)),
                ('user', models.ForeignKey(related_name='owner', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserPushToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('push_token', models.CharField(max_length=1024, null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(related_name='owner_device_token', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserTerms',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('version', models.CharField(default=b'1.0', max_length=10, null=True, blank=True)),
                ('modified', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
