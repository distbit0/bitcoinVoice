#############################################################################################
#
# Bitcoin Voice - Web API
#
##############################################################################################

import sys
import os
import blockchainInterface as interface
import tornado.ioloop
import tornado.web
import tornado.httpserver
import json
frontendPath = sys.argv[1] + "/frontend"
backendPath = sys.argv[1] + "/backend"

path = sys.argv[1]

def getConfig():
  import json
  return json.loads(open(backendPath + "/config.json").read())

class HTMLHandler(tornado.web.RequestHandler):
  def get(self):
    fileContents = open(frontendPath + "/index.html").read()
    self.write(fileContents)

class publicLabelHTMLHandler(tornado.web.RequestHandler):
  def get(self):
    fileContents = open(frontendPath + "/publiclabel.html").read()
    self.write(fileContents)

class tableSortHandler(tornado.web.RequestHandler):
  def get(self):
    fileContents = open(frontendPath + "/tableSort.js").read()
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

        elif function == "getPublicLabelAggregates":
          rowsCount = getConfig()["uiDefaults"]["rowsCount"]
          chainID = int(self.get_argument("chainID"))
          startPos = rowsCount if self.get_argument("startPos") == "" else int(self.get_argument("startPos", default=rowsCount))
          endPos = 0 if self.get_argument("endPos") == "" else int(self.get_argument("endPos", default=0))
          startDate = self.get_argument("startDate", default=-1)
          endDate = self.get_argument("endDate", default=100000000000)
          searchTerm = self.get_argument("searchTerm", default="")

          labels = interface.getPublicLabelAggregates(chainID, startPos, endPos, startDate, endDate, searchTerm)
          self.write(json.dumps(labels))

        elif function == "getPublicLabelOutputs":
          rowsCount = getConfig()["uiDefaults"]["rowsCount"]
          chainID = int(self.get_argument("chainID"))
          startDate = self.get_argument("startDate", default=-1)
          endDate = self.get_argument("endDate", default=100000000000)
          publicLabel = self.get_argument("publicLabel", default="")
          searchByTxID = self.get_argument("searchTerm", default="")

          labels = interface.getPublicLabelOutputs(chainID, startDate, endDate, publicLabel, searchByTxID)
          self.write(json.dumps(labels))


redirectApplication = tornado.web.Application([
       (r'/', redirect)
    ])


application = tornado.web.Application([
  (r"/publiclabel.*", publicLabelHTMLHandler),
  (r"/index.*", HTMLHandler),
  #(r"/.*", HTMLHandler),
  (r"/", HTMLHandler),
  (r"/api/", homeHandler),
  (r"/js.js", JSHandler),
  (r"/css.css", CSSHandler),
  (r"/tableSort.js", tableSortHandler),
  (r'/webfavicon.ico()', tornado.web.StaticFileHandler, {'path': frontendPath + '/favicon.ico'}),
  (r'/magnifyingGlass.png()', tornado.web.StaticFileHandler, {'path': frontendPath + '/magnifyingGlass.png'}),
  (r"/shareTech.ttf()", tornado.web.StaticFileHandler, {'path': frontendPath + '/shareTech.ttf'}),
  (r"/hairline.ttf()", tornado.web.StaticFileHandler, {'path': frontendPath + '/hairline.ttf'}),

])

'''
, ssl_options={
    "certfile": os.path.join(backendPath, "ssl/certificate.crt"),
    "keyfile": os.path.join(backendPath, "ssl/private.key"),
})
'''

http_server = tornado.httpserver.HTTPServer(application, ssl_options={
    "certfile": os.path.join(backendPath, "ssl/certificate.crt"),
    "keyfile": os.path.join(backendPath, "ssl/private.key"),
})


if __name__ == "__main__":
  redirectApplication.listen(80)
  http_server.listen(443)
  tornado.ioloop.IOLoop.instance().start()
