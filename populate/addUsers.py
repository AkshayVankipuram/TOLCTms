from TMS import models, views
from django.conf import settings
from random import randint
import os

def read_file(fname, names):
	f = open(fname, 'r')
	for line in f.read().split('\n'):
		s = line.split()
		if len(s) > 1:
			names.append(s[0].lower())

def populate(names):
	dbskills = list(models.Skill.objects.all())
	for name in names:
		u = models.TMSUser()
		print('Creating ' + name)
		u.create_user(name, name+'pass', name, name+'@tolc.edu')
		u.skill_1 = dbskills[randint(0, len(dbskills) - 1)]
		u.skill_1_lvl = randint(1, 5)
		u.skill_2 = dbskills[randint(0, len(dbskills) - 1)]
		u.skill_2_lvl = randint(1, 5)
		u.skill_3 = dbskills[randint(0, len(dbskills) - 1)]
		u.skill_3_lvl = randint(1, 5)
		b = randint(0, 1)
		if b == 0:
			u.colocate_pref = False
		else:
			u.colocate_pref = True
		u.save()
