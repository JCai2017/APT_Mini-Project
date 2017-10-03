class UpLoad(webapp2.RequestHandler):
	def get(self):
		stName = self.request.get('stream')
		stream = Stream.query(Stream.name == stName).get()
		user = users.get_current_user()
		nickname = user.nickname()
		template_values = {
			'stream' : stName,
			'user' : nickname
		}
		template = JINJA_ENVIRONMENT.get_template('upload.html')
        self.response.write(template.render(template_values))
    def post(self):
    	stName = self.request.get('stream')
    	stream = Stream.query(Stream.name == stName).get()
    	images  = self.request.get('img')
    	for i in images:
    		stream.images.append(i)
    	stream.put()
    	self.redirect() # should go to view the stream


class ViewAllStream(webapp2.RequestHandler):
	def get(self):
		allStr = Stream.all()
		template_values = dict()
		for s in allStr:
			template_values[s.name] = s.coverImage
		template = JINJA_ENVIRONMENT.get_template('viewAllStream.html')
		self.response.write(template.render(template_value))


class ViewOneStream(webapp2.RequestHandler):
	def get(self):
		stName = self.request.get('stream')
		stream = Stream.query(Stream.name == stName).get()
		url = stream.url
		cover = stream.coverImage
		tags = stream.tags
		lastUpdate = stream.lastUpdate
		views = stream.views
		images = stream.images
		template = JINJA_ENVIRONMENT.get_template('viewOneStream.html')
		self.response.write(template.render(name = stName, cover = cover, url = url, 
			tags = tags, lastUpdate = lastUpdate, views = views, images = images))