#!/usr/bin/env python

# [START imports]
import os

from google.appengine.api import users
from google.appengine.api import mail
from google.appengine.ext import ndb

import jinja2
import webapp2
import logging
import re
import json

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
    numImages = ndb.IntegerProperty()
    views = ndb.IntegerProperty()


class User(ndb.Model):
    identity = ndb.StringProperty(indexed=True)
    name = ndb.StringProperty(indexed=False)
    created = ndb.LocalStructuredProperty(Stream, repeated=True)
    subscribed = ndb.LocalStructuredProperty(Stream, repeated=True)


class Tag(ndb.Model):
    name = ndb.StringProperty()
    stream = ndb.KeyProperty(kind=Stream)

class ListofIndex(ndb.Model):
	name = ndb.StringProperty()
	time = ndb.DateTimeProperty(auto_now_add=True)

class Search(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('Search.html')
        self.response.write(template.render())

    def post(self):
        user = users.get_current_user()
        streamset = set()
        searchtarget = self.request.get('target')
        # targetTagList = self.request.get('target').split(', ')
        if len(searchtarget) > 0:
            name_result = Stream.query(searchtarget == Stream.name).order(\
                                                                -Stream.time)
            tag_result = Tag.query(searchtarget == Tag.name)

            # we only want top 5 latest
            result_list = name_result.fetch(5)

            for names in name_result:
                streamKey = names.key
                # create a set of streams which match the result
                if streamKey not in streamset:
                    streamset.add(streamKey)
                else:
                    pass

            # break when got 5 streams
            i = 0
            for tags in tag_result:
                key_of_stream = tags.stream
                if i == 5:
                    break
                else:
                    if key_of_stream in streamset:
                        pass
                    else:
                        streamset.add(key_of_stream)
                        result_list.append(key_of_stream.get())
                        i = i + 1

            template_values = {
                'user': user,
                'Results': result_list,
            }
            template = JINJA_ENVIRONMENT.get_template('Search.html')
            self.response.write(template.render(template_values))
        else:
            template = JINJA_ENVIRONMENT.get_template('Search.html')
            self.response.write(template.render())

class SearchList(webapp2.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'application/json'
		term = self.request.get('term')
		result = dict()
		if len(term) > 0:
			candidate = ListofIndex.query().order(-ListofIndex.time).fetch()
			for index in candidate:
				if term.lower() in index.index.lower():
					if len(result) >= 20:
						pass
					else:
						result[index.index] = index.index
				else:
					pass
			self.response.write(json.dumps(result))
		else:
			self.response.write(json.dumps(result))
