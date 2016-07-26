# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Vehicles',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.CharField(max_length=10, null=True, blank=True)),
                ('make', models.CharField(max_length=255, null=True, blank=True)),
                ('model', models.CharField(max_length=255, null=True, blank=True)),
                ('make_id', models.CharField(max_length=100, null=True, blank=True)),
                ('model_id', models.CharField(max_length=100, null=True, blank=True)),
                ('plate', models.CharField(max_length=255, null=True, blank=True)),
                ('vin', models.CharField(max_length=255, null=True, blank=True)),
                ('color', models.CharField(max_length=255, null=True, blank=True)),
                ('state', models.CharField(max_length=255, null=True, blank=True)),
                ('country', models.CharField(max_length=255, null=True, blank=True)),
                ('place_id', models.CharField(max_length=255, null=True, blank=True)),
                ('formatted_address', models.CharField(max_length=255, null=True, blank=True)),
                ('secondary_email', models.CharField(max_length=100, null=True, blank=True)),
                ('is_fleeter', models.BooleanField(default=True)),
                ('user', models.ForeignKey(related_name='vehicle_owner', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
