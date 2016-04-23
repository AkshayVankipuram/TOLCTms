from django.db import models
from django.contrib.auth.models import User, Group
from django.utils import dateparse, timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from statistics import variance

class TMSUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    reputation = models.FloatField(default=0.0)
    colocate = models.BooleanField(default=False)

    skills = models.ManyToManyField('Skill', through="UserSkill", related_name="+")

    def __str__(self):
        if self.user is None:
            return "Please create a user using create_user method"
        else:
            return self.user.username

    def __unicode__(self):
        if self.user is None:
            return "Please create a user using create_user method"
        else:
            return self.user.username

    @staticmethod
    def get_user(username):
        u = User.objects.get(username=username)
        if u is not None:
            return TMSUser.objects.get(user=u)
        else:
            return None

    def get_username(self):
        return self.user.username

    def create_user(self, username, password, firstname, email):
        u = User(username=username, email=email, first_name=firstname)
        u.set_password(password)
        u.save()
        self.user = u

    def delete_user(self):
        u = User.objects.get(username=self.get_username)
        if u is not None:
            u.delete()

class Membership(models.Model):
    user = models.ForeignKey('TMSUser', on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    objective = models.CharField(max_length=50)

    def __str__(self):
        return self.user.get_username() + self.course.title

    def __unicode__(self):
        return self.user.get_username() + self.course.title


class TMSGroup(models.Model):
    name = models.CharField(max_length=50)
    members = models.ManyToManyField('TMSUser', related_name="groups")
    course = models.ForeignKey('Course', null=True, related_name="groups")
    task = models.ForeignKey('Task', null=True, related_name="+")
    completed = models.BooleanField(default=False)
    evaluated = models.BooleanField(default=False)

    variance = models.FloatField(default=0.0)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def get_group_rep(self):
        r = [u.reputation for u in self.members.all()]
        return sum(r)/len(r)

    def set_group_variance(self):
        d = {}
        task_skills = [sk.name for sk in self.task.skills.all()]
        for u in self.members.all():
            us = UserSkill.objects.filter(user=u).all()
            for s in us:
                if s.skill.name in task_skills:
                    if s.skill.name not in d:
                        d[s.skill.name] = []
                    d[s.skill.name].append(s.level)
        r = [variance(d[sd]) for sd in d]
        self.variance = sum(r)/len(r)
        self.save()

class Skill(models.Model):
    name = models.CharField(max_length=15)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

class UserSkill(models.Model):
    user = models.ForeignKey('TMSUser', on_delete=models.CASCADE)
    skill = models.ForeignKey('Skill', on_delete=models.CASCADE)
    level = models.FloatField(default=1.0, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])

    def __str__(self):
        return self.user.get_username() + self.skill.name

    def __unicode__(self):
        return self.user.get_username() + self.skill.name


class Course(models.Model):
    title = models.CharField(max_length=50)
    instructor = models.CharField(max_length=20)
    semester = models.CharField(max_length=10)
    students = models.ManyToManyField(TMSUser, through="Membership", related_name="courses")

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title

    def get_tasks(self):
        ret = []
        for task in self.tasks.all():
            ret.append(task.to_json())
        return ret

class Task(models.Model):
    title = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    start = models.DateTimeField(null=True)
    end = models.DateTimeField(null=True)

    skills = models.ManyToManyField('Skill', related_name="tasks")

    course_owner = models.ForeignKey('Course', null=True, related_name="tasks")
    user_owner = models.ForeignKey('TMSUser', null=True, related_name="tasks")

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title

    @staticmethod
    def parse_iso_format(iso_string):
        dt = dateparse.parse_datetime(iso_string)
        return timezone.make_aware(dt)

    @staticmethod
    def parse_time_str(timestr):
        pattern = '%m-%d-%Y %H:%M:%S'
        dt = timezone.datetime.strptime(timestr, pattern)
        return timezone.make_aware(dt)

    def set_date_times_iso(self, start_iso, end_iso):
        self.start = Task.parse_iso_format(start_iso)
        self.end = Task.parse_iso_format(end_iso)

    def set_date_times_str(self, start_str, end_str):
        self.start = Task.parse_time_str(start_str)
        self.end = Task.parse_time_str(end_str)

    def to_json(self, isoformat=True):
        if self.end < timezone.now():
            self.completed = True
            self.save()

        if self.course_owner is not None:
            owner = self.course_owner.title
        elif self.user_owner is not None:
            owner = self.user_owner.get_username()
        else:
            owner = "None"

        format_start = self.start.isoformat()
        format_end = self.end.isoformat()
        if not isoformat:
            format_start = self.start.strftime('%m-%d-%Y %H:%M:%S')
            format_end = self.end.strftime('%m-%d-%Y %H:%M:%S')

        ret = {
            'id': self.title.replace(' ', '_').lower(),
            'title': self.title,
            'description': self.description,
            'start': format_start,
            'end': format_end,
            'owner': owner,
            'skills': [s.name for s in self.skills.all()]
        }

        return ret

