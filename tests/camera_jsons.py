
# test to NOT take buildings into account which are OUTSIDE the camera-triangle
# vertices are OUTSIDE triangle, but building clearly in view
CAMERA_BROODFABRIEK = """
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