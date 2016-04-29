# TMSPrj
**A time management system for MOOC**

**Install django globally (may require sudo permissions)**
```
$ pip install django
```

**Run manage.py**
```
$ python manage.py runserver
```

**Launch *http://localhost:8000* in the browser**

Logins available (subset)
```
User		Pass
akshay		akshaypass
harshal		harshalpass
bhargavi	bhargavipass
ajith		ajithpass
```
The database has 1003 users. So for more logins you can use any of the user names (lower case) with 'pass' appended for the password.

**In case you are unable to login**

**Run django shell**
```
$ python manage.py runserver
```

**Managing Databases**

If you make any changes to TMS/models.py run the following before continuing 
```
$ python manage.py makemigrations TMS
$ python manage.py migrate
```
