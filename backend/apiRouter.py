import sys
import os
import blockchainInterface as interface
import tornado.ioloop
import tornado.web
import tornado.httpserver
import json
frontendPath = sys.argv[1] + "/frontend"
path = sys.argv[1]

def getConfig():
  import json
  return json.loads(open("config.json").read())
  
  
class HTMLHandler(tornado.web.RequestHandler):
  def get(self):
    fileContents = open(frontendPath + "/index.html").read()
    self.write(fileContents)

class JSHandler(tornado.web.RequestHandler):
  def get(self):
    fileContents = open(frontendPath + "/js.js").read()
    self.write(fileContents)

class CSSHandler(tornado.web.RequestHandler):
  def get(self):
    self.set_header('Content-Type', 'text/css')
    fileContents = open(frontendPath + "/css.css").read()
    self.write(fileContents)

class redirect (tornado.web.RequestHandler):
  def get(self):  
    self.redirect("https://" +  self.request.host + self.request.uri)
    
class homeHandler(tornado.web.RequestHandler):
  # This routing table directs off to the services to support the UI.
  # Route to the appropriate function, passing in parameters as required.
  
 def get(self):  
    function = self.get_argument("function")
    
    if function == "getUiDefaults":
      uiDefaults = getConfig()["uiDefaults"]
      self.write(json.dumps(uiDefaults))
    
    elif function == "searchLabels":
      startPos = int(self.get_argument("startPos"))
      endPos = int(self.get_argument("endPos"))
      startDate = self.get_argument("startDate")
      endDate = self.get_argument("endDate")
      searchTerm = self.get_argument("searchTerm")
      coin = self.get_argument("coin")
      labels = interface.searchLabels(startPos, endPos, startDate, endDate, searchTerm, coin)
      self.write(json.dumps(labels))

redirectApplication = tornado.web.Application([
        (r'/', redirect)
    ])
application = tornado.web.Application([
  (r"/api/", homeHandler),
  (r"/*", HTMLHandler),
  (r"/js.js", JSHandler),
  (r"/css.css", CSSHandler),
  (r'/webfavicon.ico()', tornado.web.StaticFileHandler, {'path': frontendPath + '/favicon.ico'}),
  (r'/magnifyingGlass.png()', tornado.web.StaticFileHandler, {'path': frontendPath + '/magnifyingGlass.png'}),
  (r"/shareTech.ttf()", tornado.web.StaticFileHandler, {'path': frontendPath + '/shareTech.ttf'}),
  (r"/hairline.ttf()", tornado.web.StaticFileHandler, {'path': frontendPath + '/hairline.ttf'}),
], ssl_options={
    "certfile": os.path.join(path + "/backend/ssl/certificate.crt"),
    "keyfile": os.path.join(path + "/backend/ssl/private.key"),
})

http_server = tornado.httpserver.HTTPServer(application, ssl_options={
    "certfile": os.path.join(path + "/backend/ssl/certificate.crt"),
    "keyfile": os.path.join(path + "/backend/ssl/private.key"),
})


if __name__ == "__main__":
  redirectApplication.listen(80)
  http_server.listen(443)
  tornado.ioloop.IOLoop.instance().start()
