# Generated by Django 2.1.7 on 2019-07-13 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WW', '0009_auto_20190713_0104'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='phonenumber',
            field=models.CharField(default='', max_length=11, verbose_name='电话号码'),
            preserve_default=False,
        ),
    ]
