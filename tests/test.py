import unittest
import geojson
import blikveld
import camera_jsons

import webbrowser

class MyTestCase(unittest.TestCase):

    def geojson_check(self, geo_json, fetched, hits):
        result = geojson.loads(geo_json)
        self.assertEqual(result.type, 'FeatureCollection')
        self.assertTrue(result.is_valid)
        self.assertEqual(result.metadata['fetched'], fetched)
        self.assertEqual(result.metadata['hits'], hits)

    def show_in_browser(self, geo_json):
        #webbrowser.open("https://google.com")
        import urllib.parse
        result_json_encoded = urllib.parse.quote(geo_json)
        webbrowser.open(f'http://geojson.io/#data=data:application/json,{result_json_encoded }')

    def test_default_camera(self):
        result = blikveld.BlikVeld().run()
        self.geojson_check(result, 20, 12) # fetched=20, hits=12

    def test_broodfabriek_camera(self):
        result = blikveld.BlikVeld().run(camera_jsons.CAMERA_BROODFABRIEK)
        self.geojson_check(result, 1, 0)
        self.show_in_browser(result)



if __name__ == '__main__':
    unittest.main()
