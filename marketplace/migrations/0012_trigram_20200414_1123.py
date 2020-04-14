from django.db import migrations
from django.contrib.postgres.operations import TrigramExtension


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0011_merge_20200410_1308'),
        ('marketplace', '0012_auto_20200414_1644')
    ]

    operations = [
        TrigramExtension(),
    ]
