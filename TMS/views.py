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
    u = models.TMSUser.objects.get(user=request.user)
    return render(request, 'dashboard.html', {
        'title': 'Dashboard',
        'user_login': {
            'url': '/logout',
            'msg': 'Logout',
            'name': request.user.username,
        },
        'skills': get_skills(u),
        'reputation': u.reputation,
        'colocate': u.colocate,
        'objectives': get_objectives(u),
        'notifications': get_notifications(u),
        'tasktags': [o.title.encode('ascii') for o in models.Task.objects.filter(~Q(parent=None) & Q(user_owner=None)).all()]
   })


def get_objectives(user):
    ret = {}
    for c in user.courses.all():
        m = models.Membership.objects.filter(Q(user=user)&Q(course=c)).all()
        objs = list(set([me.objective for me in models.Membership.objects.all()]))
        ret[c.title] = {
            'myobj': m[0].objective,
            'objs': [{
                'name': o,
                'id': '{0}-{1}'.format(c.title.replace(' ','_'), o)
                } for o in objs]
        }
    return ret

def set_objective(request):
    u = models.TMSUser.objects.get(user=request.user)
    c = request.GET.get('course', '')
    obj = request.GET.get('objective', '')
    course = models.Course.objects.get(title=c)
    m = models.Membership.objects.filter(user=u).filter(course=course).all()
    if m:
        m.objective = obj
        m.save()
    return JsonResponse({
            'status': 'OK'
        })

def get_notifications(user):
    ret = []
    for course in user.courses.all():
        for task in course.tasks.all():
            g = user.groups.filter(task=task).all()
            if not g:
                ret.append(task.to_json())
    return ret

def bulletin(request):
    c = request.GET.get('course', '')
    t = request.GET.get('task', '')

    context = {'title' : 'Bulletin Board', 'course': c }

    u = models.TMSUser.objects.get(user=request.user)
    task = models.Task.objects.get(title=t)
    task_skills = [ts.name for ts in task.skills.all()]
    group_formed = u.groups.filter(task=task).all()

    if not group_formed:
        context['task'] = task.to_json(False)
        for skill in context['task']['skills']:
            if skill['level'] - int(skill['level']) > 0.5:
                v  = int(skill['level']) + 1
            else:
                v = int(skill['level'])
            skill['level'] = (v * [1]) + ((5 - v) * [0])
        u = models.TMSUser.objects.get(user=request.user)
        context['skill_names'] = [s.name[:min(4, len(s.name))].capitalize() for s in u.skills.filter(name__in=task_skills).all()]
        context['skill_vals'] = [s.level for s in u.skills.filter(name__in=task_skills).all()] + \
                [maprange((0.0, 100.0),(0.0, 5.0),u.reputation)]
        context['user_login'] = {
            'url': '/logout',
            'msg': 'Logout',
            'name': request.user.username
        }
        return render(request, 'bulletin.html', context)
    else:
        return redirect('/')

def chart_data(request):
    tp = request.GET.get('tp', 'task')
    if tp == 'task':
        usernames = json.loads(request.GET.get('users', '[]'))
        t = request.GET.get('task', '')
        task = models.Task.objects.get(title=t)
        task_skills = [ts.name for ts in task.skills.all()]

        ous = [models.TMSUser.objects.get(user=request.user)] + \
                [models.TMSUser.get_user(uname.lower()) for uname in usernames]
        def get_skill(cu):
            return [{'axis': s.name, 'value': s.level / 5.0} for s in cu.skills.filter(name__in=task_skills).all()] + \
                [{'axis': 'reputation', 'value': maprange((0.0, 100.0),(0.0, 1.0),cu.reputation)}]

        return JsonResponse([get_skill(cu) for cu in ous], safe=False)
    else:
        u = models.TMSUser.objects.get(user=request.user)
        return JsonResponse([{'axis': s.name, 'value': s.level / 5.0} for s in u.skills.all()] + \
                [{'axis': 'reputation', 'value': maprange((0.0, 100.0),(0.0, 1.0),u.reputation)}], safe=False)

def table_data(request):
    c = request.GET.get('course', '')
    t = request.GET.get('task', '')

    user = models.TMSUser.objects.get(user=request.user)
    course = models.Course.objects.get(title=c)
    context = { 'data' : [] }
    task = models.Task.objects.get(title=t)
    task_skills = [ts.name for ts in task.skills.all()]
    mem = models.Membership.objects.filter(Q(user=user)&Q(course=course)).all()
    for u in course.students.exclude(user=request.user).all():
        m = models.Membership.objects.filter(Q(user=u)&Q(course=course)).all()
        if m[0].objective == mem[0].objective:
            g = u.groups.filter(task=task)
            if not g:
                skill_vals = [round(s.level, 2) for s in u.skills.filter(name__in=task_skills).all()]
                context['data'].append([
                        u.get_username().capitalize(),
                        u.user.email] +
                        skill_vals + [
                        maprange((0.0, 100.0),(0.0, 5.0),u.reputation)
                     ])

    return JsonResponse(context)

def get_skill_breakdown(request):
    u = models.TMSUser.objects.get(user=request.user)

    context = {}
    for group in u.groups.all():
        duration = (group.task.end - group.task.start).total_seconds() / 3600.0 / 4.0
        context[group.task.title] = [{
            'title': child.title,
            'description': child.description,
            'duration': '{0}:00'.format(duration),
            'stick': True,
            'resourceID': u.get_username()
        } for child in group.task.children.all()]
    return JsonResponse(context)


def maprange(a, b, s):
    (a1, a2), (b1, b2) = a, b
    return  b1 + ((s - a1) * (b2 - b1) / (a2 - a1))

def event_stream(request):
    u = models.TMSUser.objects.get(user=request.user)
    events = []
    for course in u.courses.all():
        for group in u.groups.filter(course=course).all():
            obj = group.task.to_json()
            obj.update({
                'ctitle': group.name,
                'editable': False,
                'resourceId': 'group_task_'+group.name.replace(' ', '_').lower(),
                })
            events.append(obj)
    return JsonResponse(events, safe=False)

def resource_stream(request):
    u = models.TMSUser.objects.get(user=request.user)
    resources = []
    for course in u.courses.all():
        for group in u.groups.filter(course=course).all():
            obj = {
                    'course': course.title,
                    'title': group.name,
                    'id': 'group_task_'+group.name.replace(' ', '_').lower(),
                    'editable': False,
                    'children': []
                }
            for member in group.members.all():
                editable = (member.get_username() == u.get_username())
                obj['children'].append({
                        'id': member.get_username().replace(' ', '_'),
                        'title': member.get_username().capitalize(),
                        'course': course.title,
                        'editable': editable,
                    })
            resources.append(obj)

    return JsonResponse(resources, safe=False)

def feedback(request):
    return HttpResponse("OK")

def get_tasks_for_user(user):
    u = models.TMSUser.objects.get(user=user)
    ret = {}
    if u is not None:
        for course in u.courses.all():
            ret[course.title] = { 'instructor' : course.instructor, 'semester': course.semester, 'tasks': course.get_tasks() }
    return ret

def get_skills(u):
    if u is not None:
        return [{
            'name': s.name,
            'rating': round(s.level, 1),
            'id': s.name.replace(' ', '_').lower()
        } for s in u.skills.all()]
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

