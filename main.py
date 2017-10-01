#!/usr/bin/env python

#[START imports]
import os

from google.appengine.api import users
from google.appengine.ext import ndb

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


def connex_key():
    return ndb.Key('Connex', DEFAULT_NAME)


class Stream(ndb.Model):
    name = ndb.StringProperty(indexed=True)
    url = ndb.StringProperty()
    coverImage = ndb.StringProperty()
    tags = ndb.StringProperty(repeated=True)
    lastUpdate = ndb.DateProperty(auto_now=True)
    numImages = ndb.IntegerProperty()
    views = ndb.IntegerProperty()
    # add image property
    images = ndb.BlobProperty(repeated=True)

class AllStreams(ndb.Model):
    streams = ndb.KeyProperty(repeated=True)
    names = ndb.StringProperty(repeated=True)


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
        create_url = '/create-stream'
        templatePg = 'login.html'
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
            if userData:
                createdStreams = userData.created
                subscribedStreams = userData.subscribed

        else:
            url = users.create_login_url(self.request.uri)

        template_values = {
                'user': nickname,
                'url': url,
                'cStreams': createdStreams,
                'sStreams': subscribedStreams
        }
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

        for entry in checkedC:
            i = 0
            for st in userData.created:
                if st.name == entry:
                    break
                i = i + 1

            del userData.created[i]
            key = allStr.streams[i]
            del allStr.streams[i]
            key.delete()
            userData.put()
            allStr.put()


        for entry in checkedS:
            del userData.subscribed[entry]
            userData.put()

        template_values = {
                'user': user.nickname(),
                'cStreams': userData.created,
                'sStreams': userData.subscribed
        }
        template = JINJA_ENVIRONMENT.get_template('main.html')
        self.response.write(template.render(template_values))


class CreateStream(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        userId = user.user_id()

        template_values = {
                'user': user.nickname(),
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
        tagList = self.request.get('tags').split(",")

        if userData:
            userData.name = user.nickname()
            stName = self.request.get('name')
            for st in allStr.names:
                logging.log(20, st)
                if st == stName:
                    logging.log(20, "Nope")
                    template_values = {
                            'user': user.nickname(),
                            'id': userId,
                            'msg': 'Stream name is already in use'
                    }
 
                    template = JINJA_ENVIRONMENT.get_template('create.html')
                    self.response.write(template.render(template_values))
                    #self.redirect('/create-stream')
                    return

            link = self.request.get('name')
            link = re.sub(r"[^\w\s]", '', link)
            link = re.sub(r"\s", '-', link)
            stream = Stream(name=self.request.get('name'),
                            url=link,
                            coverImage=self.request.get('image'),
                            tags=tagList, numImages=0, views=0)
            userData.created.append(stream)
            status = userData.put()
            allStr.streams.append(status)
            allStr.names.append(stName)
            allStr.put()

        else:
            data.identity = userID
            data.name = user.nickname()
            stName = self.request.get('name')
            for st in allStr:
                if st.name == stName:
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
            stream = Stream(name=self.request.get('name'),
                                url=link,
                                coverImage=self.request.get('image'),
                                tags=tagList, numImages=0, views=0)
            data.created.append(stream)
            status = data.put()
            allStr.append(status)
            allStr.put()

        template_values = {
                'user': user.nickname(),
                'cStreams': userData.created,
                'sStreams': userData.subscribed
        }
        template = JINJA_ENVIRONMENT.get_template('main.html')
        self.response.write(template.render(template_values))
        

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/create-stream', CreateStream),
], debug=True)
