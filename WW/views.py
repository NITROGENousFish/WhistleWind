"""
    本模块遵循Restful原则，使用不同的HTTP动词对应不同类型的操作
    POST: 增加
    GET: 获取
    PUT: 修改
    DELETE: 删除
    接口的具体功能见
    http://rap2.taobao.org/organization/repository/editor?id=224734&mod=313234
"""
from django.shortcuts import render
import exrex
import json
import os
import demjson
import traceback
from datetime import datetime, timedelta, timezone
from . import models, sendEmail
from django.views import View
from django.http import HttpResponse
from django.http import JsonResponse, FileResponse, QueryDict
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from django.core.cache import cache
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname('__file__')))
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')
PIC_ROOT = os.path.join(MEDIA_ROOT, 'pic')

# jhc work----------------------------------------------------------------


class UsersView(View):
    """
    本模块用于对用户信息进行增删改查
    """

    def post(self, request):
        # TO DO 用户注册
        result = {
            "state": {
                "msg": "existed",
                'descripntion': 'Null',
            },
        }
        try:
            post = demjson.decode(request.body)
            phone_number = post["phone_number"]
            password = post["password"]
            # veri_code = request.POST.get("veri_code")
            user = models.User.objects.filter(phonenumber=phone_number)
            if len(user) == 1:  # 已存在
                result['state']['msg'] = 'existed'
                return JsonResponse(result)
            elif len(user) == 0:  # 不存在，可以创建
                user = models.User.objects.create(
                    phonenumber=phone_number, password=password)
                user_id = user.id
                result['data'] = {'user_id': user_id}
                result['state']['msg'] = 'successful'
                return JsonResponse(result)
        except Exception as e:
            result['state']['msg'] = 'failed'
            result['state']['description'] = str(repr(e))
            print('\nrepr(e):\t', repr(e))
            print('traceback.print_exc():', traceback.print_exc())
            return JsonResponse(result)

    def get(self, request):
        # TO DO 获取用户信息
        # default_number = 10  # 没有请求数据默认返回数量
        result = {
            "data": {
                "user_id": 0,
                "username": "",
                "email": "",
                "phonenumber": "",
                "avatar": "",
                "introduction": "",
                "follows_number": 0,
                "followers_number": 0,
                "messages_number": 0,
                "comments_number": 0,
                "follows": [],
                "followers": [],
                "messages": [],
                "comments": [],
            },
            "state": {
                'msg': 'failed',
                'descripntion': 'Null',
            }
        }
        try:
            user_id = request.GET.get('user_id')
            follows_start = int(request.GET.get('follows_start'))
            follows_number = int(request.GET.get('follows_number'))
            followers_start = int(request.GET.get('followers_start'))
            followers_number = int(request.GET.get('followers_number'))
            messages_start = int(request.GET.get('messages_start'))
            messages_number = int(request.GET.get('messages_number'))
            comments_start = int(request.GET.get('comments_start'))
            comments_number = int(request.GET.get('comments_number'))
            # -----------------------------------------------------
            userInfo = models.User.objects.filter(id=user_id)
            userInfo = userInfo.first()
            result['data']['user_id'] = int(user_id)
            result['data']['username'] = userInfo.username
            result['data']['email'] = userInfo.email
            result['data']['phonenumber'] = userInfo.phonenumber
            result['data']['avatar'] = str(userInfo.avatar)
            result['data']['introduction'] = userInfo.introduction
            result['data']['birth_date'] = str(
                userInfo.birth_date.strftime("%Y-%m-%d"))
            result['data']['gender'] = str(userInfo.gender)
            result['data']['registration_date'] = str(
                userInfo.registration_date.strftime("%Y-%m-%d"))
            '''
            关注的人
            '''
            follows = models.Followship.objects.filter(
                fan=user_id).order_by('date')
            allFollows = len(follows)
            result['data']['follows_number'] = allFollows
            res = self.request_return_user(
                follows, follows_start, follows_number)
            for i in res:
                oneFoll = models.User.objects.get(id=str(i.followed_user))
                result['data']['follows'].append(
                    {
                        "user_id": str(i.followed_user),
                        "username": oneFoll.username,
                        "avatar": str(oneFoll.avatar)
                    }
                )
            '''
            粉丝
            '''
            followers = models.Followship.objects.filter(
                followed_user=user_id).order_by('date')
            allFollowers = len(followers)
            result['data']['followers_number'] = allFollowers
            res = self.request_return_user(
                followers, followers_start, followers_number)
            for i in res:
                oneFoll = models.User.objects.get(id=str(i.fan))
                result['data']['followers'].append(
                    {
                        "user_id": str(i.fan),
                        "username": oneFoll.username,
                        "avatar": str(oneFoll.avatar)
                    }
                )
            '''
            信息
            '''
            messages = models.Message.objects.filter(
                author=user_id).order_by('-add_date')
            allMessages = len(messages)
            result['data']['messages_number'] = allMessages
            res = self.request_return_user(
                messages, messages_start, messages_number)
            for i in res:
                mesImg = models.MessageImage.objects.filter(message=i.id)
                if len(mesImg) >= 3:
                    mesImg = mesImg[:3]
                img = []
                for j in mesImg:
                    img.append(str(j))
                result['data']['messages'].append(
                    {
                        "message_id": str(i.id),
                        "title": i.title,
                        "content": i.content,
                        "like": i.like,
                        "dislike": i.dislike,
                        "comments_number": len(models.Comment.objects.filter(msg=i.id)),
                        "images": img,
                    }
                )
            '''
            评论
            '''
            comments = models.Comment.objects.filter(
                author=user_id).order_by('-add_date')
            allComments = len(comments)
            result['data']['comments_number'] = allComments
            res = self.request_return_user(
                comments, comments_start, comments_number)
            for i in res:
                result['data']['comments'].append(
                    {
                        "comment_id": str(i.id),
                        "content": i.content
                    }
                )
            result['state']['msg'] = 'successful'
        except Exception as e:
            result['state']['msg'] = 'failed'
            result['state']['descripntion'] = repr(e)
            del result['data']
            print('\nrepr(e):\t', repr(e))
            print('traceback.print_exc():', traceback.print_exc())
        return JsonResponse(result)

    def request_return_user(self, allContent, start, num):
        res = allContent
        # 返回全部
        if num == -1:
            res = res
        # 开始位置大于总数
        elif start > len(res) - 1:
            # 总数小于11，返回全部
            if len(res) <= 10:
                res = res
            # 总数较多，返回10条
            else:
                res = res[0:10]
        # 开始位置+请求数量=超出总数
        elif start <= len(res) - 1 and (start+num) > len(res)-1:
            res = res[start:]
        else:
            res = res[start:start+num]
        return res

    def put(self, request):
        # TO DO 修改用户信息
        result = {
            "state": {
                "msg": "successful",
                'descripntion': 'Null',
            },
            "data": {
                "user_id": 0
            }
        }
        try:
            put = demjson.decode(request.body)
            user_id = put['user_id']
            # username = put['username']
            # email = put['email']
            # phonenumber = put['phonenumber']
            # avatar = put['avatar']
            # introduction = put['introduction']
            user = models.User.objects.filter(id=user_id).first()
            if user != None:
                # try:
                if 'username' in put:
                    user.username = put['username']
                if 'email' in put:
                    user.email = put['email']
                if 'phonenumber' in put:
                    user.phonenumber = put['phonenumber']
                if 'avatar' in put:
                    user.avatar = put['avatar']
                if 'introduction' in put:
                    user.introduction = put['introduction']
                if 'birth_date' in put:
                    user.birth_date = datetime.strptime(
                        put['birth_date'], '%Y-%m-%d')
                if 'gender' in put:
                    user.gender = put['gender']
                user.save()
                result['state']['msg'] = 'successful'
                result['data']['user_id'] = user_id
                # except:
                #     result['state']['msg'] = 'failed'
            else:
                result['state']['msg'] = 'wrong'
        except Exception as e:
            result['state']['msg'] = 'failed'
            result['state']['description'] = str(repr(e))
            result.pop('data')
            print('\nrepr(e):\t', repr(e))
            print('traceback.print_exc():', traceback.print_exc())
        return JsonResponse(result)

    def delete(self, request):
        # TO DO 删除用户信息
        # 暂无需实现,保留接口，暂不实现此功能
        pass
# jhc work----------------------------------------------------------------


class MessagesView(View):
    """本模块用于对消息进行增删改查"""

    def post(self, request):
        """接收发送的消息"""
        result = {
            "state": {
                "msg": "successful",
                "description": ""
            },
            "data": {
                "msg_id": 0
            }
        }
        try:
            request_data = demjson.decode(request.body)
            author_id = request_data['user_id']
            pos_x = request_data['position']['pos_x']
            pos_y = request_data['position']['pos_y']
            content = request_data['content']

            authors = models.User.objects.filter(id=author_id)
            # 如果查询用户不存在
            if not authors.exists():
                result['state']['msg'] = 'wrong'
                result['state']['description'] = 'The user does not exist'
                result.pop('data')
                return JsonResponse(result)
            # 如果查询用户已被删除
            elif authors[0].deleted == 1:
                result['state']['msg'] = 'deleted'
                result['state']['description'] = 'The user has been deleted'
                result.pop('data')
                return JsonResponse(result)
            else:
                author = models.User.objects.filter(id=author_id)[0]
                message = models.Message.objects.create(
                    pos_x=pos_x,
                    pos_y=pos_y,
                    content=content,
                    author=author
                )

                if 'title' in request_data.keys():
                    title = request_data['title']
                    message.title = title
                if 'images' in request_data.keys():
                    images = request_data['images']
                    for image in images:
                        messageImage = models.MessageImage.objects.create(
                            message=message, img=image['image_url']
                        )
                        messageImage.save()
                if 'videos' in request_data.keys():
                    videos = request_data['videos']
                    for video in videos:
                        messageVideo = models.MessageVideo.objects.create(
                            message=message, video=video['video_url']
                        )
                        messageVideo.save()
                if 'mentioned' in request_data.keys():
                    mentions = request_data['mentioned']
                    for mention in mentions:
                        mentioned_user = models.User.objects.filter(
                            id=mention['user_id'])[0]
                        message.mention.add(mentioned_user)
                if 'tags' in request_data.keys():
                    tags = request_data['tags']
                    for tag_content in tags:
                        tag_content = tag_content['tag']
                        tag = models.Tag.objects.filter(tag=tag_content)
                        if tag.exists():
                            tag = tag[0]
                            message.tag.add(tag)
                        else:
                            tag = models.Tag.objects.create(tag=tag_content)
                            tag.save()
                            message.tag.add(tag)
                if 'device' in request_data.keys():
                    device = request_data['device']
                    message.device = device
                message.save()
                result['state']['msg'] = 'successful'
                result['data']['msg_id'] = message.id
                return JsonResponse(result)
        except Exception as e:
            result['state']['msg'] = 'failed'
            result['state']['description'] = str(repr(e))
            result.pop('data')
            print('\nrepr(e):\t', repr(e))
            print('traceback.print_exc():', traceback.print_exc())
            return JsonResponse(result)

    def get(self, request):
        # TO DO 获取消息
        result = {
            "data": {
                'msg_id': 0,
                "position": {
                    "pos_x": 0,
                    "pos_y": 0
                },
                "title": "",
                "content": "",
                "author": {
                    "author_id": 0,
                    "username": "",
                    "avatar": ""
                },
                "like": 0,
                "dislike": 0,
                "who_like": [
                ],
                "who_dislike": [
                ],
                "add_date": "",
                "mod_date": "",
                "comments": [
                ],
                "images": [
                ],
                "videos": [
                ],
                "tags": [
                ],
                "mentioned": [
                ],
                "device": ""
            },
            "state": {
                "msg": "",
                "description": ""
            }
        }
        try:
            # request_data = demjson.decode(request.body)
            request_data = request.GET.dict()
            msg_id = request_data['msg_id']
            messages = models.Message.objects.filter(id=msg_id)
            # 如果查询信息不存在
            if not messages.exists():
                result['state']['msg'] = 'wrong'
                result['state']['description'] = 'The message does not exist'
                result.pop('data')
                return JsonResponse(result)
            # 如果查询信息已被删除
            elif messages[0].deleted == 1:
                result['state']['msg'] = 'deleted'
                result['state']['description'] = 'The message has been deleted'
                result.pop('data')
                return JsonResponse(result)
            else:
                message = messages[0]
                author = message.author
                result['data']['msg_id'] = message.id
                result['data']['position']['pos_x'] = message.pos_x
                result['data']['position']['pos_y'] = message.pos_y
                result['data']['title'] = message.title
                result['data']['content'] = message.content
                result['data']['author']['author_id'] = author.id
                result['data']['author']['username'] = author.username
                result['data']['author']['avatar'] = author.avatar
                result['data']['like'] = message.like
                result['data']['dislike'] = message.dislike
                result['data']['device'] = message.device
                for i, user in enumerate(message.who_like.all()):
                    user_info = {
                        "user_id": user.id,
                        "username": user.username,
                        "avatar": user.avatar
                    }
                    result['data']['who_like'].append(user_info)
                    if i >= 9:
                        break
                for i, user in enumerate(message.who_dislike.all()):
                    user_info = {
                        "user_id": user.id,
                        "username": user.username,
                        "avatar": user.avatar
                    }
                    result['data']['who_dislike'].append(user_info)
                    if i >= 9:
                        break
                result['data']['add_date'] = message.add_date.astimezone(
                    timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
                result['data']['mod_date'] = message.mod_date.astimezone(
                    timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
                for i, comment in enumerate(message.comment_set.filter(type='parent')):
                    comment_info = {
                        "comment_id": comment.id,
                        "content": comment.content,
                        'like': comment.like,
                        "child_comments_number": comment.comment_parent_comment_set.count(),
                        'author': {
                            'author_id': comment.author.id,
                            'username': comment.author.username,
                            'avatar': comment.author.avatar
                        }
                    }
                    result['data']['comments'].append(comment_info)
                    if i >= 9:
                        break
                for i, image in enumerate(message.messageimage_set.all()):
                    image_info = {
                        'image_url': image.img
                    }
                    result['data']['images'].append(image_info)
                for i, video in enumerate(message.messagevideo_set.all()):
                    video_info = {
                        'video_url': video.video
                    }
                    result['data']['videos'].append(video_info)
                for tag in message.tag.all():
                    tag_info = {
                        'tag': tag.tag
                    }
                    result['data']['tags'].append(tag_info)
                for mention in message.mention.all():
                    mention_info = {
                        'user_id': mention.id
                    }
                    result['data']['mentioned'].append(mention_info)

                result['state']['msg'] = 'successful'
                return JsonResponse(result)
        except Exception as e:
            result['state']['msg'] = 'failed'
            result['state']['description'] = str(repr(e))
            result.pop('data')
            print('\nrepr(e):\t', repr(e))
            print('traceback.print_exc():', traceback.print_exc())
            return JsonResponse(result)

    def put(self, request):
        # TO DO 修改消息
        result = {
            "state": {
                "msg": "",
                "description": ""
            },
            "data": {
                "msg_id": 0
            }
        }
        try:
            request_data = demjson.decode(request.body)
            msg_id = request_data['msg_id']
            messages = models.Message.objects.filter(id=msg_id)
            # 如果查询信息不存在
            if not messages.exists():
                result['state']['msg'] = 'wrong'
                result['state']['description'] = 'The message does not exist'
                result.pop('data')
                return JsonResponse(result)
            # 如果查询信息已被删除
            elif messages[0].deleted == 1:
                result['state']['msg'] = 'deleted'
                result['state']['description'] = 'The message has been deleted'
                result.pop('data')
                return JsonResponse(result)
            else:
                message = messages[0]
                if 'title' in request_data.keys():
                    message.title = request_data['title']
                if 'content' in request_data.keys():
                    message.content = request_data['content']
                if 'images' in request_data.keys():
                    message.messageimage_set.all().delete()
                    for image in request_data['images']:
                        message_image = models.MessageImage.objects.create(
                            img=image['image_url'],
                            message=message
                        )
                        message_image.save()
                if 'videos' in request_data.keys():
                    message.messagevideo_set.all().delete()
                    for video in request_data['videos']:
                        message_video = models.MessageVideo.objects.create(
                            video=video['video_url'],
                            message=message
                        )
                        message_video.save()
                if 'mentioned' in request_data.keys():
                    message.mention.remove(*message.mention.all())
                    mentions = request_data['mentioned']
                    for mention in mentions:
                        mentioned_user = models.User.objects.filter(
                            id=mention['user_id'])[0]
                        message.mention.add(mentioned_user)
                if 'tags' in request_data.keys():
                    message.tag.remove(*message.tag.all())
                    tags = request_data['tags']
                    for tag_content in tags:
                        tag = models.Tag.objects.filter(tag=tag_content)
                        if tag.exists():
                            tag = tag[0]
                            message.tag.add(tag)
                        else:
                            tag = models.Tag.objects.create(tag=tag_content)
                            tag.save()
                            message.tag.add(tag)
                if 'device' in request_data.keys():
                    device = request_data['device']
                    message.device = device
                message.save()
                result['state']['msg'] = 'successful'
                result['data']['msg_id'] = message.id
                return JsonResponse(result)
        except Exception as e:
            result['state']['msg'] = 'failed'
            result['state']['description'] = str(repr(e))
            result.pop('data')
            print('\nrepr(e):\t', repr(e))
            print('traceback.print_exc():', traceback.print_exc())
            return JsonResponse(result)

    def delete(self, request):
        # TO DO 删除消息
        result = {
            "state": {
                "msg": "",
                "description": ""
            },
            "data": {
                "msg_id": 0
            }
        }
        try:
            request_data = demjson.decode(request.body)
            msg_id = request_data['msg_id']
            messages = models.Message.objects.filter(id=msg_id)
            # 如果查询信息不存在
            if not messages.exists():
                result['state']['msg'] = 'wrong'
                result['state']['description'] = 'The message does not exist'
                result.pop('data')
                return JsonResponse(result)
            # 如果查询信息已被删除
            elif messages[0].deleted == 1:
                result['state']['msg'] = 'deleted'
                result['state']['description'] = 'The message has been deleted'
                result.pop('data')
                return JsonResponse(result)
            else:
                message = messages[0]
                message.deleted = 1
                message.save()
                result['state']['msg'] = 'successful'
                result['data']['msg_id'] = msg_id
                return JsonResponse(result)
        except Exception as e:
            result['state']['msg'] = 'failed'
            result['state']['description'] = str(repr(e))
            result.pop('data')
            print('\nrepr(e):\t', repr(e))
            print('traceback.print_exc():', traceback.print_exc())
            return JsonResponse(result)


# jhc----------------
class CommentsView(View):
    """
    本模块用于对评论进行增删改查；
    """

    def post(self, request):
        # TO DO 发送评论
        result = {
            "state": {
                "msg": "failed",
                "description": ""
            },
            "data": {
                "comment_id": 0
            }
        }
        comment = demjson.decode(request.body)
        # print(comment)
        # user_id = request.POST.get("user_id")
        # content = request.POST.get("content")
        # msg_id = request.POST.get("msg_id")
        # print(user_id, msg_id)
        try:
            user = models.User.objects.filter(id=comment['user_id'])
            if len(user) == 0:
                result['state']['msg'] = 'wrong'
                result['state']['description'] = 'Use a non-existent user or information id to send a comment'
                result.pop('data')
            else:
                user = user[0]
                mess = models.Message.objects.filter(id=comment['msg_id'])[0]
                comm = models.Comment.objects.create(
                    msg=mess,
                    content=comment['content'],
                    author=user,
                    type="parent",
                )
                comm.save()
                result['state']['msg'] = 'successful'
                result['data']['comment_id'] = comm.id
        except Exception as e:
            result['state']['msg'] = 'failed'
            result['state']['description'] = str(repr(e))
            result.pop('data')
            print('\nrepr(e):\t', repr(e))
            print('traceback.print_exc():', traceback.print_exc())
        return JsonResponse(result)

    def get(self, request):
        # TO DO 获取评论
        result = {
            "data": {
                "comment_id": 0,
                "msg_id": 0,
                "author": {
                    "author_id": "",
                    "username": "",
                    "avatar": ""
                },
                "content": "",
                "like": 0,
                "who_like": [],
                "add_date": "",
                "mod_date": "",
                "reply_to": "",
                "parent_comment_id": "",
                "child_comments": []
            },
            "state": {
                "msg": "failed"
            }
        }

        comment_id = request.GET.get('comment_id')
        try:
            comment = models.Comment.objects.filter(id=comment_id)
            if len(comment) != 0:
                comment = comment.first()
                if comment.deleted != 1:
                    result['data']['comment_id'] = comment.id
                    result['data']['msg_id'] = str(comment.msg)
                    result['data']['author']['author_id'] = str(comment.author)
                    result['data']['author']['username'] = str(
                        comment.author.username)
                    result['data']['author']['avatar'] = str(
                        comment.author.avatar)
                    result['data']['content'] = str(comment.content)
                    result['data']['like'] = comment.like
                    result['data']['add_date'] = str(comment.add_date.astimezone(
                        timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S"))
                    result['data']['mod_date'] = str(comment.mod_date.astimezone(
                        timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S"))
                    result['data']['reply_to'] = str(comment.reply_to)
                    result['data']['parent_comment_id'] = str(
                        comment.parent_comment)
                    if comment.type == "parent":
                        child_comment = models.Comment.objects.filter(
                            type="child", parent_comment=comment_id)
                        for i in child_comment:
                            oneChild = {
                                "comment_id": i.id,
                                'content': str(i.content),
                                'like': i.like,
                                "author": {
                                    "author_id": i.author.id,
                                    "username": str(i.author.username),
                                    "avatar": str(i.author.avatar),
                                }
                            }

                            result['data']['child_comments'].append(oneChild)
                    who_like = comment.who_like.all()
                    for i in who_like:
                        oneLike = {
                            "user_id": i.id,
                            "username": str(i.username),
                            "avatar": str(i.avatar),
                        }
                        result['data']['who_like'].append(oneLike)
                    result['state']['msg'] = 'successful'
                else:
                    result['state']['msg'] = 'deleted'
                    result['state']['description'] = "is Deleted"
            else:
                result['state']['msg'] = 'wrong'
        except Exception as e:
            result['state']['msg'] = 'failed'
            result['state']['description'] = str(repr(e))
            result.pop('data')
            print('\nrepr(e):\t', repr(e))
            print('traceback.print_exc():', traceback.print_exc())
        # print(result)
        result = demjson.decode(str(result))
        return JsonResponse(result)

    def put(self, request):
        # TO DO 修改评论
        pass

    def delete(self, request):
        # TO DO 删除评论
        result = {
            "state": {
                "msg": "failed",
                "description": "",
            },
            "data": {
                "comment_id": 0
            }
        }
        delete = demjson.decode(request.body)
        try:
            comm = models.Comment.objects.filter(id=delete['comment_id'])
            if len(comm) == 0:
                result['state']['msg'] = 'wrong'
                result['state']['description'] = 'Use a non-existent user or information id to send a comment'
                result.pop('data')
            else:
                comm = comm[0]
                if comm.deleted != 1:
                    comm.deleted = 1
                    comm.save()
                    result['state']['msg'] = 'successful'
                    result['data']['comment_id'] = comm.id
                else:
                    result['state']['msg'] = 'deleted'
                    result['state']['description'] = "is Deleted"
        except Exception as e:
            result['state']['msg'] = 'failed'
            result['state']['description'] = str(repr(e))
            result.pop('data')
            print('\nrepr(e):\t', repr(e))
            print('traceback.print_exc():', traceback.print_exc())
        return JsonResponse(result)


def commentsChildComments(request):
    # TO DO 接收子评论
    result = {
        "state": {
            "msg": "failed",
            "description": ""
        },
        "data": {
            "comment_id": 0
        }
    }
    comment = demjson.decode(request.body)
    #       "user_id": "",
    #   "reply_to": "",
    #   "content": "",
    #   "parent_comment_id": "",
    #   "msg_id": ""
    try:
        user = models.User.objects.filter(id=comment['user_id'])
        if len(user) == 0:
            result['state']['msg'] = 'wrong'
            result['state']['description'] = 'Use a non-existent user or information id to send a comment'
            result.pop('data')
        else:
            user = user[0]
            mess = models.Message.objects.filter(id=comment['msg_id'])[0]
            comm = models.Comment.objects.create(
                msg=mess,
                content=comment['content'],
                author=user,
                type="child",
                reply_to=models.User.objects.filter(id=comment['reply_to'])[0],
                parent_comment=models.Comment.objects.filter(
                    id=comment['parent_comment_id'])[0],
            )
            comm.save()
            result['state']['msg'] = 'successful'
            result['data']['comment_id'] = comm.id
    except Exception as e:
        result['state']['msg'] = 'failed'
        result['state']['description'] = str(repr(e))
        result.pop('data')
        print('\nrepr(e):\t', repr(e))
        print('traceback.print_exc():', traceback.print_exc())
    return JsonResponse(result)
# jhc-----------------------------------


class ImagesView(View):
    """本模块用于上传下载图片"""

    def post(self, request):
        # TO DO 上传图片
        result = {
            "data": {
                "image_url": "",
                "description": ""
            },
            "state": {
                "msg": ""
            }
        }
        try:
            image_file = request.FILES.get("image")
            image_type = request.POST.get("type")
            image = models.Image.objects.create(
                img=image_file,
                type=image_type
            )
            image.save()
            result['data']['image_url'] = image.img.url
            result['state']['msg'] = 'successful'
            return JsonResponse(result)
        except Exception as e:
            result['state']['msg'] = 'failed'
            result['state']['description'] = str(repr(e))
            result.pop('data')
            print('\nrepr(e):\t', repr(e))
            print('traceback.print_exc():', traceback.print_exc())
            return JsonResponse(result)

    def get(self, request):
        # TO DO 返回图片
        try:
            url = request.GET.get('image_url')
            url = os.path.join(PROJECT_ROOT, url)
            return FileResponse(open(url, 'rb'))
        except Exception as e:
            result = {
                "state": {
                    "msg": "",
                    "description": ""
                }
            }
            result['state']['msg'] = 'failed'
            result['state']['description'] = str(repr(e))
            print('\nrepr(e):\t', repr(e))
            print('traceback.print_exc():', traceback.print_exc())
            return JsonResponse(result)


class VideosView(View):
    """本模块用于上传下载视频"""

    def post(self, request):
        # TO DO 上传视频
        result = {
            "data": {
                "video_url": "",
                "description": ""
            },
            "state": {
                "msg": ""
            }
        }
        try:
            video_file = request.FILES.get("video")
            video = models.Video.objects.create(
                video=video_file
            )
            video.save()
            result['data']['video_url'] = video.video.url
            result['state']['msg'] = 'successful'
            return JsonResponse(result)
        except Exception as e:
            result['state']['msg'] = 'failed'
            result['state']['description'] = str(repr(e))
            result.pop('data')
            print('\nrepr(e):\t', repr(e))
            print('traceback.print_exc():', traceback.print_exc())
            return JsonResponse(result)

    def get(self, request):
        # TO DO 返回视频
        try:
            url = request.GET.get('video_url')
            url = os.path.join(PROJECT_ROOT, url)
            return FileResponse(open(url, 'rb'))
        except Exception as e:
            result = {
                "state": {
                    "msg": "",
                    "description": ""
                }
            }
            result['state']['msg'] = 'failed'
            result['state']['description'] = str(repr(e))
            print('\nrepr(e):\t', repr(e))
            print('traceback.print_exc():', traceback.print_exc())
            return JsonResponse(result)


def login(request):
    # TO DO 登陆
    result = {
        "state": {
            "msg": "",
            "description": ""
        },
        "data": {
            "cookie": "",
            "user_id": 0
        }
    }
    try:
        request_data = demjson.decode(request.body)
        phone_number = request_data['phone_number']
        password = request_data['password']
        user = models.User.objects.filter(phonenumber=phone_number)[0]
        if user.password == password:
            result['state']['msg'] = 'successful'
            result['data']['user_id'] = user.id
            return JsonResponse(result)
        else:
            result['state']['msg'] = 'wrong'
            return JsonResponse(result)
    except IndexError as e:
        result['state']['msg'] = 'nonexistent'
        result['state']['description'] = str(repr(e))
        result.pop('data')
        print('\nrepr(e):\t', repr(e))
        print('traceback.print_exc():', traceback.print_exc())
        return JsonResponse(result)
    except Exception as e:
        result['state']['msg'] = 'failed'
        result['state']['description'] = str(repr(e))
        result.pop('data')
        print('\nrepr(e):\t', repr(e))
        print('traceback.print_exc():', traceback.print_exc())
        return JsonResponse(result)


def requestVericode(request):
    # TO DO 向用户手机发送验证码，并将验证码存入数据库中
    result = {
        "state": {
            "msg": "",
            "description": ""
        },
        "data": {
            "time_limit": ''
        }
    }
    time_limit = 300
    try:
        request_data = demjson.decode(request.body)
        phone_number = request_data['phone_number']

        client = AcsClient('LTAIFp0' + 'FVf7njxtN',
                           'TJ1NBIx8RqJhqzuM' + 'gC0KtXUzYCxZDw', 'cn-hangzhou')
        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain('dysmsapi.aliyuncs.com')
        request.set_method('POST')
        request.set_protocol_type('https')  # https | http
        request.set_version('2017-05-25')
        request.set_action_name('SendSms')

        request.add_query_param('RegionId', "cn-hangzhou")
        request.add_query_param('PhoneNumbers', phone_number)
        request.add_query_param('SignName', "顺呼验证码")
        request.add_query_param('TemplateCode', "SMS_158051516")
        code = exrex.getone(r"\d{6}")
        request.add_query_param('TemplateParam', "{'code': '%s'}" % code)

        response = client.do_action(request)
        # print(str(response, encoding = 'utf-8'))
        cache.set(phone_number, code, time_limit)
        result['state']['msg'] = 'successful'
        result['data']['time_limit'] = time_limit
        return JsonResponse(result)
    except Exception as e:
        result.pop('data')
        result['state']['description'] = str(repr(e))
        result['state']['msg'] = 'failed'
        print('\nrepr(e):\t', repr(e))
        print('traceback.print_exc():', traceback.print_exc())
        return JsonResponse(result)


def testVericode(request):
    # TO DO 验证验证码是否正确
    result = {
        "state": {
            "msg": "",
            "description": ""
        }
    }
    try:
        request_data = demjson.decode(request.body)
        phone_number = request_data['phone_number']
        vericode = request_data['vericode']
        if vericode == cache.get(phone_number):
            result['state']['msg'] = 'successful'
            return JsonResponse(result)
        else:
            result['state']['msg'] = 'wrong'
            return JsonResponse(result)
    except Exception as e:
        result['state']['msg'] = 'failed'
        result['state']['description'] = str(repr(e))
        print('\nrepr(e):\t', repr(e))
        print('traceback.print_exc():', traceback.print_exc())
        return JsonResponse(result)


def messagesSet(request):
    # TO DO 根据地理信息等返回一组消息
    result = {
        "state": {
            "msg": "",
            "description": ""
        },
        "data": {
            "messages": [
            ]
        }
    }
    try:
        request_data = request.GET.dict()
        user_id = request_data['user_id']
        pos_x = float(request_data['pos_x'])
        pos_y = float(request_data['pos_y'])
        width = float(request_data['width'])
        height = float(request_data['height'])
        number = int(request_data['number'])

        messages = models.Message.objects.filter(
            pos_x__gte=pos_x-width/2, pos_x__lte=pos_x+width/2,
            pos_y__gte=pos_y-height/2, pos_y__lte=pos_y+height/2)
        for i, message in enumerate(messages):
            if i >= number:
                break
            if message.deleted == 1:
                number += 1
                continue
            message_info = {
                "msg_id": message.id,
                "title": message.title,
                "content": message.content,
                "images": [
                ],
                "videos": [
                ],
                "author": {
                    "author_id": message.author.id,
                    "username": message.author.username,
                    "avatar": message.author.avatar
                },
                "position": {
                    "pos_x": message.pos_x,
                    "pos_y": message.pos_y
                }
            }
            # if len(message.messageimage_set.all()) > 0:
            #     message_info['images'].append({
            #         "image_url": message.messageimage_set.all()[0].img
            #     })
            # result['data']['messages'].append(message_info)
            for image in message.messageimage_set.all():
                image_info = {
                    "image_url": image.img
                }
                message_info['images'].append(image_info)
            for video in message.messagevideo_set.all():
                video_info = {
                    "video_url": video.video
                }
                message_info['videos'].append(video_info)
            result['data']['messages'].append(message_info)
        result['state']['msg'] = 'successful'
        return JsonResponse(result)
    except Exception as e:
        result['state']['msg'] = 'failed'
        result['state']['description'] = str(repr(e))
        result.pop('data')
        print('\nrepr(e):\t', repr(e))
        print('traceback.print_exc():', traceback.print_exc())
        return JsonResponse(result)


def messagesLike(request):
    # TO DO 给消息点赞
    result = {
        "state": {
            "msg": "",
            "description": ""
        },
        "data": {
            "msg_id": 0,
            "like": 0,
            "dislike": 0
        }
    }
    try:
        request_data = demjson.decode(request.body)
        msg_id = request_data['msg_id']
        user_id = request_data['user_id']
        users = models.User.objects.filter(id=user_id)
        messages = models.Message.objects.filter(id=msg_id)
        # 如果查询用户不存在
        if not users.exists():
            result['state']['msg'] = 'wrong'
            result['state']['description'] = 'The user does not exist'
            result.pop('data')
            return JsonResponse(result)
        # 如果查询用户已被删除
        elif users[0].deleted == 1:
            result['state']['msg'] = 'deleted'
            result['state']['description'] = 'The user has been deleted'
            result.pop('data')
            return JsonResponse(result)
        # 如果查询消息不存在
        elif not messages.exists():
            result['state']['msg'] = 'wrong'
            result['state']['description'] = 'The message does not exist'
            result.pop('data')
            return JsonResponse(result)
        # 如果查询消息已被删除
        elif messages[0].deleted == 1:
            result['state']['msg'] = 'deleted'
            result['state']['description'] = 'The message has been deleted'
            result.pop('data')
            return JsonResponse(result)
        else:
            message = messages[0]
            user = users[0]
            if user in message.who_like.all():
                result['state']['msg'] = 'wrong'
                result['state']['description'] = "Liked once"
            else:
                message.like += 1
                message.who_like.add(user)
                message.save()
                result['state']['msg'] = 'successful'
            result['data']['msg_id'] = message.id
            result['data']['like'] = message.like
            result['data']['dislike'] = message.dislike
            return JsonResponse(result)
    except Exception as e:
        result.pop('data')
        result['state']['msg'] = 'failed'
        result['state']['description'] = str(repr(e))
        print('\nrepr(e):\t', repr(e))
        print('traceback.print_exc():', traceback.print_exc())
        return JsonResponse(result)


def messagesDislike(request):
    # TO DO 给消息点踩
    result = {
        "state": {
            "msg": "",
            "description": ""
        },
        "data": {
            "msg_id": 0,
            "like": 0,
            "dislike": 0
        }
    }
    try:
        request_data = demjson.decode(request.body)
        msg_id = request_data['msg_id']
        user_id = request_data['user_id']
        users = models.User.objects.filter(id=user_id)
        messages = models.Message.objects.filter(id=msg_id)
        # 如果查询用户不存在
        if not users.exists():
            result['state']['msg'] = 'wrong'
            result['state']['description'] = 'The user does not exist'
            result.pop('data')
            return JsonResponse(result)
        # 如果查询用户已被删除
        elif users[0].deleted == 1:
            result['state']['msg'] = 'deleted'
            result['state']['description'] = 'The user has been deleted'
            result.pop('data')
            return JsonResponse(result)
        # 如果查询消息不存在
        elif not messages.exists():
            result['state']['msg'] = 'wrong'
            result['state']['description'] = 'The message does not exist'
            result.pop('data')
            return JsonResponse(result)
        # 如果查询消息已被删除
        elif messages[0].deleted == 1:
            result['state']['msg'] = 'deleted'
            result['state']['description'] = 'The message has been deleted'
            result.pop('data')
            return JsonResponse(result)
        else:
            message = messages[0]
            user = users[0]
            if user in message.who_dislike.all():
                result['state']['msg'] = 'wrong'
                result['state']['description'] = "Disliked once"
            else:
                message.dislike += 1
                message.who_dislike.add(user)
                message.save()
                result['state']['msg'] = 'successful'
            result['data']['msg_id'] = message.id
            result['data']['like'] = message.like
            result['data']['dislike'] = message.dislike
            return JsonResponse(result)
    except Exception as e:
        result.pop('data')
        result['state']['msg'] = 'failed'
        result['state']['description'] = str(repr(e))
        print('\nrepr(e):\t', repr(e))
        print('traceback.print_exc():', traceback.print_exc())
        return JsonResponse(result)


def messagesMentioned(request):
    """查看被@的信息"""
    result = {
        "state": {
            "msg": "",
            "description": ""
        },
        "data": {
            "messages": [
            ]
        }
    }
    try:
        request_data = request.GET.dict()
        user_id = request_data['user_id']
        time_limit = int(request_data['time_limit'])
        count_limit = int(request_data['count_limit'])
        user_id = request_data['user_id']
        users = models.User.objects.filter(id=user_id)
        # 如果查询用户不存在
        if not users.exists():
            result['state']['msg'] = 'wrong'
            result['state']['description'] = 'The user does not exist'
            result.pop('data')
            return JsonResponse(result)
        # 如果查询用户已被删除
        elif users[0].deleted == 1:
            result['state']['msg'] = 'deleted'
            result['state']['description'] = 'The user has been deleted'
            result.pop('data')
            return JsonResponse(result)
        else:
            user = users[0]
            start_time = datetime.now() - timedelta(hours=time_limit)
            if time_limit == -1 and count_limit == -1:
                messages = user.message_mention_user.filter().order_by('-add_date')
            elif time_limit == -1 and count_limit >= 0:
                messages = user.message_mention_user.filter().order_by(
                    '-add_date')[0: count_limit]
            elif time_limit >= 0 and count_limit == -1:
                messages = user.message_mention_user.filter(
                    add_date__gt=start_time).order_by('-add_date')
            else:
                messages = user.message_mention_user.filter(
                    add_date__gt=start_time).order_by('-add_date')[0: count_limit]
            for message in messages:
                message_info = {
                    "msg_id": message.id,
                    "title": message.title,
                    "content": message.content,
                    "author": {
                        "author_id": message.author.id,
                        "username": message.author.username,
                        "avatar": message.author.avatar
                    }
                }
                result['data']['messages'].append(message_info)
            result['state']['msg'] = 'successful'
            return JsonResponse(result)
    except Exception as e:
        result.pop('data')
        result['state']['msg'] = 'failed'
        result['state']['description'] = str(repr(e))
        print('\nrepr(e):\t', repr(e))
        print('traceback.print_exc():', traceback.print_exc())
        return JsonResponse(result)


def commentsLike(request):
    # TO DO 给评论点赞
    result = {
        "state": {
            "msg": "",
            "description": ""
        },
        "data": {
            "comment_id": 0,
            "like": 0,
        }
    }
    try:
        request_data = demjson.decode(request.body)
        comment_id = request_data['comment_id']
        user_id = request_data['user_id']
        users = models.User.objects.filter(id=user_id)
        comments = models.Comment.objects.filter(id=comment_id)
        # 如果查询用户不存在
        if not users.exists():
            result['state']['msg'] = 'wrong'
            result['state']['description'] = 'The user does not exist'
            result.pop('data')
            return JsonResponse(result)
        # 如果查询用户已被删除
        elif users[0].deleted == 1:
            result['state']['msg'] = 'deleted'
            result['state']['description'] = 'The user has been deleted'
            result.pop('data')
            return JsonResponse(result)
        # 如果查询评论不存在
        elif not comments.exists():
            result['state']['msg'] = 'wrong'
            result['state']['description'] = 'The comment does not exist'
            result.pop('data')
            return JsonResponse(result)
        # 如果查询评论已被删除
        elif comments[0].deleted == 1:
            result['state']['msg'] = 'deleted'
            result['state']['description'] = 'The comment has been deleted'
            result.pop('data')
            return JsonResponse(result)
        else:
            comment = comments[0]
            user = users[0]
            if user in comment.who_like.all():
                result['state']['msg'] = 'wrong'
                result['state']['description'] = "Liked once"
            else:
                comment.like += 1
                comment.who_like.add(user)
                comment.save()
                result['state']['msg'] = 'successful'
            result['data']['comment_id'] = comment.id
            result['data']['like'] = comment.like
            return JsonResponse(result)
    except Exception as e:
        result.pop('data')
        result['state']['msg'] = 'failed'
        result['state']['description'] = str(repr(e))
        print('\nrepr(e):\t', repr(e))
        print('traceback.print_exc():', traceback.print_exc())
        return JsonResponse(result)


def staticResources(request):
    # TO DO 获取静态资源
    try:
        url = request.GET.get('resource_url')
        url = os.path.join(PROJECT_ROOT, url)
        return FileResponse(open(url, 'rb'))
    except Exception as e:
        result = {
            "state": {
                "msg": "",
                "description": ""
            }
        }
        result['state']['msg'] = 'failed'
        result['state']['description'] = str(repr(e))
        print('\nrepr(e):\t', repr(e))
        print('traceback.print_exc():', traceback.print_exc())
        return JsonResponse(result)


def usersDeveces(request):
    result = {
        "state": {
            "msg": "",
            "description": ""
        }
    }
    try:
        request_data = demjson.decode(request.body)
        user_id = request_data['user_id']
        phone_model = request_data['phone_model']
        imei = request_data['imei']
        users = models.User.objects.filter(id=user_id)
        # 如果查询用户不存在
        if not users.exists():
            result['state']['msg'] = 'wrong'
            result['state']['description'] = 'The user does not exist'
            result.pop('data')
            return JsonResponse(result)
        # 如果查询用户已被删除
        elif users[0].deleted == 1:
            result['state']['msg'] = 'deleted'
            result['state']['description'] = 'The user has been deleted'
            result.pop('data')
            return JsonResponse(result)
        devices = models.Device.objects.filter(
            phone_model=phone_model, imei=imei
        )
        if not devices.exists():
            device = models.Device.objects.create(
                phone_model=phone_model, imei=imei
            )
            device.save()
        else:
            device = devices[0]
        user_device = models.UserDevice.objects.create(
            device=device,
            user=users[0]
        )
        user_device.save()
        result['state']['msg'] = 'successful'
        return JsonResponse(result)
    except Exception as e:
        result['state']['description'] = str(repr(e))
        result['state']['msg'] = 'failed'
        print('\nrepr(e):\t', repr(e))
        print('traceback.print_exc():', traceback.print_exc())
        return JsonResponse(result)


def usersFollow(request):
    result = {
        "state": {
            "msg": "",
            "description": ""
        }
    }
    try:
        request_data = demjson.decode(request.body)
        user_id = request_data['user_id']
        followed_user_id = request_data['followed_user_id']
        users = models.User.objects.filter(id=user_id)
        followed_users = models.User.objects.filter(id=followed_user_id)
        # 如果查询用户不存在
        if not users.exists():
            result['state']['msg'] = 'wrong'
            result['state']['description'] = 'The user does not exist'
            return JsonResponse(result)
        # 如果查询用户已被删除
        elif users[0].deleted == 1:
            result['state']['msg'] = 'deleted'
            result['state']['description'] = 'The user has been deleted'
            return JsonResponse(result)
        if not followed_users.exists():
            result['state']['msg'] = 'wrong'
            result['state']['description'] = 'The user does not exist'
            return JsonResponse(result)
        # 如果查询用户已被删除
        elif followed_users[0].deleted == 1:
            result['state']['msg'] = 'deleted'
            result['state']['description'] = 'The user has been deleted'
            return JsonResponse(result)
        user = users[0]
        followed_user = followed_users[0]
        followships = models.Followship.objects.filter(
            fan=user, followed_user=followed_user
        )
        if not followships.exists():
            followship = models.Followship.objects.create(
                fan=user, followed_user=followed_user
            )
            followship.save()
        else:
            followship = followships[0]
            result['state']['msg'] = 'existed'
            return JsonResponse(result)
        result['state']['msg'] = 'successful'
        return JsonResponse(result)
    except Exception as e:
        result['state']['description'] = str(repr(e))
        result['state']['msg'] = 'failed'
        print('\nrepr(e):\t', repr(e))
        print('traceback.print_exc():', traceback.print_exc())
        return JsonResponse(result)


def version(request):
    result = {
        "state": {
            "msg": "",
            "description": ""
        },
        "data": {
            "latest_version": "",
            "download_link": "",
            "description": ""
        }
    }
    try:
        latest_version = models.Version.objects.filter(
        ).order_by('-date')[0]
        result['data']['latest_version'] = latest_version.version
        result['data']['download_link'] = latest_version.download_link
        result['data']['description'] = latest_version.description
        result['state']['msg'] = 'successful'
        return JsonResponse(result)
    except Exception as e:
        result['state']['description'] = str(repr(e))
        result['state']['msg'] = 'failed'
        print('\nrepr(e):\t', repr(e))
        print('traceback.print_exc():', traceback.print_exc())
        return JsonResponse(result)


def home(request):
    if request.method == 'POST':
        latest_version = models.Version.objects.filter(
        ).order_by('-date')[0]
        file = open(latest_version.download_link, 'rb')
        response = HttpResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="shunhu.apk"'
        return response
    return render(request, 'index.html')