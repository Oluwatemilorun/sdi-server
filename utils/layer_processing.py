"""
Layer/Data processing module.

Contains all methods that help in processing of vector files and raster files.
This layers can be processed and stored in the accompaying database and can also be queried into single files

Layer types:
- ESRI Shapefile
- Raster Files
- Google KMZ/KML
- Comma Delimited Files (CSV)
"""

import os
import psycopg2
from psycopg2.sql import SQL, Identifier, Literal, Placeholder
import osgeo.ogr
from osgeo import ogr, osr, gdal
import shapely
import shapely.wkt
import geopandas as gpd
import config
import subprocess

# %matplotlib inline

def format_field_type(field_type):
	if field_type == 'Integer64':
		return 'BIGINT'
	elif field_type == 'Integer32' or field_type == 'Interger':
		return 'INTEGER'
	elif field_type == 'String':
		return 'VARCHAR'
	elif field_type == 'DateTime':
		return 'TIMESTAMP'
	else:
		return field_type.upper()

def get_geometry_type(layer):
	feature = layer.GetNextFeature()
	geometry = feature.GetGeometryRef()
	return geometry.GetGeometryName()
	# wkt = geometry.ExportToWkt()
	# return wkt.split(' ', 1)[0]


def save_shapefile_layer(file, database):
	filename = file.rsplit('.')[0].lower()
	file_extn = file.rsplit('.', 1)[1].lower()
	file = os.path.join(config.UPLOAD_FOLDER, database['name'], file)
	shapefile = ogr.Open(file)
	
	if not shapefile:
		print('unable to open shapefile => %s.%s' % (file, file_extn))
		return False, 'unable to open shapefile => %s.%s' % (file, file_extn)

	layer = shapefile.GetLayer()
	spatial_ref = layer.GetSpatialRef() # if no .prj file, None will returned
	
	# If .prj file is available.
	if spatial_ref:
		print('Detected .prj file for shapefile <%s>' % (filename))

		sr = osr.SpatialReference('%s' % spatial_ref)
		res = sr.AutoIdentifyEPSG()

		if res == 0:  # success
			SRID = int(sr.GetAuthorityCode(None))

		else:
			print('Could not determine SRID of <%s>.shp' % (filname))

	cmds = 'shp2pgsql -s %s -d -g %s -I -- %s public.%s | psql -d %s -U %s -p 5432' % (
		SRID if spatial_ref else 0,
		'geometry',
		file,
		filename,
		database['name'],
		database['user']
	)

	instance = subprocess.run(cmds, shell=True)

	try:
		instance.check_returncode()

	except Exception:
		return False, 'Error saving layer to database'
	
	else:
		return True, 'Success'



def save_raster_layer(file, database):

	filename = file.rsplit('.')[0].lower()
	file_extn = file.rsplit('.', 1)[1].lower()
	file = os.path.join(config.UPLOAD_FOLDER, database['name'], file)

	try:
		raster = gdal.Open(file)
		
	except RuntimeError as e:
		print('unable to open raster file => %s.%s' % (file, file_extn))
		print(e)
		return False, 'unable to open raster file => %s.%s' % (file, file_extn)
		
	
	proj = osr.SpatialReference(wkt=raster.GetProjection())
	projection = str(proj.GetAttrValue('AUTHORITY', 1))
	gt = raster.GetGeoTransform()
	pixelSizeX = str(round(gt[1]))
	pixelSizeY = str(round(-gt[5]))
	cmds = 'raster2pgsql -s %s -t auto -d -f %s -F -I -M -C -- %s public.%s | psql -d %s -U %s -p 5432' % (
		projection,
		'raster',
		file,
		filename,
		database['name'],
		database['user']
	)

	instance = subprocess.run(cmds, shell=True)

	try:
		instance.check_returncode()

	except Exception:
		return False, 'Error saving layer to database'

	else:
		return True, 'Success'


# ====================
# initial
def save_shapefile_layer_2(file, database):
	"""
	Process and save shapefiles into database. Before processing shapefiles, the associates files must be included.
	`shp`, `shx`, `dbf`

	:params :file: The shapefile to process `.shp`\n
	:params :database: The database to save layer
	```
		{
			"user": assignment['db_username'],
			"pass": assignment['db_password'],
			"name": assignment['db_name']
		}
	```
	"""

	filename = file.rsplit('.')[0].lower()
	file_extn = file.rsplit('.', 1)[1].lower()
	file = os.path.join(config.UPLOAD_FOLDER, database['name'], file)

	shapefile = ogr.Open(file)

	# layer = shapefile.GetLayerCount() #get all layers
	if not shapefile:
		print('unable to open shapefile => %s.shp' % (file))
		return False, 'unable to open shapefile <%s>.shp' % (filename)

	try:
		conn = psycopg2.connect(
			database=database['name'],
			user=config.DATABASE_USER,
			password=config.DATABASE_PASSWORD
		)

		cursor = conn.cursor()
		cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis;")

	except Exception as e:
		print(e)

		conn.rollback
		conn.close()
		return False, e

	cursor.execute("DROP TABLE IF EXISTS %s" % (filename))

	layer = shapefile.GetLayer()
	spatial_ref = layer.GetSpatialRef()  # if no .prj file, None will returned
	layer_definition = layer.GetLayerDefn()
	number_feature = layer.GetFeatureCount()
	number_fields = layer_definition.GetFieldCount()
	geometry_type = get_geometry_type(layer)
	fields = []
	coordTrans = None
	SRID = 0

	print(geometry_type)

	# If .prj file is available.
	if spatial_ref:
		print('Detected .prj file for shapefile <%s>' % (filename))

		sr = osr.SpatialReference('%s' % spatial_ref)
		res = sr.AutoIdentifyEPSG()

		if res == 0:  # success
			SRID = int(sr.GetAuthorityCode(None))

		else:
			print('Could not determine SRID of <%s>.shp' % (filname))

	for i in range(number_fields):
		fields_prop = {'name': '', 'type_code': '',
                 'type': '', 'width': '', 'precision': ''}
		fields_prop['name'] = layer_definition.GetFieldDefn(i).GetName()
		fields_prop['type_code'] = layer_definition.GetFieldDefn(i).GetType()
		fields_prop['type'] = layer_definition.GetFieldDefn(
			i).GetFieldTypeName(fields_prop['type_code'])
		fields_prop['width'] = layer_definition.GetFieldDefn(i).GetWidth()
		fields_prop['precision'] = layer_definition.GetFieldDefn(i).GetPrecision()

		fields.append(fields_prop)

	print("Creating new Table for <%s> with fields => %s" %
	      (filename, [a['name'] for a in fields]))

	fields_query = []
	for x in fields:
		if x['name'] == 'id':
			pass
		else:
			# TODO: set width and precision (for floats)
			fields_query.append(
				'%s %s' % (x['name'], format_field_type(x['type']))
			)

	# create table to hold layer data
	# TODO: check for GEOGRAPHY and GEOMETRY
	cursor.execute(
		SQL("CREATE TABLE {} (id SERIAL PRIMARY KEY, {}, outline GEOMETRY({}))").format(
			Identifier(filename),
			SQL(', ').join(map(SQL, fields_query)),
			Literal(geometry_type)
		) if len(fields_query) >= 1 else SQL("CREATE TABLE {} (id SERIAL PRIMARY KEY, outline GEOMETRY({}))").format(
			Identifier(filename),
			Literal(geometry_type)
		)
	)

	# create a spatial index for the outline field, which is necessary to make efficient spatial queries
	cursor.execute(
		SQL("CREATE INDEX {} ON {} USING GIST(outline)").format(
			Identifier('%s_index' % filename),
			Identifier(filename)
		)
	)

	conn.commit()

	# First delete the existing contents of this table in case we want to run the code multiple times.
	cursor.execute(
		SQL("DELETE FROM {}").format(Identifier(filename))
	)

	for feature in layer:
		feature_fields = [b['name'] for b in fields if b['name'].lower() != 'id']
		feature_values = [feature.GetField(x) for x in feature_fields]

		# Get feature geometry
		geometry = feature.GetGeometryRef()

		# Convert geometry to WKT format
		wkt = geometry.ExportToWkt()

		cursor.execute(
			SQL("INSERT INTO {} ({}, outline) VALUES ({}, ST_GeomFromText(%s))").format(
				Identifier(filename),
				SQL(', ').join(map(SQL, feature_fields)),
				SQL(', ').join(Placeholder() * len(feature_fields))
			), feature_values.__add__([wkt])
		)

	conn.commit()

	# Update the SRID of all features in a geometry column
	if spatial_ref:
		print('Updating SRID for <%s> with => %s' % (filename, SRID))
		try:
			cursor.execute(
				SQL("ALTER TABLE {} ALTER COLUMN {} TYPE geometry({}, 3857) USING ST_Transform(ST_SetSRID({}, {}), 3857)").format(
					Identifier(filename),
					Identifier('outline'),
					Literal(geometry_type),
					Identifier('outline'),
					Literal(SRID)
				)
			)

			conn.commit()

		except psycopg2.ProgrammingError:
			conn.rollback

	# manipulate the spatial database and add a new geography that will hold the centroid value.
	# This will be done so we can later make a query based on centroid location.
	try:
		cursor.execute(
			SQL("ALTER TABLE {} ADD COLUMN centroid GEOMETRY").format(Identifier(filename))
		)

	except psycopg2.ProgrammingError:
		conn.rollback

	cursor.execute(
		SQL("UPDATE {} SET centroid=ST_Centroid(outline::geometry)").format(
			Identifier(filename))
	)

	conn.commit()
	conn.close()

	return True, 'Success'


def reproject_shapefile_layer(shapefile, inSRID, outSRID):

	return None


