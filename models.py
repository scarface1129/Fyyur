from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from flask_migrate import Migrate
import app
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    geners = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_description = db.Column(db.String(500))
    looking_for_talent = db.Column(db.Boolean, default = False)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(120))
    looking_for_venue = db.Column(db.Boolean, default = False)
    seeking_description = db.Column(db.String(500))
    venue = db.relationship('Venue', secondary=shows,
      backref=db.backref('artist', lazy=True))

shows = db.Table('shows',
    db.Column('Artist_id', db.Integer, db.ForeignKey('Artist.id'), primary_key=True),
    db.Column('Venue_id', db.Integer, db.ForeignKey('Venue.id'), primary_key=True),
    db.Column(db.DateTime)
)