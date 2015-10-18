# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('summarizer', '0003_summary_title'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='summary',
            name='date',
        ),
        migrations.AddField(
            model_name='topic',
            name='updated',
            field=models.DateField(blank=True, null=True),
        ),
    ]
