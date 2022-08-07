#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import re
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
import datetime
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import collections
from sqlalchemy import desc
collections.Callable = collections.abc.Callable  #by me
#installed a lesser version of jinja2 to be compatible with flask_moment
# installed Werkzeug==2.0.0 to stop the error --> cannot import name 'safe_str_cmp' from 'werkzeug.security'
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Events(db.Model):
  __tablename__ = 'Events'
  id = db.Column(db.Integer,primary_key=True, nullable=False, autoincrement=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
  start_time = db.Column(db.DateTime,nullable=False)

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
    shows = db.relationship('Events', backref='venue',cascade='all, delete-orphan', lazy = True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'
class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_links = db.Column(db.String(500))
    website_link = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    looking_for_venue = db.Column(db.Boolean, default = False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Events', backref='artist',cascade='all, delete-orphan', lazy = True)
    booking_days = db.Column(db.String(500), default='Monday,Tuesday,Wednesday', nullable=True)

    


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, str):
        date = dateutil.parser.parse(value)
  else:
    date = value
  # date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#
def seperateItems(item):
  if item == None:
    return None
  my_list = item.split(",")
  if len(my_list)>1:
    last = my_list[-1]
    if last[-1] == '}':
      last = last.rstrip(last[-1])
    first = my_list[0]
    if first[0] == '{':
      first = first.lstrip(first[0])
    my_list[0] = first
    my_list[-1] = last
    return my_list

def getDayOfTheWeek(date):
  # print(type(date))
  weekday = date.weekday()
  weekdays = ['Monday','Tuesday','Wednesday','Thursday','Friday','Sarturday','Sunday']
  for item in weekdays:
    if weekdays.index(item) == weekday:
      return weekdays[weekday]
      


@app.route('/')
def index():
  artists = Artist.query.order_by(desc('id')).all()[:5]
  venues = Venue.query.order_by(desc('id')).all()[:5]
  event = Events.query.filter_by(id=1).all()[0]
  date = event.start_time
  getDayOfTheWeek(date)
  context = {'venues':venues, 'artists':artists}
  return render_template('pages/home.html', data=context)

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  
  data= Venue.query.order_by('id').all()
  return render_template('pages/venues.html', data=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  keyword = request.form.get('search_term')
  look_for = '%{0}%'.format(keyword)
  venues = Venue.query.filter(Venue.name.ilike(look_for)).all()
  city = Venue.query.filter(Venue.city.ilike(look_for)).all()
  state = Venue.query.filter(Venue.state.ilike(look_for)).all()
  array = []
  if venues or city or state:
    data = venues + city + state
    for item in data:
      if item not in array:
        array.append(item)

  count = len(array)
  context = {'data':array,'count':count}
  return render_template('pages/search_venues.html', results=context, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  upcoming_shows = []
  past_shows = []
  CurrentDate = datetime.now()
  events = Events.query.filter_by(venue_id = venue_id).all() 
  for items in events:
    if items.start_time > CurrentDate:
      upcoming_shows.append(items)
    else:
      past_shows.append(items) 
  data = Venue.query.get(venue_id)
  my_string = data.geners
  my_list = my_string.split(",")
  if len(my_list)>1:
    last = my_list[-1]
    last = last.rstrip(last[-1])
    first = my_list[0]
    first = first.lstrip(first[0])
    my_list[0] = first
    my_list[-1] = last
  context = {"data":data,'upcoming_shows':upcoming_shows,"past_shows":past_shows,'geners':my_list}
  return render_template('pages/show_venue.html', venue=context)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  address = request.form.get('address')
  phone = request.form.getlist('phone')
  genres = request.form.get('genres')
  facebook_link = request.form.get('facebook_link')
  image_link = request.form.get('image_link')
  website_link = request.form.get('website_link')
  seeking_talent = request.form.get('seeking_talent')
  seeking_description = request.form.get('seeking_description')
  try:
    if seeking_talent == 'y':
      seeking_talent = True
    else:
      seeking_talent = False
    venue = Venue(name=name,city=city,state=state,address=address,phone=phone,geners=genres,
                  facebook_link=facebook_link,website_link=website_link,image_link=image_link,looking_for_talent=seeking_talent,
                  seeking_description=seeking_description)
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    # data = Venue.query.filter(name = name).all()
    # print(data)
    flash('Venue ' + name + ' was successfully listed!')
  # TODO: modify data to be the data object returned from db insertion
  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Venue ' + name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  db.session.close()
  artists = Artist.query.order_by(desc('id')).all()[:5]
  venues = Venue.query.order_by(desc('id')).all()[:5]
  context = {'venues':venues, 'artists':artists}
  return render_template('pages/home.html', data=context)

@app.route('/venues/<venue_id>/delete')
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue = Venue.query.get(venue_id)
    event = Events.query.filter_by(venue_id = venue_id).all()
    print(event)
    db.session.delete(venue)
    db.session.commit()

  except:
    db.session.rollback()
  finally:
    db.session.close()
    artists = Artist.query.order_by(desc('id')).all()[:5]
    venues = Venue.query.order_by(desc('id')).all()[:5]
    context = {'venues':venues, 'artists':artists}
    return redirect(url_for('index',data=context))
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  
  
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data= Artist.query.order_by('id').all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  keyword = request.form.get('search_term')
  look_for = '%{0}%'.format(keyword)
  artists = Artist.query.filter(Artist.name.ilike(look_for)).all()
  city = Artist.query.filter(Artist.city.ilike(look_for)).all()
  state = Artist.query.filter(Artist.state.ilike(look_for)).all()
  array = []
  if artists or city or state:
    data = artists + city + state
    for item in data:
      if item not in array:
        array.append(item)

  count = len(array)
  context = {'data':array,'count':count}
  return render_template('pages/search_artists.html', results=context, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  # list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  
  upcoming_shows = []
  past_shows = []
  CurrentDate = datetime.now()
  events = Events.query.filter_by(artist_id = artist_id).all()
  for items in events:
    if items.start_time > CurrentDate:
      upcoming_shows.append(items)
    else:
      past_shows.append(items) 
  data = Artist.query.get(artist_id)
  my_string = data.genres
  availableDays = data.booking_days
  my_list = seperateItems(my_string)
  my_days_of_work = seperateItems(availableDays)
  print(my_days_of_work)
  context = {"data":data,'upcoming_shows':upcoming_shows,"past_shows":past_shows,"geners":my_list,'WorkingDays':my_days_of_work}
  return render_template('pages/show_artist.html', artist=context)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist= Artist.query.get(artist_id)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:

    artist = Artist.query.get(artist_id)
    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.genres = request.form.getlist('genres')
    artist.facebook_link = request.form.get('facebook_link')
    artist.image_link = request.form.get('image_link')
    artist.website_link = request.form.get('website_link')
    seeking_venue = request.form.get('seeking_venue')
    artist.booking_days = request.form.get('booking_days')
    if seeking_venue == 'y':
      artist.looking_for_venue = True
    else:
      artist.looking_for_venue = False
    artist.seeking_description = request.form.get('seeking_description')
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close() 
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue= Venue.query.get(venue_id)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  try:

    venue = Venue.query.get(venue_id)
    venue.name = request.form.get('name')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.address = request.form.get('address')
    venue.phone = request.form.get('phone')
    venue.geners = request.form.getlist('genres')
    venue.facebook_link = request.form.get('facebook_link')
    venue.image_link = request.form.get('image_link')
    venue.website_link = request.form.get('website_link')
    seeking_talent = request.form.get('seeking_talent')
    if seeking_talent == 'y':
      venue.looking_for_talent = True
    else:
      venue.looking_for_talent = False
    venue.seeking_description = request.form.get('seeking_description')
    print(request.form.get('seeking_description'))
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close() 

  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  phone = request.form.get('phone')
  genres = request.form.getlist('genres')
  facebook_link = request.form.get('facebook_link')
  image_link = request.form.get('image_link')
  website_link = request.form.get('website_link')
  seeking_venue = request.form.get('seeking_venue')
  seeking_description = request.form.get('seeking_description')
  booking_days = request.form.get('booking_days')
  try:
    if seeking_venue == 'y':
      seeking_venue = True
    else:
      seeking_venue = False
    artist = Artist(name=name,city=city,state=state,phone=phone,genres=genres,
                  facebook_link=facebook_link,image_links=image_link,looking_for_venue=seeking_venue,
                  seeking_description=seeking_description, website_link=website_link, booking_days=booking_days)
    
    db.session.add(artist)
    db.session.commit()
  # on successful db insert, flash success
    flash('Artist ' + name + ' was successfully listed!')
  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Artist ' + name + ' could not be listed.')
  artists = Artist.query.order_by(desc('id')).all()[:5]
  venues = Venue.query.order_by(desc('id')).all()[:5]
  context = {'venues':venues, 'artists':artists}
  return render_template('pages/home.html', data=context)


# @app.route('/artists/<artist_id>/delete')
# def delete_artist(artist_id):
#   try:
#       artist = Artist.query.get(artist_id)
#       db.session.delete(artist)
#       db.session.commit()
#   except:
#     db.session.rollback()
#   finally:
#       db.session.close()
#       return redirect(url_for('index'))

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data=Events.query.order_by('id').all()
  context = {'shows':data}
  return render_template('pages/shows.html', data = context)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try: 
    venue_id = request.form.get('venue_id')
    artist_id = request.form.get('artist_id')
    start_time = request.form.get('start_time')
    format = '%Y-%m-%d %H:%M:%S'
    converted_time = datetime.strptime(start_time, format)
    artist = Artist.query.get(artist_id)
    day = getDayOfTheWeek(converted_time)
    availableDays = seperateItems(artist.booking_days)
    print(day)
    print(availableDays)
    if day not in availableDays:
      flash('The Artist is Not available at the moment! check artist Profile to see when Artist will be available')
      return redirect(url_for('shows/create'))
    

    venue = Venue.query.get(venue_id)
    event = Events(start_time=start_time)
    event.venue = venue
    event.artist = artist
    db.session.add(event)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:        
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    print(sys.exc_info())
  finally:
    db.session.close()
    artists = Artist.query.order_by(desc('id')).all()[:5]
    venues = Venue.query.order_by(desc('id')).all()[:5]
    context = {'venues':venues, 'artists':artists}           
    return render_template('pages/home.html', data = context)
    
  
  

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
