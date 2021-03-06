# Generated by Django 2.1.7 on 2020-04-09 10:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('WW', '0031_auto_20200407_2138'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='parent_comment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comment_parent_comment_set', to='WW.Comment', verbose_name='该评论属的父评论'),
        ),
        migrations.AddField(
            model_name='comment',
            name='reply_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comment_reply_to_set', to='WW.User', verbose_name='该评论所回复的用户'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='who_like',
            field=models.ManyToManyField(blank=True, null=True, related_name='comment_who_like_set', to='WW.User', verbose_name='点赞该评论的用户'),
        ),
        migrations.AlterField(
            model_name='message',
            name='mention',
            field=models.ManyToManyField(blank=True, null=True, related_name='message_mention_user', to='WW.User', verbose_name='被该信息@的用户'),
        ),
        migrations.AlterField(
            model_name='message',
            name='tag',
            field=models.ManyToManyField(blank=True, null=True, related_name='message_tag_set', to='WW.Tag', verbose_name='该信息的tag'),
        ),
        migrations.AlterField(
            model_name='message',
            name='who_dislike',
            field=models.ManyToManyField(blank=True, null=True, related_name='message_who_dislike_set', to='WW.User', verbose_name='点踩该信息的用户'),
        ),
        migrations.AlterField(
            model_name='message',
            name='who_like',
            field=models.ManyToManyField(blank=True, null=True, related_name='message_who_like_set', to='WW.User', verbose_name='点赞该信息的用户'),
        ),
        migrations.AlterField(
            model_name='user',
            name='gender',
            field=models.CharField(choices=[('male', 'Male'), ('female', 'Female')], default='unknown', max_length=31, verbose_name='性别'),
        ),
    ]
