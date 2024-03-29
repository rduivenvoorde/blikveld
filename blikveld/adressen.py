#!/usr/bin/env python3

# pip install geojson
import geojson  # https://pypi.org/project/geojson/
# pip install requests
import requests
from blikveld.exception import BlikVeldException

class Adressen:

    # BAG_VIEWER_URL https://bagviewer.kadaster.nl/lvbag/bag-viewer/api/bag/bevragen?objectIds=0392100000045923
    BAG_VIEWER_URL = 'https://bagviewer.kadaster.nl/lvbag/bag-viewer/api/bag/bevragen'  # ?objectIds=0392100000045927,0392100000045931

    # Bebouwing WFS
    KADASTER_BEBOUWING_WFS_URL = 'https://geodata.nationaalgeoregister.nl/bag/wfs/v1_1'  # depricated
    KADASTER_BEBOUWING_WFS_URL = 'https://service.pdok.nl/lv/bag/wfs/v2_0'
    KADASTER_BEBOUWING_WFS_TYPE = 'bag:verblijfsobject'
    KADASTER_BEBOUWING_WFS_TIMEOUT = 3

    def __init__(self):
        self.url = ''
        self.data = ''

    # def get_via_bagviewer(self, bag_ids_stringlist):
    #     '''
    #     See: https://geoforum.nl/t/manieren-om-op-basis-van-een-klein-lijstje-pand-ids-de-adressen-te-vinden/5238
    #     Apparently an unofficial way to retrieve Pand details, INCLUDING the addresses via a
    #     GET to the bagviewer:
    #       https://bagviewer.kadaster.nl/lvbag/bag-viewer/api/bag/bevragen?objectIds=0392100000045927,0392100000045931
    #
    #     :param bag_ids_list:
    #     :return:
    #     '''
    #
    #     params = {'objectIds': bag_ids_stringlist}
    #     response = requests.get(self.BAG_VIEWER_URL, params=params, timeout=10)
    #     print(response.url)
    #     if 200 != response.status_code:
    #         raise Exception(
    #             f'WFS url returned status {response.status_code}:\n{response.url}')
    #     pand_adressen = geojson.loads(response.text)
    #     return pand_adressen

    def get_via_bebouwing_wfs(self, bag_ids_stringlist):

        # http://geodata.nationaalgeoregister.nl/bag/wfs?service=wfs&version=2.0.0&request=GetFeature&typeName=bag:verblijfsobject&count=25&propertyName=bag:postcode,bag:woonplaats
        if len(bag_ids_stringlist) == 1:
            property_filter = f'<PropertyIsEqualTo><PropertyName>bag:pandidentificatie</PropertyName><Literal>{bag_ids_stringlist[0]}</Literal></PropertyIsEqualTo>'
        elif len(bag_ids_stringlist) > 1:
            property_filter = '<Or>'
            for bag_id in bag_ids_stringlist:
                property_filter = property_filter + f'<PropertyIsEqualTo><PropertyName>bag:pandidentificatie</PropertyName><Literal>{bag_id}</Literal></PropertyIsEqualTo>'
            property_filter = property_filter + '</Or>'
        elif len(bag_ids_stringlist) == 0:
            #raise BlikVeldException(f'Trying to find BAG adressen, but empty Pand list: {bag_ids_stringlist}')
            # RD 20211202 NOT raising exception, but returning an empty panden list
            return geojson.loads('{"type": "FeatureCollection", "features": []}')
        else:
            raise BlikVeldException(f'Something Wrong with the bag id parameters: {bag_ids_stringlist}')
        
        filter = f'<Filter>{property_filter}</Filter>'

        params = {
            'service': 'WFS',
            'request': 'GetFeature',
            'version': '2.0.0',
            'srsName': 'urn:ogc:def:crs:EPSG::4326',
            'outputFormat': 'application/json; subtype=geojson',  # service is VERY strict: 'application/json;subtype=geojson' (no space in between type;subtype) raises 400
            'typeNames': self.KADASTER_BEBOUWING_WFS_TYPE,
            'filter': filter
        }
        self.data = params

        # response = requests.get(self.KADASTER_BEBOUWING_WFS_URL, params=params, timeout=5)
        # if 200 != response.status_code:
        #     raise Exception(
        #         f'WFS url returned status {response.status_code}:\n{response.url}')

        from urllib3 import exceptions
        try:
            # 13 dec: adding close on header, after seeing: ResourceWarning: unclosed <ssl.SSLSocket fd=3, family=AddressFamily.AF_INET6, type=SocketKind.SOCK_STREAM, proto=6, laddr=('2a10:3781:52f:1:37e8:b7a7:506a:e978', 52898, 0, 0), raddr=('2001:67c:2f04:f300::123', 443, 0, 0)>
            # see: https://stackoverflow.com/questions/10115126/python-requests-close-http-connection
            req = requests.Request('POST', self.KADASTER_BEBOUWING_WFS_URL, data=params, headers={'Connection': 'close'})
            prepared = req.prepare()

            self.url = req.url
            self.data = params

            s = requests.Session()
            response = s.send(prepared, timeout=self.KADASTER_BEBOUWING_WFS_TIMEOUT)

            pand_adressen_geojson = geojson.loads(response.text)
        except exceptions.ReadTimeoutError:
            raise BlikVeldException(f'TimeOut Error in Fetching adressen via: {self.KADASTER_BEBOUWING_WFS_URL} TimeOut setting: {self.KADASTER_BEBOUWING_WFS_TIMEOUT}')
        except Exception as e:
            print(e)
            raise BlikVeldException(f'Error: {e}')

        return pand_adressen_geojson

if __name__ == '__main__':

    import json
    #result = Adressen().get_via_bagviewer(['0392100000045927','0392100000045931'])
    result = Adressen().get_via_bebouwing_wfs(['0392100000045861'])
    #result = Adressen().get_via_bebouwing_wfs(['0392100000045927','0392100000045931'])
    print(json.dumps(result, indent=4, sort_keys=True))


