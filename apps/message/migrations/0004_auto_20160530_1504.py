# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('message', '0003_auto_20160530_1443'),
    ]

    operations = [
        migrations.RenameField(
            model_name='messageusersaction',
            old_name='message_modifier',
            new_name='modifier',
        ),
    ]
