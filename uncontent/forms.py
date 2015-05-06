from django import forms
from uncontent.models import UserProfile, Collection, Video, Comment
from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialAccount


class AddCollectionForm(forms.Form):#discard
    name = forms.CharField(help_text='collection name')
    class Meta:
        model = Collection
        fields = ('name')
		
class AddVideoForm(forms.Form):
	#newcollection = forms.CharField(required=False, initial='False')
	collection_name = forms.CharField(help_text='collection name')
	video_url = forms.URLField(help_text='video url')
	description = forms.CharField(required=False, help_text='description')
	def clean_collection_name(self):
		data = self.cleaned_data['collection_name']
		if data.find("#")!=-1 or data.find("*")!=-1 or data.find("&")!=-1 or data.find(";")!=-1 or data.find("/")!=-1 or data.find("?")!=-1 or data.find("+")!=-1:
			raise forms.ValidationError("No special characters: #*&\;/?+")
		
	
class FollowCollectionForm(forms.Form):
	username = forms.CharField()
	tofollowname = forms.CharField()
	
	
