from django.db import models
from django.contrib.auth.models import User, Group
from django.utils import dateparse, timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class TMSUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    skills = models.ManyToManyField('Skill', related_name="+")
    reputation = models.PositiveIntegerField(default=0)
    colocate_pref = models.BooleanField(default=False)

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

    def skills_to_json(self):
        return {
                'colocate_pref' : self.colocate_pref,
                'skills': [s.to_json() for s in self.skills.all()]
            }

class TMSGroup(models.Model):
    name = models.CharField(max_length=50)
    members = models.ManyToManyField('TMSUser', related_name="groups")
    cumulative_rep = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def set_group_rep(self):
        self.cumulative_rep = sum([u.reputation for u in self.members.all()])

class Skill(models.Model):
    name = models.ForeignKey('SkillRepo', related_name="+")
    level = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])

    def __str__(self):
        if self.name is not None:
            return self.name.name
        else:
            return ''

    def __unicode__(self):
        if self.name is not None:
            return self.name.name
        else:
            return ''

    def to_json(self):
        return {
                'name': self.name,
                'level': self.level
            }


class SkillRepo(models.Model):
    name = models.CharField(max_length=10, primary_key=True)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

class Course(models.Model):
    title = models.CharField(max_length=50)
    instructor = models.CharField(max_length=20)
    semester = models.CharField(max_length=10)
    students = models.ManyToManyField(TMSUser, related_name="courses")

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
    parent = models.ForeignKey('self', null=True, related_name="children")
    title = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    start = models.DateTimeField(null=True)
    end = models.DateTimeField(null=True)

    cowner = models.ForeignKey(Course, null=True, related_name="tasks")
    uowner = models.ForeignKey(TMSUser, null=True, related_name="tasks")

    skills = models.ManyToManyField('Skill', related_name="+")

    grouped = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    evaluated = models.BooleanField(default=False)

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

    def to_json(self):
        if self.end < timezone.now():
            self.completed = True
            self.save()

        ret = {
            'id': self.title.replace(' ', '_').lower(),
            'title': self.title,
            'description': self.description,
            'start': self.start.strftime('%m-%d-%Y %H:%M:%S'),
            'end': self.end.strftime('%m-%d-%Y %H:%M:%S'),
            'grouped': self.grouped,
            'completed': self.completed,
            'evaluated': self.evaluated,
            'skills': [s.name for s in self.skills.all()]
        }

        return ret

