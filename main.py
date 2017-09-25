#!/usr/bin/env python

#[START imports]
import os

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

DEFAULT_NAME = 'default_connex'

JINJA_ENVIRONMENT = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
        extensions=['jinja2.ext.autoescape'],
        autoescape=True)
# [END imports]


def connex_key():
    return ndb.Key('Connex', DEFAULT_NAME)


class Stream(ndb.Model):
    name = ndb.StringProperty(indexed=False)
    url = ndb.StringProperty(indexed=True)
    coverImage = ndb.StringProperty(indexed=False)
    tags = ndb.StringProperty(repeated=True)


class User(ndb.Model):
    identity = ndb.StringProperty(indexed=True)
    name = ndb.StringProperty(indexed=False)
    created = ndb.LocalStructuredProperty(Stream, repeated=True)
    subscribed = ndb.LocalStructuredProperty(Stream, repeated=True)


class MainPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        createdStreams = []
        subscribedStreams = []
        create_url = '/create_stream'
        templatePg = 'login.html'
        if user:
            nickname = user.nickname()
            userId = user.user_id()
            url = users.create_logout_url(self.request.uri)
            query = User.query(User.identity == userId)
            userData = query.get()
            templatePg = 'main.html'
            if userData:
                createdStreams = userData.created
                subscribedStreams = userData.subscribed

        else:
            url = users.create_login_url(self.request.uri)

        template_values = {
                'user': user,
                'url': url,
                'create_url': create_url,
                'cStreams': createdStreams,
                'sStreams': subscribedStreams
        }
        template = JINJA_ENVIRONMENT.get_template(templatePg)
        self.response.write(template.render(template_values))


class CreateStream(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        userId = user.user_id()

        template_values = {
                'user': user,
                'id': userId
        }

        template = JINJA_ENVIRONMENT.get_template('create.html')
        self.response.write(template.render(template_values))

    def post(self):
        user = users.get_current_user()
        userId = user.user_id()
        query = User.query(User.identity == userId)
        userData = query.get()
        data = User(parent=connex_key())
        status = 0
        tagList = self.request.get('tags').split(",")

        if userData:
            userData.name = user.nickname()
            userData.created.append(Stream(
                name=self.request.get('name'),
                url=self.request.get('url'),
                coverImage=self.request.get('image'),
                tags=tagList))
            status = userData.put()

        else:
            data.identity = userID
            data.name = user.nickname()
            data.created.append(Stream(name=self.request.get('name'),
                                       url=self.request.get('url'),
                                       coverImage=self.request.get('image'),
                                       tags=tagList))
            status = data.put()
        self.redirect('/')

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/create_stream', CreateStream),
], debug=True)
