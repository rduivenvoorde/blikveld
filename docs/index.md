
The class Blikveld and it's urn method takes a camera_json string parameter  
and optionally a camera_scale parameter (and for debugging purposes an context parameter).

The output is a geojson with 'Panden' as being returned from the 
'https://geodata.nationaalgeoregister.nl/bag/wfs/v1_1?' wfs service.


- web api

  - endpoints

  - query


- cli api

Settings: 
- pand of bebouwing 
- 

Return:
- actual number of returned objects 'numbersMatched'
- type of objects 'pand'
- actual features (of type x which are hit by camera) as (geojson) features
- metadata 

Meta (debug) info: 
- wfs url (in metdata)
- camera json
- 'scaled' value
- 'fetched': objects fetched with wfs url
- calculated 'hits' (both modi)
