# Generated by Django 3.1.3 on 2021-02-08 19:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project_view', '0041_auto_20210208_1946'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='participation',
            unique_together={('project', 'participant')},
        ),
    ]
