#!/usr/bin/env python

# [START imports]
import os
import json

from urlparse import urlparse, parse_qs
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
    time = ndb.DateTimeProperty(auto_now_add=True)


class Image(ndb.Model):
    time = ndb.DateTimeProperty(auto_now_add=True)
    stream = ndb.KeyProperty(kind=Stream)
    full_size_image = ndb.BlobProperty()
    Thumbnail = ndb.BlobProperty()
    geoPt = ndb.GeoPtProperty()

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

class API(webapp2.RequestHandler):
    def get(self):
        response = {'resultUrls': [], 'resultImages': [], 'titles': []}
        queries = self.request.get('target')
        if queries:
            logging.log(20, "I'M IN!!!!!!!!")
            streamSet = set()
            searchName = self.request.get('target')
            name_result = Stream.query(searchName == Stream.name).order(\
                                                             -Stream.time)
            tag_result = Tag.query('#'+searchName == Tag.name)

            lst = name_result.fetch(5)
            result_list = []
            image_list = []
            titles = []
            #keys = []

            for streams in lst:
                result_list.append(streams.key.urlsafe())
                if streams.coverImage:
                    image_list.append(streams.coverImage)
                else:
                    image_list.append('None')
                titles.append(streams.name)
                #keys.append(streams.key)

            for names in name_result:
                streamKey = names.key
                if streamKey not in streamSet:
                    streamSet.add(streamKey)
                else:
                    pass

            i = 0
            for tags in tag_result:
                key_of_stream = tags.stream
                if i == 5:
                    break
                else:
                    if key_of_stream in streamSet:
                        pass
                    else:
                        streamSet.add(key_of_stream)
                        result_list.append(key_of_stream.urlsafe())
                        if key_of_stream.get().coverImage:
                            image_list.append(key_of_stream.get().coverImage)
                        else:
                            image_list.append('None')
                        titles.append(key_of_stream.get().name)
                        i = i + 1

            response['resultUrls'] = result_list
            response['resultImages'] = image_list
            response['titles'] = titles

        logging.log(20, response)
        r = json.dumps(response)
        self.response.write(r)

class StreamAPI(webapp2.RequestHandler):
    def get(self):
        response = {'coverImage':[], 'images': [], 'names': [], 'owner': '', 'key': ''}
        queries = self.request.get('target')
        querySub = self.request.get('subscriber')
        queryLocation = self.request.get('location')
        queryLat = self.request.get('lat')
        names = []
        img = []
        coverImage = []
        owner = ''
        key = ''
        if queries:
            logging.log(20, "I'M IN!!!!!!!!")
            if queries == "all":
                s = Stream.query().order(-Stream.time)
                results = s.fetch(16)
                for i in results:
                    names.append(i.name)
                    if i.coverImage:
                        coverImage.append(i.coverImage)
                    else:
                        coverImage.append("None")
            else:
                sName = queries
                result = Stream.query(Stream.name == sName).fetch(1)
                owner = result[0].ownerEmail
                key = result[0].key.urlsafe()
                for r in result:
                    names.append(r.name)
                    if r.coverImage:
                        coverImage.append(r.coverImage)
                    else:
                        coverImage.append("None")
                    imgs = Image.query(Image.stream == r.key).fetch()
                    for i in imgs:
                        img.append('/img?img_id=' + i.key.urlsafe())

        if querySub:
            logging.log(20, "I'M IN!!!!!!!!")
            s = Subscriber.query(Subscriber.email == querySub).fetch()
            for i in s:
                st = i.stream
                names.append(st.get().name)
                if st.get().coverImage:
                    coverImage.append(st.get().coverImage)
                else:
                    coverImage.append("None")

        if queryLocation:
            logging.log(20, "I'M IN!!!!!!!!")
            a = queryLocation
            b = queryLat
            a = float(a)
            b = float(b)
            all_image = Image.query().fetch()
            for i in all_image:
                x, y = i.geoPt.lon, i.geoPt.lat
                if x - a < 10 and a - x > -10 and y - b < 10 and b - y > -10:
                    img.append('/img?img_id=' + i.key.urlsafe())

        response['coverImage'] = coverImage
        response['images'] = img
        response['names'] = names
        response['owner'] = owner
        response['key'] = key

        logging.log(20, response)
        #if querySub or queries:
            #r = json.dumps(response, ensure_ascii=False).encode('utf8')
        #else:
        r = json.dumps(response)
        self.response.write(r)

