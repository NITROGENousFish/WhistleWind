# Generated by Django 2.1.7 on 2020-03-26 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WW', '0019_auto_20200311_2055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.CharField(default='media/pic/rua.jpg', max_length=500, verbose_name='存储头像地址'),
        ),
    ]
