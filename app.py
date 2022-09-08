#----------------------------------------------------------------------------#
# Attribution
# https://github.com/BernardKwesi/cd0046-SQL-and-Data-Modeling-for-the-Web/blob/master/app.py
# https://github.com/bytrebase/cd0046-SQL-and-Data-Modeling-for-the-Web/blob/master/app.py
#----------------------------------------------------------------------------#


#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from datetime import datetime
from models.Venue import Venue
from models.Artist import Artist
from models.Show import Show
from utils.connection import db
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
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
def get_upcoming_shows(shows):
    num_of_upcoming_shows = 0

    for show in shows:
        if show.start_time.isoformat() >= datetime.now().isoformat():
            num_of_upcoming_shows += 1
    return num_of_upcoming_shows

def get_upcoming_venue_shows(venue):
    # get the num of upcoming shows for that venue ID
    all_shows = Show.query.filter_by(venue_id=venue.id).all()
    return get_upcoming_shows(all_shows)
    
def get_upcoming_artist_shows(artist):
    # get the num of upcoming shows for that artist ID
    all_shows = Show.query.filter_by(venue_id=artist.id).all()
    return get_upcoming_shows(all_shows)


def addVenue(venue):
    new_venue = dict()
    new_venue["id"] = venue.id
    new_venue["name"] = venue.name
    new_venue["num_upcoming_shows"] = get_upcoming_venue_shows(venue)
    return new_venue


@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    all_venues = Venue.query.all()
    venueDict = dict()
    state = list()
    data = list()
    for venue in all_venues:
        venueDict["city"] = venue.city
        venueDict["state"] = venue.state
        venueDict["venues"] = []
        if venue.state not in state:
            venueDict["venues"].append(addVenue(venue))
            state.append(venue.state)
            data.append(venueDict)
            venueDict = {}
        else:
            state_index = state.index(venue.state)
            data[state_index]["venues"].append(addVenue(venue))

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get('search_term')
    search_results = Venue.query.filter(
        Venue.name.ilike('%{}%'.format(search_term))).all()
    data = []
    for venue in search_results:
        data.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": get_upcoming_venue_shows(venue)
        })

    response = {
        "count": len(search_results),
        "data": data
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.filter_by(id = venue_id).first()
    data = dict()

    data["id"] = venue.id
    data["name"] = venue.name
    data["genres"] = venue.genres
    data["address"] = venue.address
    data["city"] = venue.city
    data["state"] = venue.state
    data["phone"] = venue.phone
    data["website"] = venue.website
    data["facebook_link"] = venue.facebook_link
    data["seeking_talent"] = venue.seeking_talent
    data["seeking_description"] = venue.seeking_description if venue.seeking_description is not None else ""
    data["image_link"] = venue.image_link

    past_shows = Show.query.join(Venue).filter(Show.artist_id == venue.id).filter(Show.start_time < datetime.now())
    upcoming_shows = Show.query.join(Venue).filter(Show.artist_id == venue.id).filter(Show.start_time > datetime.now())
    past_shows_list = []
    upcoming_shows_list = []
    for past_show in past_shows:
        show = dict()
        show["artist_id"] = past_show.artist.id
        show["artist_name"] = past_show.artist.name
        show["artist_image_link"] = past_show.artist.image_link
        show["start_time"] = str(past_show.start_time)
        past_shows_list.append(show)

    for upcoming_show in upcoming_shows:
        show = dict()
        show["artist_id"] = upcoming_show.artist.id
        show["artist_name"] = upcoming_show.artist.name
        show["artist_image_link"] = upcoming_show.artist.image_link
        show["start_time"] = str(upcoming_show.start_time)
        upcoming_shows_list.append(show)

    data["past_shows"] = past_shows_list
    data["upcoming_shows"] = upcoming_shows_list
    data["past_shows_count"] = len(past_shows_list)
    data["upcoming_shows_count"] = len(upcoming_shows_list)

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

    # on successful db insert, flash success
    # flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

    form = VenueForm(request.form)
    error = False
    if form.validate():
        try:
            name = request.form.get('name')
            city = request.form.get('city')
            state = request.form.get('state')
            address = request.form.get('address')
            phone = request.form.get('phone')
            genres = request.form.getlist('genres')
            facebook_link = request.form.get('facebook_link')
            image_link = request.form.get('image_link')
            website_link = request.form.get('website_link')
            seeking_talent = request.form.get('seeking_talent')
            # seeking_talent = True if request.form.get('seeking_talent') is not None else False
            seeking_description = request.form.get('seeking_description')

            new_venue = Venue(
                name=name,
                city=city,
                state=state,
                address=address,
                phone=phone,
                genres=genres,
                facebook_link=facebook_link,
                image_link=image_link,
                website=website_link,
                seeking_talent=seeking_talent,
                seeking_description=seeking_description
            )
            db.session.add(new_venue)
            db.session.commit()
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()

        if error:
            flash('An error occurred. Venue ' + name + ' could not be listed.')
            return redirect(url_for('create_venue_form', form=form))
        else:
            flash('Venue ' + name + ' was successfully listed!')
            return render_template('pages/home.html')
    else:
        errors = form.errors
        for key in errors:
            flash(key + ' ' + errors[key][0])
        return redirect(url_for('create_venue_form', form=form))


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error = False
    try:
        venue = Venue.query.filter_by(id=venue_id).first()
        db.session.delete(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()

    if error:
        flash('An error occurred. Venue ' +
              venue.name + ' could not be deleted.')
    else:
        flash('Venue ' + venue.name + ' has been deleted.')

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = []
    artists = Artist.query.all()
    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name
        })

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term')
    search_results = Artist.query.filter(
        Artist.name.ilike('%{}%'.format(search_term))).all()
    data = []
    for artist in search_results:
        data.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": get_upcoming_artist_shows(artist)
        })

    response = {
        "count": len(data),
        "data": data
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    artist = Artist.query.filter_by(id = artist_id).first()
    data = dict()

    data["id"] = artist.id
    data["name"] = artist.name
    data["genres"] = artist.genres
    data["city"] = artist.city
    data["state"] = artist.state
    data["phone"] = artist.phone
    data["facebook_link"] = artist.facebook_link
    data["seeking_venue"] = artist.seeking_venue
    data["image_link"] = artist.image_link
    
    past_shows = Show.query.join(Artist).filter(Show.artist_id == artist.id).filter(Show.start_time < datetime.now())
    upcoming_shows = Show.query.join(Artist).filter(Show.artist_id == artist.id).filter(Show.start_time > datetime.now())
    past_shows_list = []
    upcoming_shows_list = []
    for past_show in past_shows:
        show = dict()
        show["venue_id"] = past_show.venue.id
        show["venue_name"] = past_show.venue.name
        show["venue_image_link"] = past_show.venue.image_link
        show["start_time"] = str(past_show.start_time)
        past_shows_list.append(show)

    for upcoming_show in upcoming_shows:
        show = dict()
        show["venue_id"] = upcoming_show.venue.id
        show["venue_name"] = upcoming_show.venue.name
        show["venue_image_link"] = upcoming_show.venue.image_link
        show["start_time"] = str(upcoming_show.start_time)
        upcoming_shows_list.append(show)

    data["past_shows"] = past_shows_list
    data["upcoming_shows"] = upcoming_shows_list
    data["past_shows_count"] = len(past_shows_list)
    data["upcoming_shows_count"] = len(upcoming_shows_list)

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.filter_by(id = artist_id).first()
    form['name'].data = artist.name
    form['genres'].data = artist.genres
    form['city'].data = artist.city
    form['state'].data = artist.state
    form['phone'].data = artist.phone
    form['website_link'].data = artist.website
    form['facebook_link'].data = artist.facebook_link
    form['seeking_venue'].data = artist.seeking_venue
    form['seeking_description'].data = artist.seeking_description

    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    form = ArtistForm(request.form)
    artist = Artist.query.filter_by(id = artist_id).first()
    if form.validate():
        artist.name = request.form.get('name')
        artist.city = request.form.get('city')
        artist.state = request.form.get('state')
        artist.phone = request.form.get('phone')
        artist.image_link = request.form.get('image_link')
        artist.facebook_link = request.form.get('facebook_link')
        artist.website = request.form.get('website_link')
        artist.genres = request.form.getlist('genres')
        artist.seeking_venue = True if request.form.get('seeking_venue') is not None else False
        artist.seeking_description = request.form.get('seeking_description')
        
        db.session.commit()
        flash('Artist ' + artist.name + ' has been updated successfully.')
    else:
        # db.session.rollback()
        # flash('Artist ' + artist.name + ' could not be updated.')
        errors = form.errors
        for key in errors:
            flash(key + ' ' + errors[key][0])

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.filter_by(id = venue_id).first()
    form['name'].data = venue.name
    form['city'].data = venue.city
    form['state'].data = venue.state
    form['address'].data = venue.address
    form['phone'].data = venue.phone
    form['genres'].data = venue.genres
    form['image_link'].data = venue.image_link
    form['website_link'].data = venue.website
    form['facebook_link'].data = venue.facebook_link
    form['seeking_talent'].data = True if request.form.get('seeking_talent') is not None else False
    form['seeking_description'].data = venue.seeking_description

    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm(request.form)
    venue = Venue.query.filter_by(id = venue_id).first()
    if form.validate():
        venue.name = request.form.get('name')
        venue.city = request.form.get('city')
        venue.state = request.form.get('state')
        venue.address = request.form.get('address')
        venue.phone = request.form.get('phone')
        venue.image_link = request.form.get('image_link')
        venue.facebook_link = request.form.get('facebook_link')
        venue.website = request.form.get('website_link')
        venue.genres = request.form.getlist('genres')
        venue.seeking_talent = True if request.form.get('seeking_talent') is not None else False
        venue.seeking_description = request.form.get('seeking_description')
        
        db.session.commit()
        flash('Venue ' + venue.name + ' has been updated successfully.')
    else:
        # db.session.rollback()
        # flash('Venue ' + venue.name + ' could not be updated.')
        errors = form.errors
        for key in errors:
            flash(key + ' ' + errors[key][0])
        
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

    # on successful db insert, flash success
    # flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    error = False
    form = ArtistForm(request.form)
    if form.validate():
        try:
            name = request.form.get('name')
            city = request.form.get('city')
            state = request.form.get('state')
            phone = request.form.get('phone')
            genres = request.form.getlist('genres')
            facebook_link = request.form.get('facebook_link')
            image_link = request.form.get('image_link')
            website_link = request.form.get('website_link')
            seeking_venue = True if request.form.get('seeking_venue') is not None else False
            seeking_description = request.form.get('seeking_description')

            new_artist = Artist(
                name=name,
                city=city,
                state=state,
                phone=phone,
                genres=genres,
                facebook_link=facebook_link,
                image_link=image_link,
                website=website_link,
                seeking_venue=seeking_venue,
                seeking_description=seeking_description
            )
            db.session.add(new_artist)
            db.session.commit()
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
        
        if error:
            flash('An error occurred. Artist ' + name + ' could not be listed.')
            return redirect(url_for('create_artist_form', form=form))
        else:
            flash('Artist ' + name + ' was successfully listed!')
            return render_template('pages/home.html')
    else:
        errors = form.errors
        for key in errors:
            flash(key + ' ' + errors[key][0])
        return redirect(url_for('create_artist_form', form=form))
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    shows = Show.query.all()
    data = []
    for show in shows:
        data.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.isoformat()
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

    # on successful db insert, flash success
    # flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    form = ShowForm(request.form)
    error = False
    if form.validate():
        try:
            artist_id = request.form.get('artist_id')
            venue_id = request.form.get('venue_id')
            start_time = request.form.get('start_time')

            new_show = Show(
                venue_id = venue_id,
                artist_id = artist_id,
                start_time = start_time
            )
            db.session.add(new_show)
            db.session.commit()
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
        
        if error:
            flash('An error occurred. Show could not be listed.')
            return redirect(url_for('create_shows', form=form))
        else:
            flash('Show was successfully listed!')
            return render_template('pages/home.html')
    else:
        errors = form.errors
        for key in errors:
            flash(key + ' ' + errors[key][0])
        return redirect(url_for('create_shows', form=form))


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
    app.debug = True
    app.run(host='localhost', port=5000)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
