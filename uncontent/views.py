from django.template import RequestContext
from django.shortcuts import render_to_response, render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.views.generic import DetailView
from django.views.generic.edit import FormMixin
#from utils import setting
from django.core.urlresolvers import reverse
import datetime
import json
import urllib
import urlparse
from uncontent.models import UserProfile, Collection, Video, Comment
from social_friends_finder.models import SocialFriendList
from uncontent.forms import AddCollectionForm, AddVideoForm, FollowCollectionForm


USING_ALLAUTH = True

#REDIRECT_IF_NO_ACCOUNT = setting('SF_REDIRECT_IF_NO_SOCIAL_ACCOUNT_FOUND', False)
#REDIRECT_URL = setting('SF_REDIRECT_URL', "/")

class FriendListView(TemplateView, DetailView, FormMixin):
	template_name = "/usr/bin/startup/templates/discover.html"
	cform_class = AddCollectionForm
	vform_class = AddVideoForm
	fform_class = FollowCollectionForm
	success_url = '/discover'

	def get(self, request, provider=None):
		self.object = self.get_object()
		if USING_ALLAUTH:
			self.social_auths = request.user.socialaccount_set.all()
		else:
			self.social_auths = request.user.social_auth.all()	
		self.social_friend_lists = []
		if self.social_auths.count() == 0:
			return super(FriendListView, self).get(request)
		self.social_friend_lists = SocialFriendList.objects.get_or_create_with_social_auths(self.social_auths)
		return super(FriendListView, self).get(request)

	def get_context_data(self, **kwargs):
		self.social_auths = self.request.user.socialaccount_set.all()		
		self.social_friend_lists = []
		if self.social_auths.count() != 0:
			self.social_friend_lists = SocialFriendList.objects.get_or_create_with_social_auths(self.social_auths)
		context = super(FriendListView, self).get_context_data(**kwargs)

		thiscollections = Collection.objects.all().filter(user=self.request.user)		
		context['thiscollections'] = thiscollections

		thisprofile = UserProfile.objects.all().filter(user=self.request.user)[0]
		context['thisprofile'] = thisprofile

		curatedcollections = Collection.objects.all().filter(user=UserProfile.objects.all()[0])
		recommendcuratedcollections = [] #all curatedcollections that this user has not followed
		for curatedcollection in curatedcollections:
			if curatedcollection.follower_list is None or curatedcollection.follower_list.find(self.request.user.username) == -1:#not following this collection
				recommendcuratedcollections.append(curatedcollection)
		context['recommendcuratedcollections'] = recommendcuratedcollections
		recommendcuratedvideos = []
		allvideos = Video.objects.all()
		for video in allvideos:
			if video.collection.follower_list is None or video.collection.follower_list.find(self.request.user.username) == -1:#not following this collection
				for recomcol in recommendcuratedcollections:
					if video.collection == recomol:
						recommendcuratedvideos.append(video)
		context['recommendcuratedvideos'] = recommendcuratedvideos

		friends = []
		for friend_list in self.social_friend_lists:
			fs = friend_list.existing_social_friends()
			for f in fs:
				friends.append(f)

		connected_providers = []
		for sa in self.social_auths:
			connected_providers.append(sa.provider)

		friendscollections = []
		allcollection = Collection.objects.all()
		for collection in allcollection:
			if collection.follower_list is None or collection.follower_list.find(self.request.user.username) == -1:#not following this collection
				for friend in friends:
					if collection.user == friend:
						friendscollections.append(collection)
		friendscollections.reverse()
		context['friendscollections'] = friendscollections
		friendsvideos = []
		for video in allvideos:
			if video.collection.follower_list is None or video.collection.follower_list.find(self.request.user.username) == -1:#not following this collection
				for friend in friends:
					if video.user == friend:
						friendsvideos.append(video)
		context['friendsvideos'] = friendsvideos
			
		if 'fform' not in context:
			context['fform'] = self.fform_class()
		if 'vform' not in context:
			context['vform'] = self.vform_class()

		return context
		
	def fform_valid(self, form):
		collectiontofollow = None
		for c in Collection.objects.all():
			if c.name == self.request.POST['tofollowname'] and c.user.username == self.request.POST['username']:
				collectiontofollow = c
				break
		if collectiontofollow.follower_list is None or collectiontofollow.follower_list.find(self.request.user.username) == -1:#this user not following
			if collectiontofollow.follower_list is None:
				collectiontofollow.follower_list = (self.request.user.username+"#")
			else:
				collectiontofollow.follower_list += (self.request.user.username+"#")
			collectiontofollow.save()
			thisprofile = UserProfile.objects.all().filter(user=self.request.user)[0]
			if thisprofile.following_collection_list is None:
				thisprofile.following_collection_list = (collectiontofollow.user.username+"*"+collectiontofollow.name+"#")
			else:
				thisprofile.following_collection_list += (collectiontofollow.user.username+"*"+collectiontofollow.name+"#")
			thisprofile.save()
		return super(FriendListView, self).form_valid(form)
	
	def vform_valid(self, form):
		thisprofile = UserProfile.objects.all().filter(user=self.request.user)[0]
		if not Collection.objects.all().filter(user=self.request.user, name=self.request.POST['collection_name']).exists():
			newcol = Collection(user=self.request.user, name=self.request.POST['collection_name'])
			newcol.collection_url = "uname=" + newcol.user.username + "&cname=" + newcol.name
			newcol.save()
			if thisprofile.collection_list is None:
				thisprofile.collection_list = (self.request.POST['collection_name']+"#")
			else:
				thisprofile.collection_list += (self.request.POST['collection_name']+"#")
			thisprofile.save()
		thiscollections = Collection.objects.all().filter(user=self.request.user)
		collectiontoadd = thiscollections.filter(name=self.request.POST['collection_name'])[0]
		if collectiontoadd.video_list is None or collectiontoadd.video_list.find(self.request.POST['video_url']) == -1:
			if collectiontoadd.video_list is None:
				collectiontoadd.video_list = (self.request.POST['video_url']+"#")
			else:
				collectiontoadd.video_list += (self.request.POST['video_url']+"#")
			newvideo = Video(user=self.request.user, collection=collectiontoadd, video_url=self.request.POST['video_url'], date_time=datetime.datetime.now(), description=self.request.POST['description'])
			s = newvideo.video_url
			if s.find("youtu.be") != -1:
				if s.rfind('?') == -1:
					id = s[s.rfind('/')+1:]
				else:
					id = s[s.rfind('/')+1:s.rfind('?')]
				newvideo.video_url = "https://youtu.be/"+id
				newvideo.image_url = "http://img.youtube.com/vi/"+id+"/0.jpg"
				newvideo.embed_url = "https://www.youtube.com/embed/"+id
			#elif s.find("vimeo.com") != -1:
				#id = s[s.rfind('/')+1:]
				#newvideo.embed_url = "https://player.vimeo.com/video/"+id
			newvideo.save()
			collectiontoadd.cover_image_url = newvideo.image_url
			collectiontoadd.cover_video_embed_url = newvideo.embed_url
			collectiontoadd.save()
		return super(FriendListView, self).form_valid(form)
	
	def form_invalid(self, **kwargs):
		return self.render_to_response(self.get_context_data(**kwargs))	

	def get_object(self):
		return get_object_or_404(SocialFriendList, pk=1)
		
	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		if 'fform' in request.POST:
			form_class = self.fform_class
			form_name = 'fform'
			form = self.get_form(form_class)
			if form.is_valid():
				return self.fform_valid(form)
		else:
			form_class = self.vform_class
			form_name = 'vform'
			form = self.get_form(form_class)
			if form.is_valid():
				return self.vform_valid(form)
		return self.form_invalid(**{form_name: form})		
	
def index(request):
	return render_to_response("index.html", RequestContext(request))

def addvideo(request):
	context = RequestContext(request)
	form = None
	thiscollections = None
	if request.user.is_authenticated():
		if request.method == 'POST':
			form = AddVideoForm(request.POST)
			if form.is_valid():
				thisprofile = UserProfile.objects.all().filter(user=request.user)[0]
				if not Collection.objects.all().filter(user=request.user, name=request.POST['collection_name']).exists():
					newcol = Collection(user=request.user, name=request.POST['collection_name'])
					newcol.collection_url = "uname=" + newcol.user.username + "&cname=" + newcol.name
					newcol.save()
					if thisprofile.collection_list is None:
						thisprofile.collection_list = (request.POST['collection_name']+"#")
					else:
						thisprofile.collection_list += (request.POST['collection_name']+"#")
				thisprofile.save()
				thiscollections = Collection.objects.all().filter(user=request.user)
				collectiontoadd = thiscollections.filter(name=request.POST['collection_name'])[0]
				if collectiontoadd.video_list is None or collectiontoadd.video_list.find(request.POST['video_url']) == -1:
					if collectiontoadd.video_list is None:
						collectiontoadd.video_list = (request.POST['video_url']+"#")
					else:
						collectiontoadd.video_list += (request.POST['video_url']+"#")
					newvideo = Video(user=request.user, collection=collectiontoadd, video_url=request.POST['video_url'], date_time=datetime.datetime.now(), description=request.POST['description'])
					s = newvideo.video_url
					if s.find("youtu.be") != -1:
						if s.rfind('?') == -1:
							id = s[s.rfind('/')+1:]
						else:
							id = s[s.rfind('/')+1:s.rfind('?')]
						newvideo.video_url = "https://youtu.be/"+id
						newvideo.image_url = "http://img.youtube.com/vi/"+id+"/0.jpg"
						newvideo.embed_url = "https://www.youtube.com/embed/"+id
					#elif s.find("vimeo.com") != -1:
						#id = s[s.rfind('/')+1:]
						#newvideo.embed_url = "https://player.vimeo.com/video/"+id
					newvideo.save()
					collectiontoadd.cover_image_url = newvideo.image_url
					collectiontoadd.cover_video_embed_url = newvideo.embed_url
					collectiontoadd.save()
		else:
			form = AddVideoForm()
	return form, thiscollections

def collection(request, username_collectionname):
	context = RequestContext(request)
	thisprofile = UserProfile.objects.all().filter(user=request.user)[0]
	vform, thiscollections = addvideo(request)
	if request.user.is_authenticated():
		str = username_collectionname
		names = urlparse.parse_qs(str)
		uname = names["uname"][0]
		cname = names["cname"][0]
		allcollection = Collection.objects.all()
		thiscollection = None
		displayfollow = True
		for collection in allcollection:
			if collection.user.username == uname and collection.name == cname:
				thiscollection = collection
				break
		if thiscollection.user == request.user:
			displayfollow = False
		if thiscollection.follower_list is not None and thiscollection.follower_list.find(request.user.username) != -1:
			displayfollow = False
		videolist = Video.objects.all().filter(user=thiscollection.user, collection=thiscollection)
		thiscollections = allcollection.filter(user=request.user)
		if request.method == 'POST':
			form = FollowCollectionForm(request.POST)
			if form.is_valid():
				displayfollow = False
				collectiontofollow = thiscollection
				if collectiontofollow.follower_list is None or collectiontofollow.follower_list.find(request.user.username) == -1:#this user not following
					if collectiontofollow.follower_list is None:
						collectiontofollow.follower_list = (request.user.username+"#")
					else:
						collectiontofollow.follower_list += (request.user.username+"#")
					collectiontofollow.save()
					if thisprofile.following_collection_list is None:
						thisprofile.following_collection_list = (collectiontofollow.user.username+"*"+collectiontofollow.name+"#")
					else:
						thisprofile.following_collection_list += (collectiontofollow.user.username+"*"+collectiontofollow.name+"#")
					thisprofile.save()
		else:
			form = FollowCollectionForm()
		return render_to_response('collection.html', {'displayfollow':displayfollow, 'form':form, 'vform':vform, 'thiscollections':thiscollections, 'thiscollection':thiscollection, 'videolist':videolist}, context)
	return HttpResponseRedirect('/')

def feed(request):
	context = RequestContext(request)
	thisprofile = UserProfile.objects.all().filter(user=request.user)[0]
	vform, thiscollections = addvideo(request)
	if request.user.is_authenticated():
		allcollection = Collection.objects.all()
		followingcollections = []
		allvideos = Video.objects.all()
		followingvideos = []
		thiscollections = allcollection.filter(user=request.user)
		for collection in allcollection:
			if collection.follower_list and collection.follower_list.find(request.user.username) != -1:
				followingcollections.append(collection)
		for video in allvideos:
			for collection in followingcollections:
				if video.collection == collection:
					followingvideos.append(video)
		followingvideos.reverse()
		
		return render_to_response('feed.html', {'vform':vform, 'followingcollections':followingcollections, 'followingvideos':followingvideos, 'thisprofile':thisprofile, 'thiscollections':thiscollections}, context)
	return HttpResponseRedirect('/')
	
def profile(request, username):
	context = RequestContext(request)
	thisprofile = UserProfile.objects.all().filter(user=request.user)[0]
	vform, thiscollections = addvideo(request)
	if request.user.is_authenticated():
		thatprofile = None
		for profile in UserProfile.objects.all():
			if profile.user.username == username:
				thatprofile = profile
				break
		thatcollections = Collection.objects.all().filter(user=thatprofile.user)
		thiscollections = Collection.objects.all().filter(user=request.user)
		followingcollections = []
		for collection in Collection.objects.all():
			if collection.follower_list and collection.follower_list.find(username) != -1:
				followingcollections.append(collection)
		return render_to_response('profile.html', {'vform':vform, 'thisprofile':thisprofile, 'thatprofile':thatprofile, 'thiscollections':thiscollections, 'thatcollections':thatcollections, 'followingcollections':followingcollections}, context)
	return HttpResponseRedirect('/')