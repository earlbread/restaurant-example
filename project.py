from flask import Flask

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)

@app.route('/')
@app.route('/restaurants/<int:restaurant_id>/')
def restaurant_menu(restaurant_id):
    menus = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()

    output = '<html><body>'

    for menu in menus:
        output += '<p>%s</p>' % menu.name
        output += '<p>%s</p>' % menu.price
        output += '<p>%s</p>' % menu.description
        output += '<br>'

    output += '</body></html>'

    return output


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
