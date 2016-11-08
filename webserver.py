import cgi
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

class WebServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith('/restaurant'):
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()

            output = '<html><body>'

            restaurants = session.query(Restaurant).all()

            for restaurant in restaurants:
                output += '<h2>%s</h2>' % restaurant.name

            output += '</body></html>'
            self.wfile.write(output)
            print output
        else:
            self.send_error(404, 'File not found %s' % self.path)
    def do_POST(self):
        try:
            self.send_response(301)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()

            ctype, pdict = cgi.parse_header(
                self.headers.getheader('content-type'))
            print ctype, pdict
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('message')

            output = '<html><body>'
            output += '<h2>Okay, how about this?</h2>'
            output += '<h1>%s</h1>' % messagecontent[0]
            output += '<h2>What would you like me to say?</h2>'
            output += '''
                      <form method="post" enctype="multipart/form-data" action="/hello">
                        <input type="text" name="message">
                        <input type="submit">
                      </form>
                      '''
            output += '</body></html>'
            self.wfile.write(output)
            print output
        except:
            pass


def main():
    try:
        server_address = ('', 8080)
        server = HTTPServer(server_address, WebServerHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C entered, stopping server...'
        server.socket.close()

if __name__ == '__main__':
    main()
