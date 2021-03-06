from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^subscriptions/$', views.subscriptions, name='subscriptions'),
	url(r'^(?P<topic_id>[0-9]+)/$', views.detail, name='detail'),
	url(r'^(?P<topic_id>[0-9]+)/subscribe$', views.subscribe, name='subscribe'),
	url(r'^(?P<topic_id>[0-9]+)/unsubscribe$', views.unsubscribe, name='unsubscribe'),
	url(r'^register/$', views.register, name='register'), # ADD NEW PATTERN!
	url(r'^login/$', views.user_login, name='login'),
	url(r'^logout/$', views.user_logout, name='logout'),
	url(r'^search/$', views.get_topics, name='search'),
]