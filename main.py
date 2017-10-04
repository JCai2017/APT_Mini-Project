#!/usr/bin/env python

# [START imports]
import os

from google.appengine.api import users
from google.appengine.api import mail
from google.appengine.ext import ndb
from google.appengine.api import images

import jinja2
import webapp2
import logging
import re

from upload import UpLoad
from upload import ViewAllStream
from upload import ViewOneStream
from upload import ImageHandler
from search import Search
from trending import *

DEFAULT_NAME = 'default_connex'

JINJA_ENVIRONMENT = jinja2.Environment(
		loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
		extensions=['jinja2.ext.autoescape'],
		autoescape=True)
# [END imports]


def connex_key():
	return ndb.Key('Connex', DEFAULT_NAME)

class Stream(ndb.Model):
	name = ndb.StringProperty(indexed=True)
	ownerEmail = ndb.StringProperty()
	url = ndb.StringProperty()
	coverImage = ndb.StringProperty()
	lastUpdate = ndb.DateProperty(auto_now=True)
	time = ndb.DateTimeProperty(auto_now_add=True)

class Image(ndb.Model):
	time = ndb.DateTimeProperty(auto_now_add=True)
	stream = ndb.KeyProperty(kind=Stream)
	full_size_image = ndb.BlobProperty()
	Thumbnail = ndb.BlobProperty()

class Tag(ndb.Model):
	name = ndb.StringProperty()
	stream = ndb.KeyProperty(kind=Stream)

class View(ndb.Model):
	stream = ndb.KeyProperty(kind=Stream)
	time = ndb.DateTimeProperty(auto_now_add=True)

class User(ndb.Model):
	identity = ndb.StringProperty(indexed=True)
	name = ndb.StringProperty(indexed=False)
	created = ndb.LocalStructuredProperty(Stream, repeated=True)

class Subscriber(ndb.Model):
	stream = ndb.KeyProperty(kind=Stream)
	email = ndb.StringProperty()

class AllStreams(ndb.Model):
	streams = ndb.KeyProperty(repeated=True)
	names = ndb.StringProperty(repeated=True)

class MainPage(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		createdStreams = []
		subscribedStreams = []
		numView = []
		numImg = []
		numView_sub = []
		numImg_sub = []
		templatePg = 'login.html'
		logging.log(20, user)
		if user:
			nickname = user.nickname()
			userId = user.user_id()
			url = users.create_logout_url(self.request.uri)
			query = User.query(User.identity == userId)
			allStr = AllStreams.query().get()
			if not allStr:
				allStr = AllStreams(parent=connex_key())
				allStr.put()
			userData = query.get()
			templatePg = 'main.html'
			
			# Get number of views and pictures of self-owned streams
			createdStreams = Stream().query(Stream.ownerEmail == user.email())
			for elem in createdStreams:
				viewCount = View.query(View.stream == elem.key).count(limit=None)
				imgCount = Image.query(Image.stream == elem.key).count(limit=None)
				numView.append(viewCount)
				numImg.append(imgCount)
			# Get number of views and picture of subscribed streams
			lst = Subscriber.query(Subscriber.email == user.email())
			for elem in lst:
				subscribedStreams.append(elem.stream)
				viewCount = View.query(View.stream == elem.stream).count(limit=None)
				imgCount = Image.query(Image.stream == elem.stream).count(limit=None)
				numView_sub.append(viewCount)
				numImg_sub.append(imgCount)
			
			my_group_list = zip(createdStreams, numView, numImg)
			sub_group_list = zip(subscribedStreams, numView_sub, numImg_sub)
			template_values = {
					'user': user,
					'url': url,
					'cStreams': my_group_list,
					'sStreams': sub_group_list
			}

		else:
			url = users.create_login_url(self.request.uri)
			logging.log(20, 'No user found')
			template_values = {'url': url}

		#for st in allStr.streams:
			#logging.log(20, st)

		template = JINJA_ENVIRONMENT.get_template(templatePg)
		self.response.write(template.render(template_values))

	def post(self):
		user = users.get_current_user()
		userId = user.user_id()
		query = User.query(User.identity == userId)
		userData = query.get()
		allStr = AllStreams.query().get()
		checkedC = self.request.get_all('cList[]')
		checkedS = self.request.get_all('sList[]')
		logging.log(20, checkedC)
		
		# Delete Streams
		for entry in checkedC:
			i = 0
			for st in userData.created:
				if st.name == entry:
					delstream = Stream.query(Stream.name == st.name).get()
					delstream.key.delete()
					break
				i = i + 1

			del userData.created[i]
			key = allStr.streams[i]
			del allStr.streams[i]
			del allStr.names[i]
			key.delete()
			userData.put()
			allStr.put()

		logging.log(20, checkedS)
		# UnSubscribe Streams
		lst = Subscriber().query(Subscriber.email == user.email()).fetch()
		for sub in lst:
			for entry in checkedS:
				if sub.stream.get().name == entry:
					sub.key.delete()
					break

		createdStreams = []
		subscribedStreams = []
		numView = []
		numImg = []
		numView_sub = []
		numImg_sub = []

		# Get number of views and pictures of self-owned streams
		createdStreams = Stream().query(Stream.ownerEmail == user.email())
		for elem in createdStreams:
			viewCount = View.query(View.stream == elem.key).count(limit=None)
			imgCount = Image.query(Image.stream == elem.key).count(limit=None)
			numView.append(viewCount)
			numImg.append(imgCount)
		# Get number of views and picture of subscribed streams
		lst = Subscriber.query(Subscriber.email == user.email())
		for elem in lst:
			subscribedStreams.append(elem.stream)
			viewCount = View.query(View.stream == elem.stream).count(limit=None)
			imgCount = Image.query(Image.stream == elem.stream).count(limit=None)
			numView_sub.append(viewCount)
			numImg_sub.append(imgCount)

		my_group_list = zip(createdStreams, numView, numImg)
		sub_group_list = zip(subscribedStreams, numView_sub, numImg_sub)

		template_values = {
				'user': user,
				'cStreams': my_group_list,
				'sStreams': sub_group_list
		}
		template = JINJA_ENVIRONMENT.get_template('main.html')
		self.response.write(template.render(template_values))

class CreateStream(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		userId = user.user_id()

		template_values = {
				'user': user,
				'id': userId,
				'msg': ''
		}

		template = JINJA_ENVIRONMENT.get_template('create.html')
		self.response.write(template.render(template_values))

	def post(self):
		user = users.get_current_user()
		userId = user.user_id()
		query = User.query(User.identity == userId)
		userData = query.get()
		data = User(parent=connex_key())
		allStr = AllStreams.query().get()
		status = 0
		link = ''
		tagsString = self.request.get('tags')
		email = user.email()

		if userData:
			userData.name = user.nickname()
			stName = self.request.get('name')
			for st in allStr.names:
				logging.log(20, st)
				if st == stName:
					logging.log(20, "Nope")
					template_values = {
							'user': user,
							'id': userId,
							'msg': 'Stream name is already in use'
					}

					template = JINJA_ENVIRONMENT.get_template('create.html')
					self.response.write(template.render(template_values))
					return

			link = self.request.get('name')
			link = re.sub(r"[^\w\s]", '', link)
			link = re.sub(r"\s", '-', link)
			link = '/?' + link
			stream = Stream(name=stName, ownerEmail=email,
							url=link, coverImage=self.request.get('image'))
			stream.put()
			userData.created.append(stream)
			status = userData.put()
			allStr.streams.append(status)
			allStr.names.append(stName)
			allStr.put()
			if tagsString != "":
				tagsList = tagsString.split(', ')
				for item in tagsList:
					tag = Tag()
					tag.name = item
					tag.stream = stream.key
					tag.put()
		else:
			data.identity = userId
			data.name = user.nickname()
			stName = self.request.get('name')
			for st in allStr.names:
				if st == stName:
					template_values = {
							'user': user,
							'id': userId,
							'msg': 'Stream name is already in use'
					}

					template = JINJA_ENVIRONMENT.get_template('create.html')
					self.response.write(template_values)
					self.redirect('/create-stream')

			link = self.request.get('name')
			link = re.sub(r"[^\w\s]", '', link)
			link = re.sub(r"\s", '-', link)
			link = '/?' + link
			stream = Stream(name=stName, ownerEmail=email,
							url=link, coverImage=self.request.get('image'))
			stream.put()
			data.created.append(stream)
			status = data.put()
			allStr.streams.append(status)
			allStr.names.append(stName)
			allStr.put()
			if tagsString != "":
				tagsList = tagsString.split(', ')
				for item in tagsList:
					tag = Tag()
					tag.name = item
					tag.stream = stream.key
					tag.put()

		user = users.get_current_user()
		userId = user.user_id()
		query = User.query(User.identity == userId)
		userData = query.get()
		invMsg = self.request.get('invMsg')
		subscriberString = self.request.get('invites')
		if subscriberString != "":
			invites = subscriberString.split(', ')
			# Send emails
			logging.log(20, invites)
			for invitee in invites:
				if len(invitee) > 1:
					if invitee.isspace():
						continue
					message = mail.EmailMessage(
							sender='jason.cai.plano@gmail.com',
							subject='Your invited to subscribe to a Connex stream')
					message.to = invitee
					if invMsg != "":
						message.body = invMsg + "\nby " + user.email()
					else:
						message.body = "You are invited to my stream! \nby " + user.email()
					message.send()
		
		self.redirect('/')

class Subscribe(webapp2.RequestHandler):
	def post(self):
		user = users.get_current_user()
		streamKey = ndb.Key(urlsafe=self.request.get('streamKey'))
		subscribersList = Subscriber.query(Subscriber.stream == streamKey).fetch()

		isRepeat = False
		for sub in subscribersList:
			if sub.email == user.email():
				isRepeat = True
				break

		if not isRepeat:
			sub = Subscriber()
			sub.stream = streamKey
			sub.email = user.email()
			sub.put()

		imgList = Image.query(Image.stream == streamKey).order(-Image.time).fetch()

		template_values = {
			'user': user,
			'images': imgList,
			'streamKey': streamKey,
		}
		template = JINJA_ENVIRONMENT.get_template('viewOneStream.html')
		self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
	('/', MainPage),
	('/create-stream', CreateStream),
	('/upload', UpLoad),
	('/view-all', ViewAllStream),
	('/view_one', ViewOneStream),
	('/img', ImageHandler),
	('/subscribe', Subscribe),
	('/search', Search),
	('/trending', Trending),
	('/crontask', CronTask),
	('/update5', Update5),
	('/updatehour', UpdateHour),
	('/updateday', UpdateDay),
	('/updatelistauto', UpdateListAuto),
], debug=True)
