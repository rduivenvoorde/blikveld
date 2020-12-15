# blikveld
Flask Api to retrieve BAG panden within 'view' of a camera-standpoint

http://spacetime.nypl.org/Leaflet.GeotagPhoto/examples/camera.html

INSTALL

Create virtual env (only first time) here: ``python3 -m venv venv``

Activate it: ``source venv/bin/activate`` (everytime you want to work in it)

Populate venv with modules used: ``pip install -r REQUIREMENTS.txt``

Start Flask from within src dir (see: https://flask.palletsprojects.com/)

```
# cd into the src dir
cd src
# now:
export FLASK_APP=app
# if you want development mode (auto reload when editing)
export FLASK_ENV=development  
flask run
* Running on http://127.0.0.1:5000/
```

Now in your browser go to http://127.0.0.1:5000/ or http://127.0.0.1:5000/camera


Wishlist:

- extra filters (like bouwjaar)
- wsgi script
- check inputs (maximize size of camera triangle, resize-factor, camera json, result set etc)
- output formats (FULL, result-panden, result-centroids (with/without camera etcetc))
- switch between BAG and Kadastrale kaart
- implement 'beam'-scenario
- only take vertices into account actually in camera-triangle
- index input page with camera-widget


DEVELOPMENT

Debugging in PyCharm

- DO NOT add 'quicker debugging by using cpython' to the project, else: 
  if you see this: Connection to Python debugger failed: Socket closed  https://intellij-support.jetbrains.com/hc/en-us/community/posts/360009880699-Can-t-run-Debugger-Connection-to-Python-debugger-failed-Socket-closed-
  PYDEVD_USE_CYTHON=NO
  
- on Debian: use required modules from Debian itself instead of installing them from pip (for development)





