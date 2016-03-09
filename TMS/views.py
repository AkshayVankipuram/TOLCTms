from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.conf import settings
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from TMS import models, color
from itertools import chain
import json, os

def pre_login(request):
    if request.user.is_authenticated():
        return redirect('/home')
    return render(request, 'login.html', {
        'title': 'Login',
        'user_login': {
            'url': '/',
            'msg': 'Login',
            'name': ''
        }
    })

def login_user(request):
    if request.user.is_authenticated():
        return redirect('/home')
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            return redirect('/home')
        else:
            return redirect('/?auth_status=failed')
    else:
        return redirect('/?auth_status=failed')

def logout_user(request):
    logout(request)
    return redirect('/')

def home(request):
    if not request.user.is_authenticated():
        return redirect('/')
    return render(request, 'dashboard.html', {
        'title': 'Dashboard',
        'user_login': {
            'url': '/logout',
            'msg': 'Logout',
            'name': request.user.username,
        },
        'taskData': get_tasks_for_user(request.user),
        'prefs': {
            'current': get_prefs(request.user),
            'allskills': sorted([s.name for s in models.Skill.objects.all()])
        }
   })

def bulletin(request):
    c = request.GET.get('course', '')
    t = request.GET.get('title', '')

    cprefs = get_prefs(request.user)
    cskills = [cprefs['skill_1']['name'], cprefs['skill_2']['name'], cprefs['skill_3']['name']]

    context = {'title' : 'Bulletin Board'}
    course = models.Course.objects.get(title=c)
    if course is not None:
        context['name'] = course.title
        task = course.tasks.get(title=t)
        if task is not None:
            j = task.to_json()
            context['task'] = j.copy()
            context['task']['skills'] = []
            for skill in j['skills']:
                if skill not in cskills:
                    context['task']['skills'].append(skill)
    context["yskills"] = cskills
    context["user_login"] = {
        'url': '/logout',
        'msg': 'Logout',
        'name': request.user.username,
    }

    return render(request, 'bulletin.html', context)   

def chart_data(request):
    c = request.GET.get('course', '')
    course = models.Course.objects.get(title=c)

    cprefs = get_prefs(request.user)
    cskills = [cprefs['skill_1']['name'], cprefs['skill_2']['name'], cprefs['skill_3']['name']]

    if course is not None:
        chartdata = { 'name': course.title, 'children': [] }
        allskills = models.Skill.objects.exclude(name__in=cskills).all()
        for skill in allskills:
            students_with_skill = course.students.filter(Q(skill_1=skill) | Q(skill_2=skill) | Q(skill_3=skill))
            chartdata['children'].append({ 'name' : skill.name.capitalize(), 'children': [] })
            for student in students_with_skill.all():
                chartdata['children'][len(chartdata['children']) - 1]['children'].append({
                        'name': student.get_username().capitalize(), 
                        'size': (student.skill_1_lvl + student.skill_2_lvl + student.skill_3_lvl) / 3.0 * (student.reputation + 1)
                    })

    return JsonResponse(chartdata)

def calendar(request):
    if not request.user.is_authenticated():
        return redirect('/')
    return render(request, 'calendar.html', {
            'title': 'Calendar',
        })

def feedback(request):
    return HttpResponse("OK")

def get_tasks_for_user(user):
    u = models.TMSUser.objects.get(user=user)
    ret = {}
    if u is not None:
        for course in u.courses.all():
            ret[course.title] = { 'instructor' : course.instructor, 'semester': course.semester, 'tasks': course.get_tasks() }
    return ret

def get_prefs(user):
    u = models.TMSUser.objects.get(user=user)
    if u is not None:
        return u.skills_to_json()
    else:
        return []

def get_tasks(user):
    u = models.TMSUser.objects.get(user=user)
    ret = []
    if u is not None:
        for course in u.courses.all():
            i = { 'name': course.title, 'tasks': [] }
            for task in course.tasks.all():
                i['tasks'].append(task.to_json())
            ret.append(i)
    return ret

def save_skills(request):
    skills = json.loads(request.GET.get('skills', '{}'))
    print(skills)
    return HttpResponse("OK")


def save_event(request):
    #j = json.loads(request.GET.get('event', '{}'))
    #t = models.Task.objects.get(title=j['title'])
    #if t is not None:
        #t.set_from_cal_event_format(j)
        #t.save()
    return HttpResponse('OK')

def event_stream(request):
    return JsonResponse({})

def resource_stream(request):
    return JsonResponse({})


def get_relevant_tasks(user):
    u = models.TMSUser.objects.get(user=user)
    return json.dumps(u.upcoming_deadlines())

def get_tasks_by_title(user):
    u = models.TMSUser.objects.get(user=user)
    ret = []
    if u is not None:
        for course in u.courses.all():
            ret.extend([t['title'] for t in course.get_tasks()])
        ret.extend([t['title'] for t in u.get_tasks(True)])
    return ret

def get_logged_users(request):
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    uids = [session.get_decoded().get('_auth_user_id', None) for session in sessions]
    ret = []
    for u in User.objects.filter(id__in=uids).exclude(username=request.user.username).all():
        print(u.username)
        tms = models.TMSUser.objects.get(user=u)
        ret.append(tms.get_username())
    return JsonResponse(ret, safe=False)
