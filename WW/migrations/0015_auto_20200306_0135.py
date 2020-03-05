# Generated by Django 2.1.7 on 2020-03-05 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WW', '0014_auto_20200306_0130'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commentimage',
            name='img',
            field=models.CharField(max_length=500, verbose_name='存储图片地址'),
        ),
        migrations.AlterField(
            model_name='commentimage',
            name='thumbnail',
            field=models.CharField(max_length=500, verbose_name='存储缩略图片地址'),
        ),
        migrations.AlterField(
            model_name='image',
            name='type',
            field=models.CharField(choices=[('avatar', 'Avatar'), ('universal', 'Universal')], default='universal', max_length=31, verbose_name='图片类型'),
        ),
        migrations.AlterField(
            model_name='messageimage',
            name='img',
            field=models.CharField(max_length=500, verbose_name='存储图片地址'),
        ),
        migrations.AlterField(
            model_name='messageimage',
            name='thumbnail',
            field=models.CharField(max_length=500, verbose_name='存储缩略图片地址'),
        ),
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.CharField(default='pic/rua.jpg', max_length=500, verbose_name='存储头像地址'),
        ),
    ]
