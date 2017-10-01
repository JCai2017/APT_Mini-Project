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
		

class ViewOneStream(webapp2.RequestHandler):
	def get(self):
		