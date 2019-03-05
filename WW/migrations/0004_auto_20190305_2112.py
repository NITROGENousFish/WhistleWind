# Generated by Django 2.1.7 on 2019-03-05 13:12

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('WW', '0003_auto_20190304_2228'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='add_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='保存日期'),
        ),
        migrations.AddField(
            model_name='comment',
            name='mod_date',
            field=models.DateTimeField(auto_now=True, verbose_name='最后修改日期'),
        ),
    ]
