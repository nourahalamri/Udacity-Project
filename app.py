#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app,db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)
    Shows = db.relationship('Show',backref='Venue',lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String())
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='Artist',lazy=True)

class Show(db.Model):
   __tablename__='Show'
   
   id = db.Column(db.Integer,primary_key=True)
   venue_id = db.Column(db.Integer,db.ForeignKey(Venue.id),nullable=False)#tablename.id
   artist_id = db.Column(db.Integer,db.ForeignKey(Artist.id),nullable=False)#tablename.id
   start_time= db.Column(db.DateTime)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format,locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)
  
    @app.route('/venues/create', methods=['GET', 'POST'])
    def create_venue_submission():
     form = VenueForm()
    error = False
    # if the form passed validation, populate the venue object from form data
    if form.validate_on_submit():
        try:
            venue = Venue()

            form.populate_obj(venue)
            # genres is a list, so convert it to string
            genresList = request.form.getlist('genres')
            venue.genres = ', '.join(genresList)
            db.session.add(venue)
            # to return users to the new venue's page, flush the session, and store the id in another variable
            db.session.flush()
            venue_id = venue.id
            db.session.commit()
        except:
            # if failed, roll back and display a message to the user
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
            # if error, return to home and display a message, or go to the new venue's page
            if error:
                flash('Oops! Something wrong happened, venue ' +
                      str(form.name.data) + ' could not be listed!', 'error')
                return render_template('pages/home.html')
            else:
                flash(
                    'Venue ' + str(form.name.data) + ' was listed successfully!')
                return redirect(url_for('show_venue', venue_id=venue_id))
    return render_template('forms/new_venue.html', form=form)
  
@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    form=VenueForm()
    if form.validate_on_submit():

     try:
        venue = Venue()
        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        tmp_genres = request.form.getlist('genres')
        venue.genres = ','.join(tmp_genres)
        venue.facebook_link = request.form['facebook_link']
        db.session.add(venue)
        db.session.commit()
     except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
     finally:
        db.session.close()
        if error:
            flash('An error occured. Venue ' +
                  request.form['name'] + ' Could not be listed!')
        else:
            flash('Venue ' + request.form['name'] +
                  ' was successfully listed!')
    flash("Wrong Vlidations")        
    return render_template('pages/home.html')

@app.route('/venues')
def venues():
    #venues = Venue.query.order_by(Venue.state, Venue.city).all()
  areas = Venue.query.distinct('city', 'state').order_by('state').all()
  for area in areas:
    area.venues = Venue.query.filter_by(city=area.city, state=area.state)
    
  return render_template('pages/venues.html', areas=areas);

    
    #return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    
    data = []
    response = {}
    
    search_term = request.form.get('search_term')
    venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
    
    for venue in venues:
        a = {}
        a['id'] = venue.id
        a['name'] = venue.name
        data.append(a)
        
        response['count'] = len(data)
        response['data'] = data
        return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  shows = Show.query.filter_by(venue_id=venue_id).all()
  pastShows = []
  upcomingShows = []

  for show in shows:
      date = show.start_time

      if date < datetime.now():
        pastShows.append({
            "artist_id": Artist.query.filter_by(id=show.artist_id).first().id,
            "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
            "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
            "start_time": str(show.start_time)
        })
      if date > datetime.now():
        upcomingShows.append({
            "artist_id": Artist.query.filter_by(id=show.artist_id).first().id,
            "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
            "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
            "start_time": str(show.start_time)
        })

  data = {
      "id": venue.id,
      "name": venue.name,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "image_link": venue.image_link,
      "website": venue.website,
      "genres": venue.genres,
      "facebook_link": venue.facebook_link,
      "seeking_description": venue.seeking_description,
      "past_shows": pastShows,
      "past_shows_count": len(pastShows),
      "upcoming_shows": upcomingShows,
      "upcoming_shows_count": len(upcomingShows)
  }

  return render_template('pages/show_venue.html', venue=data)


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = Venue.query.get(venue_id)

    error = False
    try:
        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        tmp_genres = request.form.getlist('genres')
        venue.genres = ','.join(tmp_genres)  # convert list to string
        venue.facebook_link = request.form['facebook_link']
        db.session.add(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occurred. Venue ' +
                  request.form['name'] + ' could not be updated.')
        else:
            flash('Venue ' + request.form['name'] +
                  ' was successfully updated!')
    return redirect(url_for('show_venue', venue_id=venue_id))



#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  return render_template('pages/artists.html', artists=Artist.query.all())

 # return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
   data = []
   response = {}

   search_term = request.form.get('search_term')
   artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()

   for artist in artists:
      a = {}
      a['id'] = artist.id
      a['name'] = artist.name
      data.append(a)

   response['count'] = len(data)
   response['data'] = data
   return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  artist_query = db.session.query(Artist).get(artist_id)

  if not artist_query: 
    return render_template('errors/404.html')

  past_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()
  past_shows = []

  for show in past_shows_query:
    past_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_image_link": show.venue.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()
  upcoming_shows = []

  for show in upcoming_shows_query:
    upcoming_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_image_link": show.venue.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })


  data = {
    "id": artist_query.id,
    "name": artist_query.name,
    "genres": artist_query.genres,
    "city": artist_query.city,
    "state": artist_query.state,
    "phone": artist_query.phone,
    "website": artist_query.website,
    "facebook_link": artist_query.facebook_link,
    "seeking_venue": artist_query.seeking_venue,
    "seeking_description": artist_query.seeking_description,
    "image_link": artist_query.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
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
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  form=ArtistForm()
  if form.validate_on_submit():

   try:
      artist = Artist()
      artist.name = request.form['name']
      artist.city = request.form['city']
      artist.state = request.form['state']
      artist.phone = request.form['phone']
      tmp_genres = request.form.getlist('genres')
      artist.genres = ','.join(tmp_genres)
      artist.website = request.form['website']
      artist.image_link = request.form['image_link']
      artist.facebook_link = request.form['facebook_link']
      db.session.add(artist)
      db.session.commit()
   except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
   finally:
      db.session.close()
      if error:
              flash('An error occurred. Artist ' + 
                    request.form['name'] + ' could not be listed.')
      else:
              flash('Artist ' + request.form['name'] + 
                    ' was successfully listed!')
  flash("Wrong Validation")
  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------
@app.route('/shows')
def shows():
  shows = Show.query.all()
  data = []
  for show in shows:
      show = {
        "venue_id": show.venue_id,
        "venue_name": db.session.query(Venue.name).filter_by(id=show.venue_id).first()[0],
        "artist_id": show.artist_id,
        "artist_name": db.session.query(Artist.name).filter_by(id=show.artist_id).first()[0],
        "artist_image_link": db.session.query(Artist.image_link).filter_by(id=show.artist_id).first()[0],
        "start_time": str(show.start_time)
      }
      data.append(show)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)
  
@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  body = {}

  try:
    show = Show(
      artist_id = request.form['artist_id'],
      venue_id = request.form['venue_id'],
      start_time = request.form['start_time'],
      )
    db.session.add(show)
    db.session.commit()
    
    body['artist_id'] = request.form['artist_id']
    body['venue_id'] = request.form['venue_id']
    body['start_time'] = request.form['start_time']
  except Exception as e:
          error = True
          db.session.rollback()
          print(sys.exc_info())
  finally:
          db.session.close()
  if error:
    # on unsuccessful db insert, flash an error
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Show could not be listed.')
    return render_template('pages/home.html')
  else:
      # on successful db insert, flash success
    flash('Show was successfully listed!')
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
