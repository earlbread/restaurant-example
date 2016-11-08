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
            output += '<p><a href="/restaurant/new">Create new restaurant</a></p>'

            restaurants = session.query(Restaurant).all()


            for restaurant in restaurants:
                output += restaurant.name
                output += '''
                          <p>
                            <a href="/restaurant/%s/edit">Edit</a>
                            <a href="/restaurant/delete">Delete</a>
                          </p>
                          ''' % restaurant.id

            output += '</body></html>'
            self.wfile.write(output)
        elif self.path.endswith('/restaurant/new'):
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()

            output = '<html><body>'
            output += '<h1>Make a new restaurant</h1>'
            output += '''
                      <form method="post" enctype="multipart/form-data" action="/restaurant/new">
                      <input type="text" name="name" placeholder="New restaraunt name">
                      <input type="submit">
                      </form>
                      '''
            self.wfile.write(output)
        else:
            self.send_error(404, 'File not found %s' % self.path)

    def do_POST(self):
        if self.path.endswith('/restaurant/new'):
            ctype, pdict = cgi.parse_header(
                self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                restaurant_name = fields.get('name')

            if restaurant_name:
                new_restaurant = Restaurant(name=restaurant_name[0])
                session.add(new_restaurant)
                session.commit()

            self.send_response(301)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Location', '/restaurant')
            self.end_headers()

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
