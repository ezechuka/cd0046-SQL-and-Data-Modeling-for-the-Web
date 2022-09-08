import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
<<<<<<< HEAD
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:1234@localhost:5432/fyyur'
=======
SQLALCHEMY_DATABASE_URI = '<Put your local database url>'
>>>>>>> 6675e948bf372781037e377c390d2a807b1cf498
