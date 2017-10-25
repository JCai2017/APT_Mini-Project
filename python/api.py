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
            tag_result = Tag.query(searchName == Tag.name)

            lst = name_result.fetch(5)
            result_list = []
            image_list = []
            titles = []
            keys = []

            for streams in lst:
                #Replace with proper method of getting the stream key
                result_list.append('/view_one?streamKey=')
                if streams.coverImage:
                    image_list.append(streams.coverImage)
                else:
                    image_list.append('None')
                titles.append(streams.name)
                keys.append(streams.key)

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
                        #Replace with proper method of getting the stream key
                        result_list.append('/view_one?streamKey=')
                        if key_of_stream.get().coverImage:
                            image_list.append(key_of_stream.get().coverImage)
                        else:
                            image_list.append('None')
                        titles.append(key_of_stream.get().names)
                        i = i + 1

            response['resultUrls'] = result_list
            response['resultImages'] = image_list
            response['titles'] = titles

        logging.log(20, response)
        r = json.dumps(response)
        self.response.write(r)