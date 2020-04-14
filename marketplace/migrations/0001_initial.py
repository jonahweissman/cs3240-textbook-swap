# Generated by Django 3.0.3 on 2020-03-02 18:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('imagefile', models.ImageField(null=True, upload_to='images/')),
                ('phonenumber', models.CharField(max_length=12, null=True)),
                ('major', models.CharField(max_length=50, null=True)),
                ('year', models.CharField(max_length=4, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_name', models.CharField(max_length=100)),
                ('item_price', models.IntegerField()),
                ('item_condition', models.CharField(choices=[('Like New', 'Like New'), ('Good', 'Good'), ('Fair', 'Fair'), ('Poor', 'Poor')], default='Brand New', max_length=20)),
                ('item_posted_date', models.DateField()),
                ('item_description', models.TextField(max_length=1000)),
                ('item_seller_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='marketplace.Profile')),
            ],
        ),
    ]
