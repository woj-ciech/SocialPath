from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from celery.result import AsyncResult
import json
from django.contrib import messages
from socialpath.tasks import socialpath_main, instagram_timeline, reddit_timeline,\
    stackoverflow_timeline, twitter_timeline
from django.apps import apps

from backend import utilsy

from social.models import *

from django.shortcuts import redirect
from social.forms import PostForm

def pinterest(request):
    pass

def search(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['username']
            print(name)
            if not Usernames.objects.filter(username=name).exists():
                u = Usernames(username=name)
                u.save()
                utilsy.create_directory(name)
                print('a')
                main_task = socialpath_main.delay(name=name)
                request.session['task_id'] = main_task.task_id

                return HttpResponseRedirect("/social")
                # return render(request, 'social_index.html', context={'task_id': main_task.task_id})
            else:

                messages.warning(request, 'User already exists in database.')  # <-
                return render(request, 'search.html', {'form': form})
        else:
            messages.error(request, "Error")
    else:
        form = PostForm()

    return render(request, 'search.html', {'form': form})

def delete(request, name):
    p = Usernames.objects.get(username=name)
    p.delete()

    m = apps.get_models()
    for model in m:
        try:
            print(model)
            to_del = model.objects.get(user=name)
            to_del.delete()
        except Exception as e:
            print(e)

    return redirect('users')
    # return redirect("social_index.html")

def delete_platform(request, name, platform):

    platform1 = apps.get_model(app_label='social', model_name=platform)
    p = platform1.objects.get(user=name)
    print(p.profile_pic)
    p.exists = False
    p.save()

    return redirect('details', name)


def get_task_info(request):
    task_id = request.GET.get('task_id', None)
    try:
        if task_id is not None:
            task = AsyncResult(task_id)
            data = {
                'state': task.state,
                'result': task.result,
            }
            return HttpResponse(json.dumps(data), content_type='application/json')
        else:
            return HttpResponse('No job id given.')
    except Exception as e:
        print(e)

def instagram(request, name):
    instagram_details = Insta.objects.get(user=name)
    context = {
        'details': instagram_details
    }

    return render(request, 'instagram.html', context)

def stackoverflow(request, name):
    stackoverflow_details = Stackover.objects.get(user=name)
    context = {
        'details': stackoverflow_details
    }

    return render(request, 'stackoverflow.html', context)

def facebook(request, name):
    facebook_details = Usernames.objects.get(name=name)
    context = {
        'details': facebook_details
    }

    return render(request, 'facebook.html', context)

def reddit(request, name):
    reddit_details = Redd.objects.get(user=name)
    context = {
        'details': reddit_details
    }

    return render(request, 'reddit.html', context)

def twitter(request, name):
    twitter_details = Twitt.objects.get(user=name)
    context = {
        'details': twitter_details
    }

    return render(request, 'twitter.html', context)


def details(request, name):
    print(name)
    details = Usernames.objects.get(username=name)

    context = {
        'details': details
    }

    return render(request, 'social_details.html',context)

def users(request):
    users = Usernames.objects.all()
    task = request.session.get('task_id')

    context = {

        'users': users,
        'task_id':task
    }

    return render(request, 'social_index.html', context)

def get_timeline(request, name, platform):
    if request.is_ajax() and request.method == 'GET':
        if platform == "instagram":
            timeline = instagram_timeline.delay(username=name)
            request.session['task_id'] = timeline.task_id
        if platform == 'reddit':
            timeline = reddit_timeline.delay(username=name)
            request.session['task_id'] = timeline.task_id

        if platform == 'stackoverflow':
            timeline = stackoverflow_timeline.delay(username=name)
            request.session['task_id'] = timeline.task_id

        if platform == 'twitter':
            timeline = twitter_timeline.delay(username=name)
            request.session['task_id'] = timeline.task_id


        return HttpResponse(json.dumps({'task_id': timeline.id}), content_type='application/json')
    else:
        return HttpResponse(json.dumps({'task_id': None}), content_type='application/json')




