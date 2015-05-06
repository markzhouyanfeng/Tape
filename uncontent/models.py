from django.contrib.auth.models import User
from django.db import models
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount

import hashlib


class Collection(models.Model):
	user = models.ForeignKey(User)
	name = models.CharField(max_length=128, blank=True)
	video_list = models.TextField(null=True, blank=True) #"video.video_url#"
	follower_list = models.TextField(null=True, blank=True) #"user.username#"
	collection_url = models.CharField(max_length=128, blank=True)
	cover_image_url = models.URLField(blank=True)
	cover_video_embed_url = models.URLField(blank=True)
	
	def __unicode__(self):
		return self.collection_url

class Video(models.Model):
	user = models.ForeignKey(User)
	collection = models.ForeignKey(Collection)
	title = models.CharField(max_length=128, blank=True)
	video_url = models.URLField(blank=True)
	embed_url = models.URLField(blank=True)
	image_url = models.URLField(blank=True)
	date_time = models.DateTimeField()
	description = models.TextField(null=True, blank=True)
	tag_list = models.TextField(null=True, blank=True) #"tag#"
	liked_list = models.TextField(null=True, blank=True) #"user.username#"
	comment_list = models.TextField(null=True, blank=True) #"user1.username*user2.username*collection.name*video.title#"
	#source
	embedable = models.BooleanField()
	report = models.BooleanField()
	
	def __unicode__(self):
		return self.video_url
	
class Comment(models.Model):
	user = models.ForeignKey(User)
	video = models.TextField(null=True, blank=True) #"user.username*collection.name*video.title"
	comment = models.TextField(null=True, blank=True)
	date_time = models.DateTimeField()
	report = models.BooleanField()


class UserProfile(models.Model):
	user = models.OneToOneField(User, related_name='profile')
	about_me = models.TextField(null=True, blank=True)
	collection_list = models.TextField(null=True, blank=True) #"collection.name#"
	following_collection_list = models.TextField(null=True, blank=True) #"user.username*collection.name#"
	friend_list = models.TextField(null=True, blank=True) #"Uid#"
	interest_list = models.TextField(null=True, blank=True) #"tag#"
	liked_video_list = models.TextField(null=True, blank=True) #"user.username*collection.name*video.title#"

	def __unicode__(self):
		return "{0}'s profile".format(self.user.username)

	class Meta:
		db_table = 'user_profile'

	def profile_image_url(self):
		"""
		Return the URL for the user's Facebook icon if the user is logged in via Facebook,
		otherwise return the user's Gravatar URL
		"""
		fb_uid = SocialAccount.objects.filter(user_id=self.user.id, provider='facebook')

		if len(fb_uid):
			return "http://graph.facebook.com/{0}/picture?width=40&height=40".format(fb_uid[0].uid)

		return "http://www.gravatar.com/avatar/{0}?s=40".format(
			hashlib.md5(self.user.email).hexdigest())
	

	def account_verified(self):
		"""
		If the user is logged in and has verified hisser email address, return True,
		otherwise return False
		"""
		result = EmailAddress.objects.filter(email=self.user.email)
		if len(result):
			return result[0].verified
		return False


User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])





	
	
	
	
	

