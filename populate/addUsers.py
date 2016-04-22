from TMS import models, views
from django.conf import settings
import random
import os

def read_file(fname, names):
    f = open(fname, 'r')
    for line in f.read().split('\n'):
        s = line.split()
        if len(s) > 1:
            names.append(s[0].lower())

def populate(names):
    random.seed()
    skills = models.Skill.objects.all()
    for name in names:
        u = models.TMSUser()
        print('Creating ' + name)
        u.create_user(name, name+'pass', name, name+'@tolc.edu')
        u.reputation = random.uniform(0.0, 100.0)
        u.save()
        for skill in skills:
            uskill = models.UserSkill(user=u, skill=skill, level=random.uniform(0.0, 5.0))
            uskill.save()


