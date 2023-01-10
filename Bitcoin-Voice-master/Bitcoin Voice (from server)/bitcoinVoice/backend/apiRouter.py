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
import mimetypes
mimetypes.add_type("text/css", "css") #add the asociation that all css files have a text/css
frontendPath = sys.argv[1] + "/frontend"
backendPath = sys.argv[1] + "/backend"

path = sys.argv[1]

def getConfig():
  return json.loads(open(backendPath + "/config.json").read())


class fileHandler(tornado.web.StaticFileHandler):
    def initialize(self, path):
        self.dirname, self.filename = os.path.split(path)
        super(fileHandler, self).initialize(self.dirname)

    def get(self, path=None, include_body=True):
        # Ignore 'path'.
        super(fileHandler, self).get(self.filename, include_body)

class redirect (tornado.web.RequestHandler):
  def get(self):
    self.redirect("https://" +  self.request.host + self.request.uri)

class apiHandler(tornado.web.RequestHandler):
  # This routing table directs off to the services to support the UI.
  # Route to the appropriate function, passing in parameters as required.

    def get(self):
        function = self.get_argument("function")

        if function == "getUiDefaults":
          uiDefaults = getConfig()["uiDefaults"]
          self.write(json.dumps(uiDefaults))

        elif function == "getPublicLabelAggregates":
          rowsCount = getConfig()["uiDefaults"]["rowsCount"]
          chainID = int(self.get_argument("chainID", default=2))
          endPos = rowsCount if self.get_argument("endPos", default="") == "" else int(self.get_argument("endPos", default=rowsCount))
          startPos = 0 if self.get_argument("startPos") == "" else int(self.get_argument("startPos", default=0))
          endDate = float(self.get_argument("endDate", default=100000000000))
          startDate = float(self.get_argument("startDate", default=-1))
          searchTerm = self.get_argument("searchTerm", default="").lower()

          labels = interface.getPublicLabelAggregates(chainID, startPos, endPos, startDate, endDate, searchTerm)
          self.write(json.dumps(labels))

        elif function == "getPublicLabelOutputs":
          rowsCount = getConfig()["uiDefaults"]["rowsCount"]
          chainID = int(self.get_argument("chainID", default=2))
          endPos = rowsCount if self.get_argument("endPos", default="") == "" else int(self.get_argument("endPos", default=rowsCount))
          startPos = 0 if self.get_argument("startPos") == "" else int(self.get_argument("startPos", default=0))
          startDate = float(self.get_argument("startDate", default=-1))
          endDate = float(self.get_argument("endDate", default=100000000000))
          publicLabel = self.get_argument("publicLabel")
          onlyUnspent = int(self.get_argument("onlyUnspent", default=1))

          labels = interface.getPublicLabelOutputs(chainID, startDate, endDate, startPos, endPos, publicLabel, onlyUnspent)
          self.write(json.dumps(labels))


redirectApplication = tornado.web.Application([
       (r'/.*', redirect)
    ])


application = tornado.web.Application([
  (r"/api/", apiHandler),
  (r'/(.+)', tornado.web.StaticFileHandler, {'path': frontendPath}),
  (r"/", fileHandler, {'path': frontendPath + "/index.html"}),
])

http_server = tornado.httpserver.HTTPServer(application, ssl_options={
    "certfile": os.path.join(backendPath, "ssl/certificate.crt"),
    "keyfile": os.path.join(backendPath, "ssl/private.key"),
})


if __name__ == "__main__":
  redirectApplication.listen(80)
  http_server.listen(443)
  tornado.ioloop.IOLoop.instance().start()
