# Generated by Django 2.1.7 on 2019-03-02 12:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('WW', '0003_auto_20190302_1926'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='pox_y',
            new_name='pos_y',
        ),
    ]
