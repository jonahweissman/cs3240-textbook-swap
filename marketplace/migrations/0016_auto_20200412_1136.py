# Generated by Django 3.0.3 on 2020-04-12 15:36

from django.db import migrations
import phone_field.models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0015_auto_20200412_1134'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='phonenumber',
            field=phone_field.models.PhoneField(blank=True, max_length=31, null=True),
        ),
    ]
