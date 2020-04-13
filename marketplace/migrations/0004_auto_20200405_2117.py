# Generated by Django 3.0.3 on 2020-04-06 02:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0003_auto_20200404_0042'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='conversation',
            name='root_message',
        ),
        migrations.AddField(
            model_name='message',
            name='conversation',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='marketplace.Conversation'),
            preserve_default=False,
        ),
    ]
