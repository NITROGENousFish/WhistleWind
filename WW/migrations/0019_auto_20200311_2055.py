# Generated by Django 2.1.7 on 2020-03-11 12:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('WW', '0018_auto_20200311_2052'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='author',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='comment_set', to='WW.User', verbose_name='该评论所属用户'),
        ),
        migrations.AlterField(
            model_name='message',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='message_set', to='WW.User', verbose_name='该信息作者'),
        ),
    ]
