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
from flask_wtf import FlaskForm
from forms import *
from flask_migrate import Migrate
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)

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
    genres = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(300))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.Text())
    artists = db.relationship('Show', back_populates='venue')


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
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(300))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.Text())
    venues = db.relationship('Show', back_populates='artist')


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
# using the association object pattern, see: https://docs.sqlalchemy.org/en/13/orm/basic_relationships.html
class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    start_date = db.Column(db.DateTime, nullable=False)
    venue = db.relationship('Venue', back_populates='artists')
    artist = db.relationship('Artist', back_populates='venues')

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


def parse_genres(genres_string):
    return genres_string[1:-1].split(',')


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
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    venues = Venue.query.all()
    possible_city_state = []
    for venue in venues:
        possible_city_state.append(venue.city + ',' + venue.state)
    unique_city_state = set(possible_city_state)
    data = []
    for city_state in unique_city_state:
        city, state = city_state.split(',')
        city_state_info = {
            'city': city,
            'state': state,
            'venues': []
        }
        data.append(city_state_info)
    now = datetime.datetime.now()
    for venue in venues:
        venue_data = {}
        venue_data['id'] = venue.id
        venue_data['name'] = venue.name
        upcoming_shows = [
            show.start_date for show in venue.artists if show.start_date > now]
        venue_data['num_upcoming_shows'] = len(upcoming_shows)
        for entry in data:
            if entry['city'] == venue.city and entry['state'] == venue.state:
                entry['venues'].append(venue_data)

    # structure od the data to render
    # data = [{
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "venues": [{
    #         "id": 1,
    #         "name": "The Musical Hop",
    #         "num_upcoming_shows": 0,
    #     }, {
    #         "id": 3,
    #         "name": "Park Square Live Music & Coffee",
    #         "num_upcoming_shows": 1,
    #     }]
    # }, {
    #     "city": "New York",
    #     "state": "NY",
    #     "venues": [{
    #         "id": 2,
    #         "name": "The Dueling Pianos Bar",
    #         "num_upcoming_shows": 0,
    #     }]
    # }]
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get('search_term', '')
    found_venues = Venue.query.filter(
        Venue.name.ilike('%' + search_term + '%')).all()
    response = {
        'count': len(found_venues),
        'data': []
    }
    now = datetime.datetime.now()
    for venue in found_venues:
        venue_data = {}
        venue_data['id'] = venue.id
        venue_data['name'] = venue.name
        upcoming_shows = [
            show.start_date for show in venue.artists if show.start_date > now]
        venue_data['num_upcoming_shows'] = len(upcoming_shows)
        response['data'].append(venue_data)
    print(response)

    # structure of the data to render
    # response = {
    #     "count": 1,
    #     "data": [{
    #         "id": 2,
    #         "name": "The Dueling Pianos Bar",
    #         "num_upcoming_shows": 0,
    #     }]
    # }
    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.get(venue_id)
    data = {
        'id': venue.id,
        'name': venue.name,
        'genres': parse_genres(venue.genres),
        'address': venue.address,
        'city': venue.city,
        'state': venue.state,
        'phone': venue.phone,
        'website': venue.website,
        'facebook_link': venue.facebook_link,
        'seeking_talent': venue.seeking_talent,
        'seeking_description': venue.seeking_description,
        'image_link': venue.image_link,
        'past_shows': [],
        'upcoming_shows': [],
        'past_shows_count': 0,
        'upcoming_shows_count': 0
    }
    now = datetime.datetime.now()
    for show in venue.artists:
        artist_info = {
            'artist_id': show.artist.id,
            'artist_name': show.artist.name,
            'artist_image_link': show.artist.image_link,
            'start_time': str(show.start_date)
        }
        if show.start_date < now:
            data['past_shows'].append(artist_info)
        else:
            data['upcoming_shows'].append(artist_info)
    data['past_shows_count'] = len(data['past_shows'])
    data['upcoming_shows_count'] = len(data['upcoming_shows'])

    # structure of the data to render
    # data1 = {
    #     "id": 4,
    #     "name": "The Musical Hop",
    #     "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    #     "address": "1015 Folsom Street",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "123-123-1234",
    #     "website": "https://www.themusicalhop.com",
    #     "facebook_link": "https://www.facebook.com/TheMusicalHop",
    #     "seeking_talent": True,
    #     "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    #     "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    #     "past_shows": [{
    #         "artist_id": 4,
    #         "artist_name": "Guns N Petals",
    #         "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #         "start_time": "2019-05-21T21:30:00.000Z"
    #     }],
    #     "upcoming_shows": [],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 0,
    # }
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    req = request.form
    form = VenueForm(req)
    if form.validate():
        try:
            seeking_talent = False
            if len(req['seeking_description']) > 0:
                seeking_talent = True
            created_venue = Venue(
                name=req['name'],
                city=req['city'],
                state=req['state'],
                address=req['address'],
                phone=req['phone'],
                genres=req.getlist('genres'),
                facebook_link=req['facebook_link'],
                image_link=req['image_link'],
                website=req['website'],
                seeking_talent=seeking_talent,
                seeking_description=req['seeking_description'],
            )
            db.session.add(created_venue)
            db.session.commit()
            flash('Venue ' + req['name'] + ' was successfully listed!')
        except SQLAlchemyError as err:
            print(err)
            db.session.rollback()
            # TODO: on unsuccessful db insert, flash an error instead.
            flash('An error occurred. Artist ' +
                  req['name'] + ' could not be listed.')
            # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        finally:
            db.session.close()
    else:
        flash('The Venue data is not valid. Please try again!')
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        venue_query = Venue.query.filter_by(id=venue_id)
        if venue_query:
            venue_query.delete()
            db.session.commit()
    except SQLAlchemyError as err:
        print(err)
        db.session.rollback()
    finally:
        db.session.close()
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    artists = Artist.query.all()
    data = []
    for artist in artists:
        info = {}
        info['id'] = artist.id
        info['name'] = artist.name
        data.append(info)
    # data = [{
    #     "id": 4,
    #     "name": "Guns N Petals",
    # }, {
    #     "id": 5,
    #     "name": "Matt Quevedo",
    # }, {
    #     "id": 6,
    #     "name": "The Wild Sax Band",
    # }]
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term', '')
    found_artists = Artist.query.filter(
        Artist.name.ilike('%' + search_term + '%')).all()
    response = {
        'count': len(found_artists),
        'data': []
    }
    now = datetime.datetime.now()
    for artist in found_artists:
        artist_data = {}
        artist_data['id'] = artist.id
        artist_data['name'] = artist.name
        upcoming_shows = [
            show.start_date for show in artist.venues if show.start_date > now]
        artist_data['num_upcoming_shows'] = len(upcoming_shows)
        response['data'].append(artist_data)
    # response = {
    #     "count": 1,
    #     "data": [{
    #         "id": 4,
    #         "name": "Guns N Petals",
    #         "num_upcoming_shows": 0,
    #     }]
    # }
    return render_template('pages/search_artists.html', results=response, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    artist = Artist.query.get(artist_id)
    data = {
        'id': artist.id,
        'name': artist.name,
        'genres': parse_genres(artist.genres),
        'city': artist.city,
        'state': artist.state,
        'phone': artist.phone,
        'website': artist.website,
        'facebook_link': artist.website,
        'seeking_venue': artist.seeking_venue,
        'seeking_description': artist.seeking_description,
        'image_link': artist.image_link,
        'past_shows': [],
        'upcoming_shows': [],
        'past_shows_count': 0,
        'upcoming_shows_count': 0
    }
    now = datetime.datetime.now()
    for show in artist.venues:
        venue_info = {
            'venue_id': show.venue.id,
            'venue_name': show.venue.name,
            'venue_image_link': show.venue.image_link,
            'start_time': str(show.start_date)
        }
        if show.start_date < now:
            data['past_shows'].append(venue_info)
        else:
            data['upcoming_shows'].append(venue_info)
    data['past_shows_count'] = len(data['past_shows'])
    data['upcoming_shows_count'] = len(data['upcoming_shows'])

    # structure of the data to render
    # data1 = {
    #     "id": 4,
    #     "name": "Guns N Petals",
    #     "genres": ["Rock n Roll"],
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "326-123-5000",
    #     "website": "https://www.gunsnpetalsband.com",
    #     "facebook_link": "https://www.facebook.com/GunsNPetals",
    #     "seeking_venue": True,
    #     "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    #     "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #     "past_shows": [{
    #         "venue_id": 1,
    #         "venue_name": "The Musical Hop",
    #         "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    #         "start_time": "2019-05-21T21:30:00.000Z"
    #     }],
    #     "upcoming_shows": [],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 0,
    # }
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    if artist:
        # https://stackoverflow.com/questions/42984453/wtforms-populate-form-with-data-if-data-exists
        genres = parse_genres(artist.genres)
        artist_data = {
            "id": artist.id,
            "name": artist.name,
            "genres": genres,
            "city": artist.city,
            "state": artist.state,
            "phone": artist.phone,
            "website": artist.website,
            "facebook_link": artist.facebook_link,
            "seeking_venue": artist.seeking_venue,
            "seeking_description": artist.seeking_description,
            "image_link": artist.image_link
        }
        # TODO: populate form with fields from artist with ID <artist_id>
        form = ArtistForm(data=artist_data)
        return render_template('forms/edit_artist.html', form=form, artist=artist_data)
    else:
        return render_template('errors/404.html'), 404


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    req = request.form
    artist = Artist.query.get(artist_id)
    if artist:
        seeking_venue = False
        if len(req['seeking_description']) > 0:
            seeking_venue = True
        try:
            artist.name = req['name']
            artist.city = req['city']
            artist.state = req['state']
            artist.phone = req['phone']
            artist.genres = req.getlist('genres')
            artist.facebook_link = req['facebook_link']
            artist.image_link = req['image_link']
            artist.website = req['website']
            artist.seeking_venue = seeking_venue
            artist.seeking_description = req['seeking_description']
            db.session.commit()
        except SQLAlchemyError as err:
            print(err)
            db.session.rollback()
        finally:
            db.session.close()
        return redirect(url_for('show_artist', artist_id=artist_id))
    else:
        return render_template('errors/404.html'), 404


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id)
    if venue:
        # https://stackoverflow.com/questions/42984453/wtforms-populate-form-with-data-if-data-exists
        genres = parse_genres(venue.genres)
        venue_data = {
            "id": venue.id,
            "name": venue.name,
            "genres": genres,
            "address": venue.address,
            "city": venue.city,
            "state": venue.state,
            "phone": venue.phone,
            "website": venue.website,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.seeking_description,
            "image_link": venue.image_link
        }
        # TODO: populate form with fields from artist with ID <artist_id>
        form = VenueForm(data=venue_data)
        return render_template('forms/edit_venue.html', form=form, venue=venue_data)
    else:
        return render_template('errors/404.html'), 404


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    req = request.form
    venue = Venue.query.get(venue_id)
    if venue:
        seeking_talent = False
        if len(req['seeking_description']) > 0:
            seeking_talent = True
        try:
            venue.name = req['name']
            venue.genres = req.getlist('genres')
            venue.address = req['address']
            venue.city = req['city']
            venue.state = req['state']
            venue.phone = req['phone']
            venue.website = req['website']
            venue.facebook_link = req['facebook_link']
            venue.seeking_talent = seeking_talent
            venue.seeking_description = req['seeking_description']
            venue.image_link = req['image_link']
            db.session.commit()
        except SQLAlchemyError as err:
            print(err)
            db.session.rollback()
        finally:
            db.session.close()
        return redirect(url_for('show_venue', venue_id=venue_id))
    else:
        return render_template('errors/404.html'), 404


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
    req = request.form
    form = ArtistForm(req)
    if form.validate():
        try:
            seeking_venue = False
            if len(req['seeking_description']) > 0:
                seeking_venue = True
            created_artist = Artist(
                name=req['name'],
                city=req['city'],
                state=req['state'],
                phone=req['phone'],
                genres=req.getlist('genres'),
                facebook_link=req['facebook_link'],
                image_link=req['image_link'],
                website=req['website'],
                seeking_venue=seeking_venue,
                seeking_description=req['seeking_description'],
            )
            db.session.add(created_artist)
            db.session.commit()
            # on successful db insert, flash success
            flash('Artist ' + req['name'] + ' was successfully listed!')
        except SQLAlchemyError as err:
            print(err)
            db.session.rollback()
            # TODO: on unsuccessful db insert, flash an error instead.
            flash('An error occurred. Artist ' +
                  req['name'] + ' could not be listed.')
        finally:
            db.session.close()
    else:
        flash('The Artist data is not valid. Please try again!')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    shows_joined = Show.query.options(
        db.joinedload('artist'), db.joinedload('venue')).all()
    data = []
    for entry in shows_joined:
        item = {
            "venue_id": entry.venue_id,
            "venue_name": entry.venue.name,
            "artist_id": entry.artist_id,
            "artist_name": entry.artist.name,
            "artist_image_link": entry.artist.image_link,
            "start_time": str(entry.start_date)
        }
        data.append(item)

    # structure of the data to render
    # data = [{
    #     "venue_id": 1,
    #     "venue_name": "The Musical Hop",
    #     "artist_id": 4,
    #     "artist_name": "Guns N Petals",
    #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #     "start_time": "2019-05-21T21:30:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 5,
    #     "artist_name": "Matt Quevedo",
    #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #     "start_time": "2019-06-15T23:00:00.000Z"
    # }]
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    req = request.form
    form = ShowForm(req)
    if form.validate():
        try:
            check_artist_id = Artist.query.get(req['artist_id'])
            check_venue_id = Venue.query.get(req['venue_id'])
            if check_artist_id and check_venue_id:
                artist_id = req['artist_id']
                venue_id = req['venue_id']
                created_show = Show(
                    artist_id=artist_id,
                    venue_id=venue_id,
                    start_date=req['start_time']
                )
                db.session.add(created_show)
                db.session.commit()
                flash('Show was successfully listed!')
            else:
                flash('Artist ID or Venue ID not found in database. Please check again.')
        except SQLAlchemyError as err:
            print(err)
            db.session.rollback()
            # TODO: on unsuccessful db insert, flash an error instead.
            flash('An error occurred. Show could not be listed.')
            # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        finally:
            db.session.close()
    else:
        flash('The start time should be greater than today. Please post a show that takes place in the future!')
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
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
