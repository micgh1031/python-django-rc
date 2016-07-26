# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AbusiveReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default=b'Pending', max_length=10, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='MessageHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('plate', models.CharField(max_length=255, null=True, blank=True)),
                ('place_id', models.CharField(max_length=255, null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='MessageReplies',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Messages',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('country', models.CharField(max_length=255, null=True, blank=True)),
                ('state', models.CharField(max_length=255, null=True, blank=True)),
                ('location', models.BooleanField(default=False)),
                ('identify', models.BooleanField(default=False)),
                ('latitude', models.CharField(max_length=255, null=True, blank=True)),
                ('longitude', models.CharField(max_length=255, null=True, blank=True)),
                ('plate', models.CharField(max_length=255, null=True, blank=True)),
                ('place_id', models.CharField(max_length=255, null=True, blank=True)),
                ('vid', models.IntegerField(default=-1, blank=True)),
                ('text', models.TextField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='MessageUsersAction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('replies', models.IntegerField(default=-1, blank=True)),
                ('modified', models.DateTimeField(auto_now_add=True)),
                ('message', models.ForeignKey(to='message.Messages', null=True)),
            ],
        ),
    ]
