#!/usr/bin/env python3

# pip install requests
import requests
import math
import webbrowser
# pip install shapely
import shapely.geometry
import shapely.affinity
import shapely.ops

# pip install geojson
import geojson  # https://pypi.org/project/geojson/

from blikveld import adressen

class BlikVeld:

    MIN_CAMERA_SCALE = 0.5
    MAX_CAMERA_SCALE = 5

    OUTPUT_ADRES_PUNTEN = 0
    OUTPUT_PAND_VLAKKEN = 1
    OUTPUT_PAND_PUNTEN = 2

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

    def show_in_geojson_io(self, geo_json):
        import urllib.parse
        result_json_encoded = urllib.parse.quote(geo_json)
        webbrowser.open(f'http://geojson.io/#data=data:application/json,{result_json_encoded }')

    def show_in_browser(self, geo_json):
        import tempfile
        fp = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        fp.write(bytes(geo_json, 'utf-8'))
        fp.close()
        webbrowser.open(fp.name)

    def show_in_qgis(self, geo_json):

        #import tempfile
        #fp = tempfile.NamedTemporaryFile(suffix='.json', delete=False)

        import pathlib
        f = pathlib.Path(__file__).parent.absolute()
        print(f)

        ff = f.joinpath('result.json')
        print(ff)
        fp = open(ff, 'bw')
        fp.write(bytes(geo_json, 'utf-8'))
        fp.close()

        import subprocess
        #subprocess.run(['qgis', fp.name])  # note that his will NOT return untill you quit QGIS (set askToSaveMemoryLayers to False in QGIS to quickly quit)!!
        subprocess.run(['qgis', f.joinpath('qgisproject.qgz')])  # note that his will NOT return untill you quit QGIS (set askToSaveMemoryLayers to False in QGIS to quickly quit)!!

    def azimuth_points(self, point1, point2):
        """azimuth between 2 shapely points """
        angle = math.atan2(point2.x - point1.x, point2.y - point1.y)
        # return math.degrees(angle) if angle>0 else math.degrees(angle) + 180
        return math.degrees(angle) % 360

    def azimuth(self, linestring):
        """azimuth of 1 shapely LineSting """
        point1 = shapely.geometry.Point(linestring.coords[0])
        point2 = shapely.geometry.Point(linestring.coords[1])
        return self.azimuth_points(point1, point2)

    def run(self,
            camera_json=None,
            camera_scale=1,

            use_bag_panden=True,
            use_kadaster_bebouwing=False,

            method_vertex=True,
            method_beam=True,

            output=OUTPUT_ADRES_PUNTEN,    # BlikVeld.OUTPUT_ADRES_PUNTEN=0 BlikVeld.OUTPUT_PAND_VLAKKEN=1 BlikVeld.OUTPUT_PAND_PUNTEN=2

            show_input=False,
            show_cameras=False,

            show_debug=False,  # if TRUE ALL debug features will be returned in result

            show_vertex_debug=False,  # if TRUE ALL 4 debug features below will be returned
            show_vertex_handled_vertex=False,  # vertex_handled_vertex
            show_vertex_viewpoint_line=False,  # vertex_viewpoint_line
            show_vertex_vertex_hit=False,  # vertex_vertex_hit
            show_vertex_viewpoint_line_hit=False,  # vertex_viewpoint_line_hit

            beams=100,  # number of 'beams'
            show_beam_debug=False,  # if TRUE ALL 4 debug features below will be returned
            show_beam_beams=False,  # beam
            show_beam_intersection_linestring=False,  # beam_intersection_linestring
            show_beam_intersection_nearest_point=False,  # beam_nearest_intersection_point
            show_beam_intersection_point=False  # beam_intersection_point
            ):

        if not camera_json:
            camera_json = self.CAMERA_JSON

        # input is a camera json
        camera = geojson.loads(camera_json)
        #print(camera)

        from blikveld import exception

        if not ('geometry' in camera and 'geometries' in camera['geometry']):
            raise exception.BlikVeldException('Camera json should be valid geojson, and have a "geometry" with two "geometries" ')

        if beams > 100.0 or beams < 1.0:
            raise exception.BlikVeldException('Number of beams should be between 1 and 100 (inclusive)')

        if not method_vertex and not method_beam:
            raise exception.BlikVeldException(f'At least one of the methods should be used: method_vertex (now: {method_vertex}) or method_beam (now: {method_beam})')

        if use_bag_panden and use_kadaster_bebouwing:
            raise exception.BlikVeldException(f'Use one dataset at a time, either Bag-panden (use_bag_panden is now {use_bag_panden}), or Kadadstralekaart-bebouwing (use_kadaster_bebouwing is now {use_kadaster_bebouwing})')

        if camera_scale < self.MIN_CAMERA_SCALE or camera_scale > self.MAX_CAMERA_SCALE:
            raise exception.BlikVeldException(f'Factor "camera_scale"={camera_scale} which is not in range {self.MIN_CAMERA_SCALE} <= camers_scale <= {self.MAX_CAMERA_SCALE}')

        if show_debug:
            show_vertex_debug = True
            show_beam_debug = True

        if show_vertex_debug:
            show_vertex_handled_vertex = True
            show_vertex_viewpoint_line = True
            show_vertex_vertex_hit = True
            show_vertex_viewpoint_line_hit = True

        if show_beam_debug:
            show_beam_beams = True
            show_beam_intersection_linestring = True
            show_beam_intersection_nearest_point = True
            show_beam_intersection_point = True

        view_point = None
        horizon = None
        for geom in camera['geometry']['geometries']:
            gtype = geom['type'].lower()
            if gtype == 'point':
                view_point = geom
            elif gtype == 'linestring':
                horizon = geom
            else:
                raise exception.BlikVeldException('Unknown geometry type in camera json')

        # {"coordinates": [4.646879, 52.396917], "type": "Point"} {"coordinates": [[4.647177, 52.397736], [4.647954, 52.39744]], "type": "LineString"}
        #print(view_point['coordinates'], horizon['coordinates'])
        # create one 3-point LineString from both geometries
        coords = list(horizon['coordinates'])  # create a copy to not update the original
        coords.insert(0, view_point['coordinates'])
        coords.append(view_point['coordinates'])
        # now create a proper geojson.Feature from it
        camera_triangle = geojson.Polygon([coords])
        # and a Feature from that
        camera_feature = geojson.Feature(geometry=camera_triangle, properties={'blikveld_type': 'camera'})

        # to resize the camera-triangle we use shapely.affinity.scale
        # but NOTE that until now we work with geojson-geoms so we need to juggle these to shapely-geoms...
        resized_camera_triangle = shapely.affinity.scale(
                shapely.geometry.shape(camera_triangle),
                xfact=camera_scale, yfact=camera_scale, origin=shapely.geometry.shape(view_point))
        resized_camera_feature = geojson.Feature(geometry=geojson.Polygon([list(resized_camera_triangle.exterior.coords)]), properties={'blikveld_type': 'camera_resized'})

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

        if use_kadaster_bebouwing:
            # kadastrale kaart WFS
            wfs_url = 'https://geodata.nationaalgeoregister.nl/kadastralekaart/wfs/v4_0?'
            wfs_type = 'kadastralekaartv4:bebouwing'
            wfs_timout = 5  # kadastralekaart endpoint is NOT fast!!
        else:  # DEFAULT TO:
            # BAG WFS
            wfs_url = 'https://geodata.nationaalgeoregister.nl/bag/wfs/v1_1?'
            wfs_type = 'bag:pand'
            wfs_timout = 2.5  # bag endpoint is fast!!

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
        source_url = 'development-json'
        if DEV:
            # with open('/tmp/panden.json', 'r') as f:
            #     input_feature_collection = geojson.load(f)
            import tests.panden_jsons
            input_feature_collection = geojson.loads(tests.panden_jsons.PANDEN)
        else:
            response = requests.get(wfs_url, params=params, timeout=wfs_timout)
            if 200 != response.status_code:
                raise exception.BlikVeldException(f'WFS url returned status {response.status_code}:\n{response.url}')
            #print(r.url)
            input_feature_collection = geojson.loads(response.text)
            source_url = response.url

        feature_collection = geojson.FeatureCollection([])
        metadata = {
            'show_input': show_input,
            'show_cameras': show_cameras,
            'method_vertex': method_vertex,
            'method_beam': method_beam,
            'use_bag_panden': use_bag_panden,
            'use_kadaster_bebouwing': use_kadaster_bebouwing,
            'wfs_panden_url': source_url,
            'panden_fetched': len(input_feature_collection.features)
        }


        # below can be use during development to see/use a specific panden json
        # with open('/tmp/panden.json', 'w') as f:
        #     geojson.dump(feature_collection, f, indent=2)


        # 2 methods/scenario's:
        # -1- method_vertex: for every pand/polygon get the coordinates,
        #      create a line from viewpoint to coordinate/vertex of the polygon,
        #      and create the list of polygons whose viewpoint lines do NOT cross other polygons
        # -2- method_beam: within the 'view/camera triangle' create 'beams' (per 1 (0.5) degree)
        #      going from view/standpoint to camera-horizon and
        #      check which polygon cross these beams and then only add the nearest polygon to viewpoint to the result list

        # so feature_collection is a (geojson)FeatureCollection object (! not a dict)

        # first create a dict (geoms), of feature_identification -> shapely polygons
        shapely_dict = {}
        # also create a feature dict to be able to easily retrieve a feature based on it's id
        feature_dict = {}
        for feature in input_feature_collection.features:
            # filter out camera feature here
            if 'blikveld_type' in feature.properties and feature.properties['blikveld_type'] in ('camera', 'camera_resized'):
                continue
            if 'gid' in feature.properties:  # BAG
                shapely_dict[feature.properties['gid']] = shapely.geometry.shape(feature.geometry)
                feature_dict[feature.properties['gid']] = feature
            elif hasattr(feature, 'id'):  # BEBOUWING
                shapely_dict[feature.id] = shapely.geometry.shape(feature.geometry)
                feature_dict[feature.id] = feature
            else:
                raise exception.BlikVeldException(f'WFS url returned features without known primary key (tried "id" and "gid")')

        result_dict = {}

        if method_vertex:
            for object_id, object_geom in shapely_dict.items():
                for vertex in object_geom.exterior.coords:
                    # only vertices WITHIN the camera triangle
                    if not resized_camera_triangle.contains(shapely.geometry.Point(vertex)):
                        continue

                    if show_vertex_handled_vertex:
                        feature_collection.features.insert(0, geojson.feature.Feature(geometry=geojson.Point(vertex), properties={'id': f'{object_id}', 'blikveld_type': 'vertex_handled_vertex'}))
                    line = shapely.geometry.LineString([vertex, view_point.coordinates])
                    if show_vertex_viewpoint_line:
                        feature_collection.features.insert(0, geojson.feature.Feature(geometry=line, properties={'id': f'{object_id}', 'blikveld_type': 'vertex_viewpoint_line'}))
                    prepared_line = shapely.prepared.prep(line)
                    hits = list(filter(prepared_line.crosses, shapely_dict.values()))
                    #print(len(hits))
                    if len(hits) == 0:
                        # this means that THIS line of sight of:
                        # - viewpoint TO vertex
                        # did NOT cross another pand, meaning:
                        # the pand with this vertex is probably in sight from the viewpoint
                        if show_vertex_vertex_hit:
                            feature_collection.features.insert(0, geojson.feature.Feature(geometry=geojson.Point(vertex), properties={'id': f'{object_id}', 'blikveld_type': 'vertex_vertex_hit'}))
                        if show_vertex_viewpoint_line_hit:
                            feature_collection.features.insert(0, geojson.feature.Feature(geometry=line, properties={'id': f'{object_id}', 'blikveld_type': 'vertex_viewpoint_line_hit'}))
                        result_dict[object_id] = feature_dict[object_id]
                        break

        if method_beam:
            horizon = shapely.geometry.LineString([horizon['coordinates'][0], horizon['coordinates'][1]])
            #for part in range(2, 100, 2):  # 50 beams
            #for part in range(2, 100, 4):  # test 25 beams
            #for part in range(10,  100, 30):  # test
            step = math.floor(100/beams)
            for part in range(1, 100, step):
                # get a portion of the horizon
                part_horizon = shapely.ops.substring(horizon, 0, part/100, True)
                # create a beam between viewpoint and second coordinate of the horizon
                beam = shapely.geometry.LineString([view_point['coordinates'], part_horizon.coords[1]])
                if camera_scale != 1.00:
                    beam = shapely.affinity.scale(
                        shapely.geometry.shape(beam),
                        xfact=camera_scale, yfact=camera_scale,
                        origin=shapely.geometry.shape(view_point))
                if show_beam_beams:
                    feature_collection.features.insert(0, geojson.feature.Feature(geometry=beam, properties={'id': f'{part}/100', 'blikveld_type': 'beam'}))

                # for every beam look which polygons are crossing
                # BUT only select the nearest!! to the viewpoint !!
                nearest_length = 10e10
                nearest_object_id = None
                nearest_intersection = None
                for object_id, object_geom in shapely_dict.items():
                    if not beam.intersection(object_geom).is_empty and object_geom.is_valid:  # WE ONLY HANDLE VALID GEOMS, ELSE YOU GET FALSE POSITIVES...
                        intersections = beam.intersection(object_geom)

                        # show_intersection_beams : show the intersecting geometries (linestrings)
                        if show_beam_intersection_linestring:
                            feature_collection.features.insert(0, geojson.feature.Feature(geometry=intersections, properties={'id': object_id, 'blikveld_type': 'beam_intersection_linestring'}))

                        if intersections.type == 'MultiLineString':
                            # testing here to be able to filter out those, as OTHERS should be wrapped in a list
                            # print(intersections)
                            pass
                        else:
                            intersections = [intersections]  # pack a single linestring in a list to be able to walk over it
                        for intersection_linestring in intersections:
                            for intersection in intersection_linestring.coords:
                                intersection_point_feature = geojson.feature.Feature(geometry=geojson.geometry.Point(intersection), properties={'id': object_id, 'blikveld_type': 'beam_intersection_point'})
                                if show_beam_intersection_point:
                                    feature_collection.features.insert(0, intersection_point_feature)
                                # create a length_line between viewpoint and intersection point
                                length_line = shapely.geometry.LineString([view_point['coordinates'], intersection])
                                beam_length = length_line.length
                                if beam_length < nearest_length:
                                    nearest_length = beam_length
                                    nearest_object_id = object_id
                                    nearest_intersection = intersection_point_feature

                # OK, all intersections of this beam handled...
                if nearest_object_id:
                    result_dict[nearest_object_id] = feature_dict[nearest_object_id]
                    if show_beam_intersection_nearest_point:
                        nearest_intersection.properties['blikveld_type'] = 'beam_nearest_intersection_point'
                        feature_collection.features.insert(0, nearest_intersection)

        metadata.update({'panden_hits': len(result_dict.keys()), 'scaled': camera_scale, 'camera': camera})

        # IF asked for result centroid, ONLY sent the feature centroids
        if output == self.OUTPUT_PAND_PUNTEN:
            metadata.update({'output': 'OUTPUT_PAND_PUNTEN'})
            for object_id in result_dict:
                # create a new centroid feature WITH the properties of the original feature
                centroid = shapely_dict[object_id].centroid  # returns a geojson.Point
                properties = dict(result_dict[object_id].properties)
                properties['blikveld_type'] = 'result_feature_centroid'
                centroid_feature = geojson.feature.Feature(geometry=centroid, properties=properties)
                feature_collection.features.insert(0, centroid_feature)
        elif output == self.OUTPUT_ADRES_PUNTEN:  # defaulting to: BlikVeld.OUTPUT_ADRES_PUNTEN
            ids = []
            for object_id in result_dict.keys():
                ids.append(feature_dict[object_id].properties['identificatie'])
            geojson_adressen = adressen.Adressen().get_via_bebouwing_wfs(ids)
            for feature in geojson_adressen.features:
                feature.properties['blikveld_type'] = 'result_adres_verblijfsobject'
                feature_collection.features.insert(0, feature)
            metadata.update({'adressen_hits': len(geojson_adressen.features), 'output': 'OUTPUT_ADRES_PUNTEN'})

        if output == self.OUTPUT_PAND_VLAKKEN:  # TODO: or debug !!
            # sent back the result features (polygons)
            metadata.update({'output': 'OUTPUT_PAND_VLAKKEN'})
            for object_id in result_dict:
                feature = result_dict[object_id]
                feature.properties['blikveld_type'] = 'result_pand'
                feature_collection.features.insert(0, feature)

        # add both original camera and resized camera to the feature_collection(result)
        if show_cameras:
            feature_collection.features.insert(0, camera_feature)
            if camera_scale != 1.00:
                feature_collection.features.insert(0, resized_camera_feature)

        # optional: add input (original camera features)
        if show_input:
            for feature in input_feature_collection.features:
                properties = dict(feature.properties)
                properties['blikveld_type'] = 'input_feature'
                f = geojson.feature.Feature(geometry=feature.geometry, properties=properties)
                feature_collection.features.insert(0, f)

        feature_collection['metadata'] = metadata
        return geojson.dumps(feature_collection)

if __name__ == '__main__':
    b = BlikVeld()
    #r = b.run()
    r = b.run(camera_json=None,
              camera_scale=1.3,

              use_bag_panden=True,
              use_kadaster_bebouwing=False,

              method_vertex=True,
              method_beam=True,

              output=BlikVeld.OUTPUT_ADRES_PUNTEN,

              show_input=True,
              show_cameras=True,

              show_debug=True,

              show_vertex_debug=True,  # if TRUE ALL 4 debug features below will be returned
              show_vertex_handled_vertex=True,             # vertex_handled_vertex
              show_vertex_viewpoint_line=True,             # vertex_viewpoint_line
              show_vertex_vertex_hit=True,                 # vertex_vertex_hit
              show_vertex_viewpoint_line_hit=True,         # vertex_viewpoint_line_hit

              beams=50,  # number of 'beams'
              show_beam_debug=True,  # if TRUE ALL 4 debug features below will be returned
              show_beam_beams=False,                       # beam
              show_beam_intersection_linestring=False,     # beam_intersection_linestring
              show_beam_intersection_nearest_point=False,  # beam_nearest_intersection_point
              show_beam_intersection_point=False           # beam_intersection_point
              )
    feature_collection = geojson.loads(r)
    #print(feature_collection.metadata)
    #b.show_in_browser(r)
    #b.show_in_geojson_io(r)
    b.show_in_qgis(r)
