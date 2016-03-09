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

Login with 'testuser' and 'testpass'

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
