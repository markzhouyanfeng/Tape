from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	# Examples:
	# url(r'^$', 'startup.views.home', name='home'),

	# prevent the extra are-you-sure-you-want-to-logout step on logout
	(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),

	url(r'^', include('uncontent.urls')),
	url(r'^accounts/', include('allauth.urls')),
	
	url(r'^find-friends/', include('social_friends_finder.urls')),
	
	url(r'^tinymce/', include('tinymce.urls')),

	# Uncomment the admin/doc line below to enable admin documentation:
	#url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

	# Uncomment the next line to enable the admin:
	url(r'^admin/', include(admin.site.urls)),
)
