# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('message', '0002_auto_20160530_1358'),
    ]

    operations = [
        migrations.RenameField(
            model_name='messages',
            old_name='message_sender',
            new_name='sender',
        ),
    ]
