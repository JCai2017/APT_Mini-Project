#!/usr/bin/env python

# [START imports]
import os

from random import uniform
from google.appengine.api import users
from google.appengine.api import mail
from google.appengine.ext import ndb
from google.appengine.api import images
from google.net.proto.ProtocolBuffer import ProtocolBufferDecodeError

import jinja2
import webapp2
import logging
import re
import json
import datetime

DEFAULT_NAME = 'default_connex'

JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
	extensions=['jinja2.ext.autoescape'],
	autoescape=True)
# [END imports]


class Stream(ndb.Model):
	name = ndb.StringProperty(indexed=True)
	ownerEmail = ndb.StringProperty()
	url = ndb.StringProperty()
	coverImage = ndb.StringProperty()
	lastUpdate = ndb.DateProperty(auto_now=True)
	time = ndb.DateProperty(auto_now_add=True)
	numImages = ndb.IntegerProperty()
	views = ndb.IntegerProperty()

class Tag(ndb.Model):
	name = ndb.StringProperty()
	stream = ndb.KeyProperty(kind=Stream)

class Image(ndb.Model):
	time = ndb.DateTimeProperty(auto_now_add=True)
	stream = ndb.KeyProperty(kind=Stream)
	full_size_image = ndb.BlobProperty()
	Thumbnail = ndb.BlobProperty()
	geoPt = ndb.GeoPtProperty()


class View(ndb.Model):
	stream = ndb.KeyProperty(kind=Stream)
	time = ndb.DateTimeProperty(auto_now_add=True)


class UpLoad(webapp2.RequestHandler):
	def post(self):
		imgLocation = self.request.get('imgLocation')
		img = Image()

		if imgLocation != "":
			img.geoPt = ndb.GeoPt(imgLocation)
		else:
			pass

		streamKey = ndb.Key(urlsafe=self.request.get('streamKey'))
		img.stream = streamKey
		img_temp = self.request.get('img')
		img.Thumbnail = images.resize(img_temp, width=280, height=280,
									  crop_to_fit=True)
		img.full_size_image = img.Thumbnail
		img.geoPt = ndb.GeoPt(uniform(-90, 90), uniform(-180, 180))
		img.put()

		stream = streamKey.get()
		stream.lastUpdate = img.time
		stream.put()

		self.redirect('/view_one?streamKey='+streamKey.urlsafe())


class ViewAllStream(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		allStr = Stream.query().order(-Stream.time)
		template_value = {
			'user': user,
			'Streams': allStr,
		}
		template = JINJA_ENVIRONMENT.get_template('viewAllStream.html')
		self.response.write(template.render(template_value))


class ViewOneStream(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()

		try:
			streamKey = ndb.Key(urlsafe=self.request.get('streamKey'))
			stream = streamKey.get()

			imgList = Image.query(Image.stream == streamKey).order(-Image.time
																   ).fetch(3)
			ownerCheck = 'notOwner'
			if stream.ownerEmail == user.email():
				ownerCheck = 'isOwner'

			template = JINJA_ENVIRONMENT.get_template('viewOneStream.html')
			self.response.write(template.render(streamKey=streamKey,
												images=imgList,
												ownerCheck=ownerCheck,
												user=user))

			view = View()
			view.stream = streamKey
			view.put()
		except TypeError:
			self.redirect('error?errorType=2')
		except ProtocolBufferDecodeError:
			self.redirect('error?errorType=3')

	def post(self):
		user = users.get_current_user()
		streamKey = ndb.Key(urlsafe=self.request.get('streamKey'))
		stream = streamKey.get()

		imgList = Image.query(Image.stream == streamKey).order(-Image.time)\
			.fetch()
		ownerCheck = 'notOwner'
		if stream.ownerEmail == user.email():
			ownerCheck = 'isOwner'

		template = JINJA_ENVIRONMENT.get_template('viewOneStream.html')
		self.response.write(template.render(streamKey=streamKey,
											images=imgList,
											ownerCheck=ownerCheck,
											user=user))

		view = View()
		view.stream = streamKey
		view.put()


class ImageHandler(webapp2.RequestHandler):
	def get(self):
		ImageKey = ndb.Key(urlsafe=self.request.get('img_id'))
		img = ImageKey.get()
		markerImage = images.resize(img.full_size_image, width=300, height=300,
									crop_to_fit=True)
		self.response.headers['Content-Type'] = 'image/png'
		self.response.out.write(markerImage)

class MarkerImageHandler(webapp2.RequestHandler):
	def get(self):
		ImageKey = ndb.Key(urlsafe=self.request.get('img_id'))
		img = ImageKey.get()
		markerImage = images.resize(img.full_size_image, width=100, height=100, crop_to_fit=True)
		self.response.headers['Content-Type'] = 'image/png'
		self.response.out.write(markerImage)

class GeoView(webapp2.RequestHandler):
	def get(self):
		streamKey = ndb.Key(urlsafe=self.request.get('streamKey'))
		user = users.get_current_user()
		
		template_values = {
			'user': user,
			'streamKey': streamKey,
		}
		template = JINJA_ENVIRONMENT.get_template('geoView.html')
		self.response.write(template.render(template_values))


class Geo_Data(webapp2.RequestHandler):
	def get(self):
		streamKey = ndb.Key(urlsafe=self.request.get('streamKey'))
		query_begin_date = self.request.get('start')
		query_end_date = self.request.get('end')
		query_begin_date_obj = datetime.datetime.strptime(query_begin_date, "%Y-%m-%dT%H:%M:%S.%fZ")
		query_end_date_obj = datetime.datetime.strptime(query_end_date, "%Y-%m-%dT%H:%M:%S.%fZ")

		finalList = []
		imgList = Image.query(Image.stream == streamKey).order(-Image.time).fetch()
		for img in imgList:
			if query_begin_date_obj <= img.time <= query_end_date_obj:
				finalList.append(img)


		self.response.headers['Content-Type'] = 'application/json'
		markers = []
		for img in finalList:
			if img.geoPt is not None:
				content = '<img src="/markerImg?img_id=' + img.key.urlsafe() + '" alt="image">'
				markers.append({'latitude': img.geoPt.lat, 'longitude': img.geoPt.lon, 'content': content})

		data = {
			'markers': markers,
		}
		self.response.out.write(json.dumps(data))


class Add_Image_mobile(webapp2.RequestHandler):
	def post(self):
		# TODO: make photoCaption meaningful
		streamKey = ndb.Key(urlsafe=self.request.get('streamKey'))
		img = Image()
		img.stream = streamKey
		img_temp = self.request.get('file')
		img.Thumbnail = images.resize(img_temp ,width=300, height=300, crop_to_fit = True)
		img.full_size_image = img_temp
		imgLocation = self.request.get('imgLocation')
		img.geoPt = ndb.GeoPt(imgLocation)
		img.put()
		tags = self.request.get('photoCaption')
		if tags != "":
			tagsList = tags.split(', ')
			for item in tagsList:
				tag = Tag()
				tag.name = item
				tag.stream = streamKey
				tag.put()

		stream = streamKey.get()
		stream.lastTimeUpload = img.time
		stream.put()
