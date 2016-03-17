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
    dbskills = list(models.SkillRepo.objects.all())
    for name in names:
        u = models.TMSUser()
        print('Creating ' + name)
        u.create_user(name, name+'pass', name, name+'@tolc.edu')
        num_skills = random.randint(0, 4)
        u.save()
        for i in range(0, num_skills):
            s = models.Skill()
            s.name = dbskills[random.randint(0, len(dbskills) - 1)]
            s.level = random.randint(1, 5)
            s.save()
            u.skills.add(s)
        b = random.randint(0, 1)
        if b == 0:
            u.colocate_pref = False
        else:
            u.colocate_pref = True
        u.save()
