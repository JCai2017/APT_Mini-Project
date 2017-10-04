#!/usr/bin/env python

# [START imports]
import os

from google.appengine.api import users
from google.appengine.api import mail
from google.appengine.ext import ndb

import datetime
import jinja2
import webapp2
import logging
import collections
import time
import re

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
	time = ndb.DateProperty(auto_now_add=True)

class User(ndb.Model):
	identity = ndb.StringProperty(indexed=True)
	name = ndb.StringProperty(indexed=False)
	created = ndb.LocalStructuredProperty(Stream, repeated=True)
	subscribed = ndb.LocalStructuredProperty(Stream, repeated=True)

class Tag(ndb.Model):
	name = ndb.StringProperty()
	stream = ndb.KeyProperty(kind=Stream)

class PopularStreams(ndb.Model):
	stream = ndb.KeyProperty(kind='Stream')
	numberofviews = ndb.IntegerProperty()

class View(ndb.Model):
	stream = ndb.KeyProperty(kind=Stream)
	time = ndb.DateTimeProperty(auto_now_add=True)

class ListofIndex(ndb.Model):
	index = ndb.StringProperty()
	time = ndb.DateTimeProperty(auto_now_add=True)

# Send trending report to 'mail' every 'duration'
class EmailUpdateList(ndb.Model):
	mail = ndb.StringProperty()
	duration = ndb.IntegerProperty()

class Trending(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		Popular_stream_list = PopularStreams.query().order(-PopularStreams.numberofviews).fetch()
		allStr = Stream.query().fetch()
		stream_list = list()
		view_list = list()
		for item in Popular_stream_list:
			if item.stream.get() in allStr:
				stream_list.append(item.stream)
				view_list.append(item.numberofviews)

		FinalResult = zip(stream_list, view_list)

		updateRateMessage = "Unavailable"

		template_values = {
			'user': user,
			'Streams': FinalResult,
			'updateRateMessage': updateRateMessage,
		}
		template = JINJA_ENVIRONMENT.get_template('Trending.html')
		self.response.write(template.render(template_values))
	def post(self):
		user = users.get_current_user()
		if user:
			Popular_stream_list = PopularStreams.query().order(-PopularStreams.numberofviews).fetch()
			stream_list = list()
			view_list = list()
			for item in Popular_stream_list:
				stream_list.append(item.stream)
				view_list.append(item.numberofviews)
			FinalResult = zip(stream_list, view_list)


			lst = EmailUpdateList.query(EmailUpdateList.mail == user.email()).fetch()
			if len(lst) == 0:
				trendRate = self.request.get('trendRate')
				if trendRate == 'Every 5 minutes':
					updateRateMessage = "You will receive trending report every 5 minutes"
					emailUpdateList = EmailUpdateList()
					emailUpdateList.mail = user.email()
					emailUpdateList.duration = 5
					emailUpdateList.put()
				elif trendRate == 'Every 1 hour':
					updateRateMessage = "You will receive trending report every 1 hour"
					emailUpdateList = EmailUpdateList()
					emailUpdateList.mail = user.email()
					emailUpdateList.duration = 60
					emailUpdateList.put()
				elif trendRate == 'Every day':
					updateRateMessage = "You will receive trending report every day"
					emailUpdateList = EmailUpdateList()
					emailUpdateList.mail = user.email()
					emailUpdateList.duration = 1440
					emailUpdateList.put()
				elif trendRate == 'No report':
					updateRateMessage = "You have never registered trending report before"
			elif len(lst)==1:
				emailUpdateList = lst[0]
				trendRate = self.request.get('trendRate')
				if trendRate == 'Every 5 minutes':
					updateRateMessage = "You will receive trending report every 5 minutes"
					emailUpdateList.duration = 5
					emailUpdateList.put()
				elif trendRate == 'Every 1 hour':
					updateRateMessage = "You will receive trending report every 1 hour"
					emailUpdateList.duration = 60
					emailUpdateList.put()
				elif trendRate == 'Every day':
					updateRateMessage = "You will receive trending report every day"
					emailUpdateList.duration = 1440
					emailUpdateList.put()
				elif trendRate == 'No report':
					updateRateMessage = "You canceled receiving trending report"
					emailUpdateList.key.delete()
			else:
				# Error protection: delete all, then recreate.
				for emailUpdateList in lst:
					emailUpdateList.key.delete()

				trendRate = self.request.get('trendRate')
				if trendRate == 'Every 5 minutes':
					updateRateMessage = "You will receive trending report every 5 minutes"
					emailUpdateList = EmailUpdateList()
					emailUpdateList.mail = user.email()
					emailUpdateList.duration = 5
					emailUpdateList.put()
				elif trendRate == 'Every 1 hour':
					updateRateMessage = "You will receive trending report every 1 hour"
					emailUpdateList = EmailUpdateList()
					emailUpdateList.mail = user.email()
					emailUpdateList.duration = 60
					emailUpdateList.put()
				elif trendRate == 'Every day':
					updateRateMessage = "You will receive trending report every day"
					emailUpdateList = EmailUpdateList()
					emailUpdateList.mail = user.email()
					emailUpdateList.duration = 1440
					emailUpdateList.put()
				elif trendRate == 'No report':
					updateRateMessage = "You canceled receiving trending report"


			template_values = {
				'user': user,
				'Streams': FinalResult,
				'updateRateMessage': updateRateMessage,
			}
			template = JINJA_ENVIRONMENT.get_template('Trending.html')
			self.response.write(template.render(template_values))

class CronTask(webapp2.RequestHandler):
	def get(self):
		LastResult = PopularStreams.query().fetch()

		for items in LastResult:
			items.key.delete()

		hour_ago = datetime.datetime.today() - datetime.timedelta(hours=1)

		ViewsWeCare = View.query(View.time >= hour_ago).fetch()

		list_of_streams=list()
		trendingStreams=list()
		viewNumber=list()

		for view in ViewsWeCare:
			if hour_ago <= view.time:
				list_of_streams.append(view.stream)
			else:
				pass

		TrendingStreams_Temp = collections.Counter(list_of_streams).most_common(5)

		for tupleElem in TrendingStreams_Temp:
			FinalResult = PopularStreams()
			FinalResult.stream = tupleElem[0]
			FinalResult.numberofviews = tupleElem[1]
			FinalResult.put()

class UpdateListAuto(webapp2.RequestHandler):
	def get(self):
		LastResult = ListofIndex.query().fetch()

		for index in LastResult:
			index.key.delete()

		namelist = Stream.query().fetch()
		taglist = Tag.query().fetch()

		for stream in namelist:
			Result = ListofIndex()
			Result.index = stream.name
			Result.put()

		tagset=set()
		for tag in taglist:
			if tag.name not in tagset:
				tagset.add(tag.name)
				Result = ListofIndex()
				Result.index = tag.name
				Result.put()
			else:
				pass

class Update5(webapp2.RequestHandler):
	def get(self):
		mail_list = EmailUpdateList.query( EmailUpdateList.duration == 5 ).fetch()
		for user in mail_list:
			if len(user.mail) > 1:
				mail.send_mail(sender = "kaichih1013@gmail.com",
								to = user.mail,
								subject = "Update Trending",
								body = " The New Trending is now Live! ")

class UpdateHour(webapp2.RequestHandler):
	def get(self):
		mail_list = EmailUpdateList.query( EmailUpdateList.duration == 60 ).fetch()
		for user in mail_list:
			if len(user.mail) > 1:
				mail.send_mail(sender = "kaichih1013@gmail.com",
								to = user.mail,
								subject = "Update Trending",
								body = """ The New Trending is now Live! """)

class UpdateDay(webapp2.RequestHandler):
	def get(self):
		mail_list = EmailUpdateList.query( EmailUpdateList.duration == 1440 ).fetch()
		for user in mail_list:
			if len(user.mail) > 1:
				mail.send_mail(sender = "kaichih1013@gmail.com",
								to = user.mail,
								subject = "Update Trending",
								body = """ The New Trending is now Live! """)

