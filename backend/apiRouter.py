import sys
import os
import blockchainInterface as interface
import tornado.ioloop
import tornado.web
import tornado.httpserver
frontendPath = sys.argv[1] + "/frontend"

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

class homeHandler(tornado.web.RequestHandler):
  # This routing table directs off to the services to support the UI.
  # Route to the appropriate function, passing in parameters as required.

  def get(self):  
    function = self.get_argument("function", default="404")
    
    if function == "getUiDefaults":
      uiDefaults = getConfig["uiDefaults"]
      self.write(uiDefaults)
    
    elif function == "getLableRange":
      coin = self.get_argument("coin")
      rangeStart = int(self.get_argument("start"))
      rangeEnd = int(self.get_argument("end"))
      labels = interface.getLabelRange(start, end, coin)
      self.write(labels)
    
    elif function == "searchLabels":
      coin = self.get_argument("coin")
      searchTerm = self.get_argument("searchTerm")
      labels = interface.searchLabels(searchTerm, coin)
      self.write(labels)


application = tornado.web.Application([
  (r"/api/", homeHandler),
  (r"/", HTMLHandler),
  (r"/js.js", JSHandler),
  (r"/css.css", CSSHandler),
  (r'/webfavicon.ico()', tornado.web.StaticFileHandler, {'path': BEE_PATH + '/favicon.ico'}),
  (r"/ShareTech.ttf()", tornado.web.StaticFileHandler, {'path': BEE_PATH + '/ShareTech.ttf'}),
])


if __name__ == "__main__":
	http_server.listen(80)
	tornado.ioloop.IOLoop.instance().start()

