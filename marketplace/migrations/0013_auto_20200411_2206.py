# Generated by Django 3.0.3 on 2020-04-12 02:06

from django.db import migrations, models
import phone_field.models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0012_auto_20200411_2152'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='imagefile',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='major',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='phonenumber',
            field=phone_field.models.PhoneField(blank=True, max_length=31, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='year',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
