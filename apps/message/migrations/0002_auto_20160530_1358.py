# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('message', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='messageusersaction',
            name='message_modifier',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='messages',
            name='message_sender',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='messagereplies',
            name='message',
            field=models.ForeignKey(related_name='message_id', to='message.Messages'),
        ),
        migrations.AddField(
            model_name='messagereplies',
            name='receipt',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='messagehistory',
            name='user',
            field=models.ForeignKey(related_name='message_history_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='abusivereport',
            name='message',
            field=models.ForeignKey(blank=True, to='message.Messages', null=True),
        ),
        migrations.AddField(
            model_name='abusivereport',
            name='reporter',
            field=models.ForeignKey(related_name='abusive_reporter', to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
