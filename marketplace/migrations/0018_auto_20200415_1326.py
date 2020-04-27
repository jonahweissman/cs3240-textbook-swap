# Generated by Django 3.0.3 on 2020-04-15 17:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0017_merge_20200414_1741'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='item_condition',
            field=models.CharField(choices=[('Like New', 'Like New'), ('Good', 'Good'), ('Fair', 'Fair'), ('Poor', 'Poor')], default='Like New', max_length=20),
        ),
        migrations.AlterField(
            model_name='item',
            name='item_status',
            field=models.CharField(choices=[('Available', 'Available'), ('Sold', 'Sold'), ('Unavailable', 'Unavailable')], default='Available', max_length=20),
        ),
    ]