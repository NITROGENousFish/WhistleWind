# Generated by Django 2.1.7 on 2020-03-31 08:30

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('WW', '0023_auto_20200331_1627'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='registration_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='发布日期'),
        ),
        migrations.AlterField(
            model_name='user',
            name='gender',
            field=models.CharField(choices=[('male', 'Male'), ('female', 'Female')], default='unknown', max_length=31, verbose_name='性别'),
        ),
    ]
