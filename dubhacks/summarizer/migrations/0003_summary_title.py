# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('summarizer', '0002_summary_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='summary',
            name='title',
            field=models.TextField(blank=True),
        ),
    ]
