import os

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_DATABASE_URI = "postgresql://akiolisa:aki12345@localhost/rsg_sdi"
ENGINE_DATABASE_URI = "postgresql://akiolisa@localhost" # TODO get the current localhost connection
SECRET_KEY = "\/xc3*%\/x8f\/x11\/xd5\/xab\/xd6%\/x91\/x15\/xa2\/xa2\/x1foh\/x98c\/xc8\/x88B\/xd1!\/x95"
UPLOAD_FOLDER = "/uploads"
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'shp', 'jpg', 'png', 'jpeg', 'tif', 'tiff', 'bmp', 'csv'}
