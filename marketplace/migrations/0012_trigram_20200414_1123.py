from django.db import migrations
from django.contrib.postgres.operations import TrigramExtension


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0011_merge_20200410_1308'),
    ]

    operations = [
        TrigramExtension(),
    ]
