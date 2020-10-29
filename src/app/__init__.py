from flask import Flask
from flask import request
from flask import render_template

from blikveld.blikveld import BlikVeld
#from blikveld import BlikVeld

app = Flask(__name__)


#Thinking about api's here:
# /         html page with entrypoints/examples
# /camera   GET input form POST result html page
# /api      GET help page (OR also working) POST retrieve geojson (of camera, all panden and blikveld panden)
# ??


# @app.route('/')
# def run():
#     return 'ok'

@app.route('/blikveld')
def blikveld():
    return BlikVeld().run()

@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)

@app.route('/')
@app.route('/camera', methods=['POST', 'GET'])
def camera():
    if request.method == 'POST':
        camera_json = request.form['camera_json']
        camera_scale = float(request.form['camera_scale'])
        result_json = BlikVeld().run(camera_json, camera_scale)
        import urllib.parse
        result_json_encoded = urllib.parse.quote(result_json)
        return render_template('result.html', result_json=result_json, result_json_encoded=result_json_encoded)
    else:
        return render_template('camera.html')
