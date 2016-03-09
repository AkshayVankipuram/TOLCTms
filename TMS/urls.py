"""TMS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from TMS import views

urlpatterns = [
    url(r'^$', views.pre_login, name="pre_login"),
    url(r'^login/$', views.login_user, name="login"),
    url(r'^logout/$', views.logout_user, name="logout"),
    url(r'^home/$', views.home, name="home"),
    url(r'^bulletin/', views.bulletin, name="bullentin"),
    url(r'^chart_data/', views.chart_data, name="chart_data"),
    url(r'^calendar/', views.calendar, name="calendar"),
    url(r'^feedback/', views.feedback, name="feedback"),
    url(r'^save_skills/', views.save_skills, name="save_skills"),
    url(r'^save_event/$', views.save_event, name="save_event"),
    url(r'^logged_users/$', views.get_logged_users, name="get_logged_users"),
    url(r'^event_stream/$', views.event_stream, name="event_stream"),
    url(r'^resource_stream/$', views.resource_stream, name="resource_stream")
]