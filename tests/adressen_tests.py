import unittest
import json

from blikveld.adressen import Adressen


class AdressenTests(unittest.TestCase):

    def test_import(self):
        from blikveld.adressen import Adressen
        import requests

    def test_get_request(self):
        #result = Adressen().get_via_bagviewer(['0392100000045927', '0392100000045931'])
        #print(result)

        result = Adressen().get_via_bebouwing_wfs(['0392100000045927', '0392100000045931'])
        self.assertEqual(len(result.features), 2)
        #print(json.dumps(result, indent=4, sort_keys=True))

if __name__ == '__main__':
    unittest.main()
