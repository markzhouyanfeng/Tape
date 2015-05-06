from django.conf.urls import patterns, url
from social_friends_finder.views import FriendListView
from django.contrib.auth.decorators import login_required
from uncontent import views

urlpatterns = patterns('social_friends_finder.views',
	url(r'^$', views.index, name='index'),
	#url(r'^discover/$', views.discover, name='discover'),
	url(r'^collection/(?P<username_collectionname>.*)/$', views.collection, name='collection'),
	url(r'^profile/(?P<username>.*)/$', views.profile, name='profile'),
	url(r'^feed/$', views.feed, name='feed'),
	url(r'^list/$', login_required(FriendListView.as_view()), name='friend_list'),
	
	#url(r'^list/$', login_required(views.FriendListView.as_view()), name='discover'),
	url(r'^discover/$', login_required(views.FriendListView.as_view())),
)
