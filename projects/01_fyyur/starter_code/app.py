# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
from datetime import datetime

import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from config import SQLALCHEMY_DATABASE_URI
from forms import *
from flask_migrate import Migrate

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)

migrate = Migrate(app, db)

print('#DEBUG connected to db => ', app.config['SQLALCHEMY_DATABASE_URI'])

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#


venue_genres = db.Table('venue_genures',
                        db.Column('venue_id', db.Integer, db.ForeignKey('venues.id'), primary_key=True),
                        db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True)
                        )

artist_genres = db.Table('artist_genres',
                         db.Column('artist_id', db.Integer, db.ForeignKey('artists.id'), primary_key=True),
                         db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True)
                         )


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_description = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Boolean, nullable=True)

    # ******************* Relationships ******************* #
    genres = db.relationship('Genre', secondary=venue_genres, backref=db.backref('venue_genres', lazy=True))
    shows = db.relationship('Show', backref='venue_shows', lazy=True)

    # def __repr__(self):
    #     return f'<Venue id: {self.id}, name: {self.name}, city: {self.city}>'


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_description = db.Column(db.String(120), nullable=True)
    seeking_venue = db.Column(db.Boolean, nullable=True)

    # ******************* Relationships ******************* #

    genres = db.relationship('Genre', secondary=artist_genres, backref=db.backref('artist_genres', lazy=True))
    shows = db.relationship('Show', backref='artist_shows', lazy=True)


class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    start_time = db.Column(db.TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<Show id: {self.id}, venue_id: {self.venue_id}, artist_id:' \
               f' {self.artist_id}, start_time: {self.start_time}>'


class City(db.Model):
    __tablename__ = 'cities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(2), nullable=True)

    city_artist = db.relationship('Artist', backref='city', lazy=True)
    city_venue = db.relationship('Venue', backref='city', lazy=True)

    def __repr__(self):
        return f'<City id: {self.id}, name: {self.name}, state: {self.state}>'


class Genre(db.Model):
    __tablename__ = 'genres'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    all_venues = Venue.query.all()
    data = []

    for venue in all_venues:
        item_index = next((i for i, item in enumerate(data) if venue.city.name == item['city']), None)
        num_of_upcoming_shows = Show.query.filter(
            (Show.venue_id == venue.id) & (Show.start_time > datetime.now())).count()

        venue_item = {
            'id': str(venue.id),
            'name': venue.name,
            "num_upcoming_shows": num_of_upcoming_shows,
        }

        if item_index:
            data[item_index]['venues'].append(venue_item)
        else:
            city_item = {
                'city': venue.city.name,
                'state': venue.city.state,
                'venues': [venue_item]
            }

            data.append(city_item)
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # search for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    search_term = request.form.get('search_term', '')
    venus = Venue.query.join(Show) \
        .filter(Venue.name.contains(search_term) & (Show.start_time >= datetime.now())).all()

    response = {
        "count": len(venus),
        "data": list(map(lambda v: {'id': v.id, 'name': v.name, 'num_upcoming_shows': len(v.shows)}, venus))
    }

    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id

    venue = Venue.query.get(venue_id)
    genres = list(map(lambda v: v.name, venue.genres))
    city = venue.city

    past_shows = Show.query.join(Artist).filter(
        (Show.start_time < datetime.utcnow()) & (Show.venue_id == venue_id)).all()

    for i, show in enumerate(past_shows, start=0):
        print('#DEBUG data date => ', past_shows[i].start_time)
        past_shows[i].start_time = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")

    upcoming_shows = Show.query.join(Artist).filter(
        (Show.start_time >= datetime.utcnow()) & (Show.venue_id == venue_id)).all()

    for i, show in enumerate(upcoming_shows, start=0):
        print('#DEBUG data date => ', upcoming_shows[i].start_time)
        upcoming_shows[i].start_time = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": genres,
        "address": venue.address,
        "city": city.name,
        "state": city.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }

    print(data)

    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

    data = request.form
    genres = data.getlist('genres')
    try:
        city = City.query.filter_by(name=data['city'].strip().lower()).first()

        if city is None:
            new_city = City(name=data['city'].strip().lower(), state=data['state'])
            db.session.add(new_city)
            city = City.query.filter_by(name=data['city'].strip().lower()).first()

        new_venue = Venue(name=data['name'],
                          city_id=city.id,
                          facebook_link=data['facebook_link'],
                          address=data['address'],
                          phone=data['phone'])
        for item in genres:
            genre = Genre.query.filter_by(name=item).first()
            if genre:
                new_venue.genres.append(genre)
            else:
                new_venue.genres.append(Genre(name=item))

        db.session.add(new_venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Venue ' + data['name'] + ' could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    data = db.session.query(Artist.id, Artist.name)
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # search for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    search_term = request.form.get('search_term', '')
    artists = Artist.query.join(Show) \
        .filter(Artist.name.contains(search_term) & (Show.start_time >= datetime.now())).all()

    response = {
        "count": len(artists),
        "data": list(map(lambda v: {'id': v.id, 'name': v.name, 'num_upcoming_shows': len(v.shows)}, artists))
    }

    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    artist = Artist.query.get(artist_id)
    genres = list(map(lambda a: a.name, artist.genres))
    city = artist.city

    past_shows = Show.query.join(Artist) \
        .filter((Show.start_time < datetime.utcnow()) & (Show.artist_id == artist_id)).all()

    for i, show in enumerate(past_shows, start=0):
        past_shows[i].start_time = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")

    upcoming_shows = Show.query.join(Artist) \
        .filter((Show.start_time >= datetime.utcnow()) & (Show.artist_id == artist_id)).all()

    for i, show in enumerate(upcoming_shows, start=0):
        upcoming_shows[i].start_time = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": genres,
        "city": city.name,
        "state": city.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "image_link": artist.image_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
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
    artist = {
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


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = {
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
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
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

    data = request.form
    genres = data.getlist('genres')
    try:
        city = City.query.filter_by(name=data['city'].strip().lower()).first()

        if city is None:
            new_city = City(name=data['city'].strip().lower(), state=data['state'])
            db.session.add(new_city)
            city = City.query.filter_by(name=data['city'].strip().lower()).first()

        new_artist = Artist(name=data['name'],
                          city_id=city.id,
                          facebook_link=data['facebook_link'],
                          phone=data['phone'])
        for item in genres:
            genre = Genre.query.filter_by(name=item).first()
            if genre:
                new_artist.genres.append(genre)
            else:
                new_artist.genres.append(Genre(name=item))

        db.session.add(new_artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')

    except:
        db.session.rollback()
        flash('An error occurred. Artist ' + data.name + ' could not be listed.')

    finally:
        db.session.close()


    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows

    shows = db.session.query(Show.venue_id, Show.artist_id, Show.start_time, Artist.name.label('artist_name'),
                             Artist.image_link.label('artist_image_link'), Venue.name.label('venue_name')) \
        .join(Artist) \
        .join(Venue).all()

    data = []
    for i, show in enumerate(shows, start=0):
        start_date = show.start_time.strftime('%m/%d/%y %H:%M:%S%z')
        data.append({
            'venue_id': show.venue_id,
            'start_time': start_date,
            'artist_id': show.artist_id,
            'artist_name': show.artist_name,
            'artist_image_link': show.artist_image_link,
            'venue_name': show.venue_name
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
    try:
        data = request.form

        new_show = Show(artist_id=data.get('artist_id'), venue_id=data.get('venue_id'),
                        start_time=data.get('start_time'))

        db.session.add(new_show)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Show could not be listed.')
    finally:
        db.session.close()
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

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
