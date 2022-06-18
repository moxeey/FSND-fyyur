#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
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

class Venue(db.Model):
    __tablename__ = 'venues'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # missing fields
    genres = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    # relationship
    shows = db.relationship('Show', backref="venue", lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # missing fields
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    # relationship
    shows = db.relationship('Show', backref="artist", lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = 'shows'
  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime)
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value) if isinstance(value, str) else value
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data =[]
  citiesVenue =  Venue.query.distinct(Venue.city, Venue.state).all()
  for state_and_city in citiesVenue:
    venues_in_city={
      "state":state_and_city.state,
      "city" : state_and_city.city
    }
    venues = Venue.query.filter_by(city=state_and_city.city,state= state_and_city.state).all()
    # reformat venue
    formattedVenues = []
    for venue in venues:
      formattedVenues.append({
        "id":venue.id,
        "name":venue.name,
        "number_upcoming_shows": len(list(filter(lambda show:
          show.start_time > datetime.now(), venue.shows)))
      })
    venues_in_city['venues'] = formattedVenues
    data.append(venues_in_city)
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  venues = Venue.query.filter(Venue.name.ilike(f"%{request.form.get('search_term')}%")).all()
  data = []
  for venue in venues:
    data.append({
      "id":venue.id,
      "name":venue.name,
      "num_upcomig_shows": len(list(filter(lambda show: show.start_time > datetime.now(), venue.shows)))
    })
  
  response={
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  setattr(venue, 'genres', venue.genres.split(','))

  # Get venue past shows
  past_shows = list(filter(lambda s: s.start_time <datetime.now(), venue.shows))
  temp_shows = []
  for show in past_shows:
    temp={}
    temp['artist_id'] = show.artist.id
    temp["artist_name"] = show.artist.name
    temp["artist_image_link"] = show.artist.image_link
    temp["start_time"] = str(show.start_time)
    temp_shows.append(temp)
  setattr(venue, "past_shows", past_shows)
  setattr(venue, "past_shows_count", len(past_shows))

  # Get venue upcomig show
  upcoming_shows = list(filter(lambda s: s.start_time > datetime.now(), venue.shows))
  temp_shows = []
  for show in upcoming_shows:
    temp={}
    temp['artist_id'] = show.artist.id
    temp["artist_name"] = show.artist.name
    temp["artist_image_link"] = show.artist.image_link
    temp["start_time"] = str(show.start_time)
    temp_shows.append(temp)
  setattr(venue, "upcoming_shows", upcoming_shows)
  setattr(venue, "upcoming_shows_count", len(upcoming_shows))

  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  form = VenueForm(request.form)
  if not form.validate():
    flash("Input error"+ str(form.errors))
    return render_template('forms/new_venue.html', form=form)

  venue = Venue(
    name=form.name.data, 
    city=form.city.data, 
    state=form.state.data, 
    address = form.address.data,
    phone= form.phone.data,
    genres= ",".join(form.genres.data),
    facebook_link = form.facebook_link.data,
    image_link= form.image_link.data,
    website = form.website_link.data,
    seeking_talent = form.seeking_talent.data,
    seeking_description = form.seeking_description.data
  )

  data={}
  try:
    db.session.add(venue)
    db.session.commit()
      # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    # TODO: modify data to be the data object returned from db insertion
    data = venue
     # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  finally:
    db.session.close()      
     # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['DELETE', 'GET'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  name =""
  try:
    venue = Venue.query.get(venue_id)
    name =venue.name
    db.session.delete(venue)
    db.session.commit()  
    flash(f"Venue {name} was successfully deleted")
  except:
    db.session.rollback()
    error = True
    flash(f"Venue {name} was not deleted")
  finally:
    db.session.close()
    if error:
      print(sys.exc_info())
      return None
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.all()
  data = []

  for artist in artists:
    data.append({
      "id": artist.id,
      "name" : artist.name
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term')
  artists = Artist.query.filter(Artist.name.ilike(f"%{search_term}%"))
  data =[]
  for artist in artists:
    data.append({
      "name": artist.name,
      "num_upcoming_shows": len(list(filter(lambda show: show.start_time > datetime.now(), artist.shows)))
    })
  response= {
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  setattr(artist, 'genres', artist.genres.split(','))

  # Get artist past shows
  past_shows = list(filter(lambda s: s.start_time <datetime.utcnow(), artist.shows))
  temp_shows = []
  for show in past_shows:
    temp={}
    temp['artist_id'] = show.artist.id
    temp["artist_name"] = show.artist.name
    temp["artist_image_link"] = show.artist.image_link
    temp["start_time"] = str(show.start_time)
    temp_shows.append(temp)
  setattr(artist, "past_shows", past_shows)
  setattr(artist, "past_shows_count", len(past_shows))

# Get artist upcomig show
  upcoming_shows = list(filter(lambda s: s.start_time > datetime.now(), artist.shows))
  temp_shows = []
  for show in upcoming_shows:
    temp={}
    temp['artist_id'] = show.artist.id
    temp["artist_name"] = show.artist.name
    temp["artist_image_link"] = show.artist.image_link
    temp["start_time"] = str(show.start_time)
    temp_shows.append(temp)
  setattr(artist, "upcoming_shows", upcoming_shows)
  setattr(artist, "upcoming_shows_count", len(upcoming_shows))
  data = artist
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  
  # TODO: populate form with fields from artist with ID <artist_id>
  artist = Artist.query.get(artist_id)
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = artist.genres.split(",")
  form.facebook_link.data = artist.facebook_link
  form.image_link.data = artist.image_link
  form.website_link.data = artist.website
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  form = ArtistForm(request.form)
  try:
    artist = Artist.query.get(artist_id)
    artist.name = form.name.data
    artist.genres = ",".join(form.genres.data)
    artist.city= form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.website = form.website_link.data
    artist.facebook_link = form.facebook_link.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data
    artist.image_link = form.image_link.data

    db.session.commit()
    flash(f"Artist {artist.name} updated successfully")
  except:
    db.session.rollback()
    flash(f"Artist {artist.name} was not updated")
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }

  # TODO: populate form with values from venue with ID <venue_id>
  venue = Venue.query.get(venue_id)
  
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.genres.data = venue.genres.split(",")
  form.facebook_link.data = venue.facebook_link
  form.image_link.data = venue.image_link
  form.website_link.data = venue.website
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  
  form = VenueForm(request.form)
  try:
    venue = Venue.query.get(venue_id)
    venue.name = form.name.data
    venue.genres = ",".join(form.genres.data)
    venue.city= form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.phone = form.phone.data
    venue.website = form.website_link.data
    venue.facebook_link = form.facebook_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    venue.image_link = form.image_link.data
    db.session.commit()
    flash(f"Venue {venue.name} updated successfully")
    
  except:
    db.session.rollback()
    flash(f"Venue {venue.name} was not updated")
  finally:
    db.session.close()

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
  # TODO: insert form data as a new Artist record in the db, instead
  form = ArtistForm(request.form)
  if not form.validate():
    flash("Input error"+ str(form.errors))
    return render_template('forms/new_artist.html', form=form)
    

  artist = Artist(
    name=form.name.data, 
    city=form.city.data, 
    state=form.state.data, 
    phone=form.phone.data,
    genres=",".join(form.genres.data),
    facebook_link = form.facebook_link.data,
    image_link= form.image_link.data,
    website = form.website_link.data,
    seeking_venue = form.seeking_venue.data,
    seeking_description = form.seeking_description.data
  )

  data={}
  try:
    db.session.add(artist)
    db.session.commit()
      # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    # TODO: modify data to be the data object returned from db insertion
    data = artist
     # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  finally:
    db.session.close()      
    
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows  = Show.query.all()
  data = []

  for show in shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time" : str(show.start_time)
    })
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)
  if not form.validate():
    flash("Input error"+ str(form.errors))
    return render_template('forms/new_show.html', form=form)


  show = Show(
    start_time = form.start_time.data,
    venue_id = form.venue_id.data,
    artist_id = form.artist_id.data
  )
  try:
    db.session.add(show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash("An error occured. Show couln't be listed")
    
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

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
