import cgi
import re
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
        edit_pattern = re.compile('/restaurant/(\\d+)/edit')
        delete_pattern = re.compile('/restaurant/(\\d+)/delete')

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
                            <a href="/restaurant/%s/delete">Delete</a>
                          </p>
                          ''' % (restaurant.id, restaurant.id)

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
            output += '</body></html>'
            self.wfile.write(output)
        elif edit_pattern.match(self.path):
            restaurant_id = int(edit_pattern.match(self.path).groups()[0])

            restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()

            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()

            output = '<html><body>'
            output += '<h1>%s</h1>' % restaurant.name
            output += '''
                      <form method="post" enctype="multipart/form-data" action="/restaurant/%s/edit">
                      <input type="text" name="name" placeholder="%s">
                      <input type="hidden" name="id" value="%s">
                      <input type="submit">
                      </form>
                      ''' % (restaurant.id, restaurant.name, restaurant.id)
            output += '</body></html>'
            self.wfile.write(output)
        elif delete_pattern.match(self.path):
            restaurant_id = int(delete_pattern.match(self.path).groups()[0])

            restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()

            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()

            output = '<html><body>'
            output += '<h1>Are you sure you want to delete %s?</h1>' % restaurant.name
            output += '''
                      <form method="post" enctype="multipart/form-data" action="/restaurant/%s/delete">
                      <input type="submit">
                      </form>
                      ''' % restaurant.id
            output += '</body></html>'
            self.wfile.write(output)
        else:
            self.send_error(404, 'File not found %s' % self.path)

    def do_POST(self):
        edit_pattern = re.compile('/restaurant/(\d+)/edit')
        delete_pattern = re.compile('/restaurant/(\\d+)/delete')

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
        elif edit_pattern.match(self.path):
            ctype, pdict = cgi.parse_header(
                self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                restaurant_name = fields.get('name')
                restaurant_id = fields.get('id')

            if restaurant_name and restaurant_id:
                restaurant = session.query(Restaurant).filter_by(id=restaurant_id[0]).one()
                restaurant.name = restaurant_name[0]
                session.add(restaurant)
                session.commit()
            self.send_response(301)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Location', '/restaurant')
            self.end_headers()
        elif delete_pattern.match(self.path):
            ctype, pdict = cgi.parse_header(
                self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)

            restaurant_id = int(delete_pattern.match(self.path).groups()[0])

            restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()

            if restaurant:
                restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
                session.delete(restaurant)
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
