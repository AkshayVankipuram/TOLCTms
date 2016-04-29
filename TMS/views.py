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
import json, os, random
from statistics import variance

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
        'reputation': u.reputation,
        'colocate': u.colocate,    
        'objectives': get_objectives(u, None),    
        'notifications': get_notifications(u),
        'skills': [skill.name for skill in models.Skill.objects.all()]
   })


def get_objectives(user, c):
    def get_vals(course):
        m = models.Membership.objects.filter(Q(user=user)&Q(course=course)).all()
        objs = list(set([me.objective for me in models.Membership.objects.all()]))
        return {
            'myobj': m[0].objective,
            'myobjid': '{0}-{1}'.format(course.title.replace(' ','_'), m[0].objective),
            'objs': [{
                'name': o,
                'id': '{0}-{1}'.format(course.title.replace(' ','_'), o)
                } for o in objs]
        }
    if c == None:
        ret= {}
        for c in user.courses.all():
            ret[c.title] = get_vals(c)
        return ret
    else:
        return get_vals(c)


def set_objective(request):
    u = models.TMSUser.objects.get(user=request.user)
    c = request.GET.get('course', '')
    obj = request.GET.get('objective', '')
    course = models.Course.objects.get(title=c)
    m = models.Membership.objects.filter(user=u).filter(course=course).all()
    if m:
        old = m[0].objective
        m[0].objective = obj
        m[0].save()
        return JsonResponse({
                'status': True,
                'old': old,
                'old_id': '{0}-{1}'.format(course.title.replace(' ','_'), old),
                'new': m[0].objective,
                'new_id': '{0}-{1}'.format(course.title.replace(' ','_'), m[0].objective)
            })
    else:
        return JsonResponse({
                'status': False
            })
def get_notifications(user):
    ret = { 'to_begin': [], 'completed': [] }
    for course in user.courses.all():
        for task in course.tasks.filter(user_owner=None).all():
            g = user.groups.filter(task=task).all()
            if not g:
                t = task.to_json()
                abbr = [w[0].upper() for w in course.title.split(' ')]
                t['course_abbr'] = ''.join(abbr[:2])
                ret['to_begin'].append(t)
            elif g and g[0].completed:
                ret['completed'].append(g[0].task.title)
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
        u = models.TMSUser.objects.get(user=request.user)
        us = models.UserSkill.objects.filter(user=u).all()
        context['skill_names'] = [s[:min(4, len(s))].capitalize() for s in task_skills]
        context['hidden'] = len(context['skill_names']) + 3
        context['skill_vals'] = [s.level for s in us if s.skill.name in task_skills] + \
                [maprange((0.0, 100.0),(0.0, 5.0),u.reputation)]
        context['user_login'] = {
            'url': '/logout',
            'msg': 'Logout',
            'name': request.user.username
        }
        context['objectives'] = get_objectives(u, models.Course.objects.get(title=c))
        return render(request, 'bulletin.html', context)
    else:
        return redirect('/')

def create_group(request):
    names = json.loads(request.GET.get('group', '[]'))
    gname = request.GET.get('name', '')
    task = request.GET.get('task', '')
    course = request.GET.get('course', '')

    t = models.Task.objects.get(title=task)
    c = models.Course.objects.get(title=course)
    g = models.TMSGroup(name=gname, task=t, course=c)
    g.save()
    for name in names:
        u = models.TMSUser.get_user(name)
        g.members.add(u)
    g.set_group_variance()
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
            us = models.UserSkill.objects.filter(user=cu).all()
            return [{'axis': s.skill.name, 'value': s.level / 5.0} for s in us if s.skill.name in task_skills] + \
                [{'axis': 'reputation', 'value': maprange((0.0, 100.0),(0.0, 1.0),cu.reputation)}]

        return JsonResponse([get_skill(cu) for cu in ous], safe=False)
    else:
        u = models.TMSUser.objects.get(user=request.user)
        us = models.UserSkill.objects.filter(user=u).all()
        return JsonResponse([{'axis': s.skill.name, 'value': s.level / 5.0} for s in us] + \
                [{'axis': 'reputation', 'value': maprange((0.0, 100.0),(0.0, 1.0),u.reputation)}], safe=False)

def table_data(request):
    c = request.GET.get('course', '')
    t = request.GET.get('task', '')
    o = request.GET.get('objective', '')

    user = models.TMSUser.objects.get(user=request.user)
    course = models.Course.objects.get(title=c)
    context = { 'data' : [] }
    task = models.Task.objects.get(title=t)
    task_skills = [ts.name for ts in task.skills.all()]

    myskills = [us.level for us in models.UserSkill.objects.filter(user=user).all() if us.skill.name in task_skills]

    #mem = models.Membership.objects.filter(Q(user=user)&Q(course=course)).all()
    for u in course.students.exclude(user=request.user).all():
        m = models.Membership.objects.filter(Q(user=u)&Q(course=course)).all()
        if (o != '' and m[0].objective == o) or o == '':
            g = u.groups.filter(task=task)
            if not g:
                us = models.UserSkill.objects.filter(user=u).all()
                skill_vals = [round(s.level, 2) for s in us if s.skill.name in task_skills]
                context['data'].append([
                        u.get_username().capitalize(),
                        u.user.email] +
                        skill_vals + [
                        maprange((0.0, 100.0),(0.0, 5.0),u.reputation),
                        get_skill_var(myskills, user.reputation, skill_vals, u.reputation)
                     ])

    return JsonResponse(context)

def get_skill_var(ms, mre, os, ore):
    d = [variance([os[i],ms[i]]) for i in range(len(ms))] + [variance([ore,mre])]
    return round(sum(d)/len(d), 2)

def get_skill_breakdown(request):
    u = models.TMSUser.objects.get(user=request.user)

    context = {}
    for group in u.groups.all():
        duration = '02:00'
        context[group.task.title] = [{
            'title': skill.name,
            'description': '',
            'duration': '{0}:00'.format(duration),
            'stick': True,
            'resourceID': u.get_username()
        } for skill in group.task.skills.all()]
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
                'completed': group.completed
                })
            events.append(obj)
            for member in group.members.all():
                for task in member.tasks.filter(course_owner=course).exclude(title=group.task.title).all():
                    rid = '{0}_{1}'.format(group.name.lower(), member.get_username()).replace(' ', '_')
                    if member == u:
                        rid = 'CU_' + rid
                    obj = task.to_json()
                    obj.update({
                            'editable': (member.get_username() == u.get_username()),
                            'resourceId': rid,
                            'completed': task.completed
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
                id = '{0}_{1}'.format(group.name.lower(), member.get_username()).replace(' ', '_')
                if member == u:
                    id = 'CU_' + id
                obj['children'].append({
                        'id': id,
                        'title': member.get_username().capitalize(),
                        'course': course.title,
                        'editable': (member.get_username() == u.get_username())
                    })
            resources.append(obj)

    return JsonResponse(resources, safe=False)

def feedback(request):
    context = {}
    context["metric_labels"] = ['Knowledge','Communication','Teamwork','ProblemSolving', 'Dependability', 'Leadership', 'Responsiveness']
    context["metric_values"] = ['1','2','3','4','5']

    user = models.TMSUser.objects.get(user=request.user)
    t = request.GET.get('task', '')
    task = models.Task.objects.get(title=t)
    group = user.groups.filter(task=task).all()
    peer_list = [member.get_username() for member in group[0].members.exclude(user=request.user).all()]
    context["peer_list"] = peer_list
    task_skills = [ts.name for ts in task.skills.all()]
    context["task_name"] = task.title;
    context["task_skills"] = task_skills;
    context['user_login'] = {
            'url': '/logout',
            'msg': 'Logout',
            'name': request.user.username
        }

    return render(request, 'feedback.html', context)
    return HttpResponse("OK")

def get_tasks_for_user(user):
    u = models.TMSUser.objects.get(user=user)
    ret = {}
    if u is not None:
        for course in u.courses.all():
            ret[course.title] = { 'instructor' : course.instructor, 'semester': course.semester, 'tasks': course.get_tasks() }
    return ret

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
    j = json.loads(request.GET.get('event', '{}'))
    
    status = 'Fail'
    if j != {}:
        u = models.TMSUser.objects.get(user=request.user)
        c = models.Course.objects.get(title=j['course_owner'])
        t = models.Task()
        t.title = j['title']
        t.description = j['description']
        t.set_date_times_iso(j['start'], j['end'])
        t.user_owner = u
        t.course_owner = c
        t.save()

        for skill in j['skills']:
            if models.Skill.objects.filter(name=skill).exists():
                t.skills.add(models.Skill.objects.get(name=skill))
        t.save()

        status = 'Pass'
    
    return JsonResponse({
            'status': status
        })

def update_event(request):
    u = models.TMSUser.objects.get(user=request.user)
    e = request.GET.get('event', '')
    if e != '':
        t = models.Task.objects.get(title=e)
        if t.user_owner != None:
           t.completed = True
           t.save()
        else: 
            g = u.groups.filter(task=t).all()
            if g:
               g[0].completed = True
               g[0].save()
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

def submit_feedback(request):
    context = {};
    peer = request.GET.get('peer','');
    reputationScore = request.GET.get('reputationScore');
    #context["skillScore"] = request.GET.get('skillScore');
    if(reputationScore != 'NA'):
        u = models.TMSUser.get_user(peer)
        newReputation =( (u.reputation * u.numberofratings) + (maprange([1,5], [0,100], float(reputationScore)) ))  / (u.numberofratings + 1)
        u.reputation = newReputation
        u.numberofratings += 1
        u.save()
    return JsonResponse({})
