
import unittest
import geojson
import webbrowser
import camera_jsons

from blikveld.camera import BlikVeld

class MyTestCase(unittest.TestCase):

    def geojson_check(self, geo_json, fetched, hits):
        result = geojson.loads(geo_json)
        self.assertEqual(result.type, 'FeatureCollection')
        self.assertTrue(result.is_valid)
        self.assertEqual(result.metadata['fetched'], fetched)
        self.assertEqual(result.metadata['hits'], hits)

    def show_in_browser(self, geo_json):
        import urllib.parse
        result_json_encoded = urllib.parse.quote(geo_json)
        webbrowser.open(f'http://geojson.io/#data=data:application/json,{result_json_encoded }')

    def test_requests_url(self):
        import requests
        response = requests.get('https://duif.net')
        self.assertEqual(response.status_code, 200)
        get_url = 'https://geodata.nationaalgeoregister.nl/bag/wfs/v1_1?service=WFS&request=GetFeature&version=2.0.0&srsName=urn%3Aogc%3Adef%3Acrs%3AEPSG%3A%3A4326&outputFormat=application%2Fjson%3B+subtype%3Dgeojson&typeNames=bag%3Averblijfsobject&filter=%3CFilter%3E%3CPropertyIsEqualTo%3E%3CPropertyName%3Ebag%3Apandidentificatie%3C%2FPropertyName%3E%3CLiteral%3E0392100000045861%3C%2FLiteral%3E%3C%2FPropertyIsEqualTo%3E%3C%2FFilter%3E'
        response = requests.get(get_url, timeout=1)
        self.assertEqual(response.status_code, 200)

        # see https://stackoverflow.com/questions/20658572/python-requests-print-entire-http-request-raw
        req = requests.Request('GET', get_url)
        prepared = req.prepare()
        print(req.url)
        s = requests.Session()
        response = s.send(prepared, timeout=1)
        self.assertEqual(response.status_code, 200)

    def test_default_camera(self):
        result = BlikVeld().run()
        self.geojson_check(result, 20, 12)  # fetched=20, hits=12

    def test_broodfabriek_camera(self):
        result = BlikVeld().run(camera_jsons.CAMERA_BROODFABRIEK)
        self.geojson_check(result, 1, 1)

if __name__ == '__main__':
    unittest.main()
