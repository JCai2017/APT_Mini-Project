#!/usr/bin/env python

# [START imports]
import os
import datetime as dt

from random import uniform
from datetime import datetime

from google.appengine.api import users
from google.appengine.api import mail
from google.appengine.ext import ndb
from google.appengine.api import images
from google.net.proto.ProtocolBuffer import ProtocolBufferDecodeError

import jinja2
import webapp2
import logging
import re

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


class Image(ndb.Model):
    time = ndb.DateTimeProperty(auto_now_add=True)
    year = ndb.IntegerProperty()
    month = ndb.IntegerProperty()
    day =  ndb.IntegerProperty()
    stream = ndb.KeyProperty(kind=Stream)
    lat = ndb.IntegerProperty()
    lon = ndb.IntegerProperty()
    full_size_image = ndb.BlobProperty()
    Thumbnail = ndb.BlobProperty()


class View(ndb.Model):
    stream = ndb.KeyProperty(kind=Stream)
    time = ndb.DateTimeProperty(auto_now_add=True)


class UpLoad(webapp2.RequestHandler):
    def post(self):
        streamKey = ndb.Key(urlsafe=self.request.get('streamKey'))
        img = Image()
        img.stream = streamKey
        today = datetime.now()
        img.year = today.year
        img.month = today.month - 1
        img.day = today.day
        img.lat = uniform(-90, 90)
        img.lon = uniform(-180, 180)
        img_temp = self.request.get('img')
        img.Thumbnail = images.resize(img_temp, width=280, height=280,
                                      crop_to_fit=True)
        img.full_size_image = img.Thumbnail
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


class GeoView(webapp2.RequestHandler):
    def get(self):
        streamKey = ndb.Key(urlsafe=self.request.get('streamKey'))
        imgList = Image.query(Image.stream == streamKey).order(-Image.time)\
            .fetch()

        for img in imgList:
            tmp = images.Image(img.full_size_image)
            tmp.resize(width=100, height=100)
            img = tmp


        template_values = {
                'imagesList': imgList
        }

        template = JINJA_ENVIRONMENT.get_template('geoView.html')
        self.response.write(template.render(template_values))
        self.redirect('/geo_view?streamKey='+streamKey.urlsafe())
