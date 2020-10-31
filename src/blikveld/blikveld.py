#!/usr/bin/env python3

# pip install geojson
import geojson  # https://pypi.org/project/geojson/
# pip install requests
import requests

import shapely.geometry
import shapely.affinity
from shapely.prepared import prep
from shapely.geometry import Point

# Camera in Atjestraat:
# kijkhoek/sector 39 graden
# bearing: 31 graden
CAMERA_JSON = """
{
  "type": "Feature",
  "properties": {
    "angle": 38.876645504061116,
    "bearing": 31.979981482645943,
    "distance": 87.9921646359149
  },
  "geometry": {
    "type": "GeometryCollection",
    "geometries": [
      {
        "type": "Point",
        "coordinates": [
          4.646878838539124,
          52.3969167956431
        ]
      },
      {
        "type": "LineString",
        "coordinates": [
          [
            4.647177386477727,
            52.39773567907421
          ],
          [
            4.647953579015309,
            52.39743995473123
          ]
        ]
      }
    ]
  }
}
"""
CAMERA_JSON = """
{
  "type": "Feature",
  "properties": {
    "angle": 18.01908757241881,
    "bearing": 102.81261738101036,
    "distance": 103.44202097484239
  },
  "geometry": {
    "type": "GeometryCollection",
    "geometries": [
      {
        "type": "Point",
        "coordinates": [
          4.647431373596192,
          52.391106301345005
        ]
      },
      {
        "type": "LineString",
        "coordinates": [
          [
            4.648970904909532,
            52.39104383732581
          ],
          [
            4.648863730220486,
            52.390756273966716
          ]
        ]
      }
    ]
  }
}
"""

class BlikVeldException(BaseException):
    pass

class BlikVeld:

    def run(self, camera_json=None, camera_scale=1):

        if not camera_json:
            camera_json = CAMERA_JSON

        # input is a camera json
        camera = geojson.loads(camera_json)
        #print(camera)

        if not ('geometry' in camera and 'geometries' in camera['geometry']):
            raise BlikVeldException('Camera json should be valid geojson, and have a "geometry" with two "geometries" ')
            return

        view_point = None
        horizon = None
        for geom in camera['geometry']['geometries']:
            gtype = geom['type'].lower()
            if gtype == 'point':
                view_point = geom
            elif gtype == 'linestring':
                horizon = geom
            else:
                raise BlikVeldException('Unknown geometry type in camera json')

        # {"coordinates": [4.646879, 52.396917], "type": "Point"} {"coordinates": [[4.647177, 52.397736], [4.647954, 52.39744]], "type": "LineString"}
        #print(view_point['coordinates'], horizon['coordinates'])
        # create one 3-point LineString from both geometries
        coords = list(horizon['coordinates'])  # create a copy to not update the original
        coords.insert(0, view_point['coordinates'])
        coords.append(view_point['coordinates'])
        # now create a proper geojson.Feature from it
        camera_triangle = geojson.Polygon([coords])
        # and a Feature from that
        camera_feature = geojson.Feature(geometry=camera_triangle, properties={'name': 'camera'})

        # to resize the camera-triangle we use shapely.affinity.scale
        # but NOTE that untill now we work with geojson-geoms so we need to juggle these to shapely-geoms...
        resized_camera_triangle = shapely.affinity.scale(
                shapely.geometry.shape(camera_triangle),
                xfact=camera_scale, yfact=camera_scale, origin=shapely.geometry.shape(view_point))
        resized_camera_feature = geojson.Feature(geometry=geojson.Polygon([list(resized_camera_triangle.exterior.coords)]), properties={'name': 'camera_resized'})

        #fc = geojson.FeatureCollection([camera_feature])
        #print(geojson.dumps(fc))

        #print(geojson.dumps(camera_feature))
        # some magic to create the posList we use in the gml
        # WFS2: Y X instead of X Y !!
        # normal camera
        #poslist = ' '.join(f'{i[1]} {i[0]}' for i in coords)
        # resized camera
        poslist = ' '.join(f'{i[1]} {i[0]}' for i in list(resized_camera_triangle.exterior.coords))


        # ARGH!!!! owslib does not do spatial filtering !!! https://github.com/geopython/OWSLib/issues/128
        # we COULD do with bbox, but ...
        # from owslib.wfs import WebFeatureService
        # from owslib.etree import etree
        # from owslib.fes import Prop
        # pdok_wfs = WebFeatureService(url='https://geodata.nationaalgeoregister.nl/kadastralekaart/wfs/v4_0', version='2.0.0')
        # filter = PropertyIsLike(propertyname='bez_gem', literal='Ingolstadt', wildCard='*')
        # response = pdok_wfs.getfeature(typename='kadastralekaartv4:bebouwing', filter=)

        # BAG WFS
        wfs_url = 'https://geodata.nationaalgeoregister.nl/bag/wfs/v1_1?'
        wfs_type = 'bag:pand'
        wfs_timout = 1.5  # bag endpoint is fast!!

        # kadastrale kaart WFS
        # wfs_url = 'https://geodata.nationaalgeoregister.nl/kadastralekaart/wfs/v4_0?'
        # wfs_type = 'kadastralekaartv4:bebouwing'
        # wfs_timout = 5  # kadastralekaart endpoint is NOT fast!!

        #spatial_filter = f'<Filter><Intersects> <PropertyName>Geometry</PropertyName><gml:Polygon srsName="urn:ogc:def:crs:EPSG::4326"><gml:exterior><gml:LinearRing><gml:posList>52.397328 4.647181 52.397753 4.648073 52.397237 4.648182 52.397328 4.647181</gml:posList></gml:LinearRing></gml:exterior></gml:Polygon></Intersects></Filter>'
        spatial_filter = f'<Filter><Intersects>' \
                         f'<PropertyName>Geometry</PropertyName>' \
                         f'<gml:Polygon srsName="urn:ogc:def:crs:EPSG::4326">' \
                         f'<gml:exterior><gml:LinearRing><gml:posList>' \
                         f'{poslist}' \
                         f'</gml:posList></gml:LinearRing></gml:exterior>' \
                         f'</gml:Polygon></Intersects></Filter>'
        params = {
            'service': 'WFS',
            'request': 'GetFeature',
            'version': '2.0.0',
            'srsName': 'urn:ogc:def:crs:EPSG::4326',
            'outputFormat': 'application/json; subtype=geojson',  # service is VERY strict: 'application/json;subtype=geojson' (no space in between type;subtype) raises 400
            'typeNames': wfs_type,
            'filter': spatial_filter
        }

        DEV = False

        if DEV:
            with open('/tmp/panden.json', 'r') as f:
                panden = geojson.load(f)
        else:
            r = requests.get(wfs_url, params=params, timeout=wfs_timout)
            if 200 != r.status_code:
                raise BlikVeldException(f'WFS url returned status {r.status_code}:\n{r.url}')
            #print(r.url)
            panden = geojson.loads(r.text)
            panden['metadata'] = {'fetched': len(panden.features)}
            #with open('/tmp/panden.json', 'w') as f:
            #    geojson.dump(panden, f, indent=2)
            #print(f'Found {len(panden["features"])} panden with camera json')

        # insert both original camera and resized camera into the panden(result)
        panden.features.insert(0, camera_feature)
        panden.features.insert(0, resized_camera_feature)

        # 2 scenario's:
        # -1- for every pand/polygon get the coordinates, create a line from viewpoint to coordinate, and create a list of polygons which do NOT cross another polygon
        # -2- within the 'view triangle' create 'beams' (per 1 (0.5) degree) and see which polygon crosses and add the nearest to viewpoint to the list

        # so panden is a (geojson)FeatureCollection object (! not a dict)

        view_point = shapely.geometry.shape(view_point)

        # first create a dict of feature_identification -> shapely polygons
        shape_dict = {}
        for centroid_feature in panden.features:
            if not 'bouwjaar' in centroid_feature.properties:
                continue
            shape_dict[centroid_feature.properties['gid']] = shapely.geometry.shape(centroid_feature.geometry)
        i = 0
        result = []
        for pand_id, pand_geom in shape_dict.items():
            # if i == 4:
            #     break
            # i += 1
            # print(pand_geom)
            for vertex in pand_geom.exterior.coords:
                # only vertices WITHIN the camera triangle
                if not resized_camera_triangle.contains(shapely.geometry.Point(vertex)):
                    continue
                #print(vertex, view_point.coords[0])
                line = shapely.geometry.LineString([vertex, view_point.coords[0]])

                prepared_line = shapely.prepared.prep(line)
                hits = list(filter(prepared_line.crosses, shape_dict.values()))
                #print(len(hits))
                if len(hits) == 0:
                    # this means that THIS line of sight of:
                    # - viewpoint TO vertex
                    # did NOT cross another pand, meaning:
                    # the pand with this vertex is probably in sight from the viewpoint
                    # print(f'Adding {pand_id} to the results')
                    centroid = pand_geom.centroid  # returns a geojson.Point
                    centroid_feature = geojson.feature.Feature(geometry=centroid, properties={'id': pand_id})
                    result.append(centroid_feature)
                    break

        panden['metadata'].update({'hits': len(result), 'scaled': camera_scale, 'camera': camera})
        for centroid_feature in result:
            panden.features.insert(0, centroid_feature)

        #with open('/tmp/pandenresult.json', 'w') as f:
        #    geojson.dump(panden, f, indent=2)

        return geojson.dumps(panden)


if __name__ == '__main__':
    BlikVeld().run()