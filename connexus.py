import os
import urllib
import urllib2


from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import images
from google.appengine.api import mail
from google.net.proto.ProtocolBuffer import ProtocolBufferDecodeError
from math import radians, cos, sin, asin, sqrt

import jinja2
import webapp2
import json
import datetime

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

from trending import *

class Stream(ndb.Model):
    ownerEmail = ndb.StringProperty()
    name = ndb.StringProperty()
    inviteMsg = ndb.StringProperty(indexed=False)
    coverUrl = ndb.StringProperty(indexed=False)
    time = ndb.DateTimeProperty(auto_now_add=True)
    lastTimeUpload = ndb.DateTimeProperty()

class Image(ndb.Model):
    time = ndb.DateTimeProperty(auto_now_add=True)
    stream = ndb.KeyProperty(kind=Stream)
    full_size_image = ndb.BlobProperty()
    Thumbnail = ndb.BlobProperty()
    geoPt = ndb.GeoPtProperty()

class Subscriber(ndb.Model):
    stream = ndb.KeyProperty(kind=Stream)
    email = ndb.StringProperty()

class View(ndb.Model):
    stream = ndb.KeyProperty(kind=Stream)
    time = ndb.DateTimeProperty(auto_now_add=True)

class Tag(ndb.Model):
    name = ndb.StringProperty()
    stream = ndb.KeyProperty(kind=Stream)


class LandingPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user();
        if user:
            log_url = users.create_logout_url(self.request.uri);
            log_url_linktext = 'Logout';
            template_values = {
                'user': user,
                'log_url': log_url,
                'log_url_linktext': log_url_linktext,
            }
            template = JINJA_ENVIRONMENT.get_template('index.html')
            self.response.write(template.render(template_values))
        else:
            log_url = users.create_login_url(self.request.uri)
            log_url_linktext = 'Login'
            template_values = {
                'user': user,
                'log_url': log_url,
                'log_url_linktext': log_url_linktext,
            }
            template = JINJA_ENVIRONMENT.get_template('index.html')
            self.response.write(template.render(template_values))

class Search(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('Search.html')
        self.response.write(template.render())

    def post(self):
        streamset=set()
        searchtarget = self.request.get('target')
        # targetTagList = self.request.get('target').split(', ')
        if len(searchtarget) > 0:
            name_result = Stream.query(searchtarget == Stream.name).order(-Stream.time)
            tag_result = Tag.query(searchtarget == Tag.name)

            result_list = name_result.fetch(5)

            for names in name_result:
                streamKey = names.key
                if streamKey not in streamset:      #create a set of streams which match the result
                    streamset.add(streamKey)
                else:
                    pass

            i = 0
            for tags in tag_result:
                key_of_stream = tags.stream
                if i == 5:
                    pass
                else:
                    if key_of_stream in streamset:
                        pass
                    else:
                        streamset.add(key_of_stream)
                        result_list.append(key_of_stream.get())
                        i = i+1

            template_values={
                'Results':result_list,
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

class Trending(webapp2.RequestHandler):
    def get(self):
        Popular_stream_list = PopularStreams.query().order(-PopularStreams.numberofviews).fetch()
        stream_list = list()
        view_list = list()
        for item in Popular_stream_list:
            stream_list.append(item.stream)
            view_list.append(item.numberofviews)

        FinalResult = zip(stream_list, view_list)

        updateRateMessage = "Unavailable"

        template_values = {
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
                'Streams': FinalResult,
                'updateRateMessage': updateRateMessage,
            }
            template = JINJA_ENVIRONMENT.get_template('Trending.html')
            self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
    ('/', LandingPage),
    ('/search', Search),
    ('/crontask', CronTask),
    ('/update5',Update5),
    ('/updatehour',UpdateHour),
    ('/updateday', UpdateDay),
    ('/trending', Trending),
    ('/updatelistauto', UpdateListAuto),
    ('/searchlist', SearchList),
], debug=True)
