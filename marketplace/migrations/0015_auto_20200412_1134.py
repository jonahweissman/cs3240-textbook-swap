# Generated by Django 3.0.3 on 2020-04-12 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0014_auto_20200411_2214'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='phonenumber',
            field=models.CharField(blank=True, max_length=12, null=True),
        ),
    ]
