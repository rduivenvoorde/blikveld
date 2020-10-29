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


