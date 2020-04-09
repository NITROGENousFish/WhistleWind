# Generated by Django 2.1.7 on 2020-04-07 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WW', '0029_auto_20200407_2053'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='mention',
            field=models.ManyToManyField(blank=True, related_name='message_mention_user', to='WW.User', verbose_name='被该信息@的用户'),
        ),
        migrations.AlterField(
            model_name='image',
            name='type',
            field=models.CharField(choices=[('avatar', 'Avatar'), ('unknown', 'Unknown'), ('universal', 'Universal')], default='universal', max_length=31, verbose_name='图片类型'),
        ),
        migrations.AlterField(
            model_name='user',
            name='gender',
            field=models.CharField(choices=[('female', 'Female'), ('male', 'Male')], default='unknown', max_length=31, verbose_name='性别'),
        ),
    ]