from flask import Flask
from flask import request
from flask import render_template

from blikveld.blikveld import BlikVeld

app = Flask(__name__)


# Thinking about api's here:
# /         html page with entrypoints/examples
# /camera   GET input form POST result html page
# /api      GET help page (OR also working) POST retrieve geojson (of camera, all panden and blikveld panden)
# ??


@app.route('/')
def run():
    return render_template('index.html')


@app.route('/blikveld')
def blikveld():
    return BlikVeld().run()


@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)


# http://127.0.0.1:5000/api?camera_json={%22type%22:%20%22Feature%22,%22properties%22:%20{%22angle%22:%2038.876645504061116,%22bearing%22:%2031.979981482645943,%22distance%22:%2087.9921646359149},%22geometry%22:%20{%22type%22:%20%22GeometryCollection%22,%22geometries%22:%20[{%22type%22:%20%22Point%22,%22coordinates%22:%20[4.646878838539124,52.3969167956431]},{%22type%22:%20%22LineString%22,%22coordinates%22:%20[[4.647177386477727,52.39773567907421],[4.647953579015309,52.39743995473123]]}]}}&camera_scale=1.5&show_cameras=true
@app.route('/api', methods=['GET'])
def api():
    if request.method == 'GET':
        # get values BOTH from POST and from GET!!!
        # https://stackoverflow.com/questions/10434599/get-the-data-received-in-a-flask-request
        camera_json = None
        if 'camera_json' in request.values:
            camera_json = request.values['camera_json']
        camera_scale = 1
        if 'camera_scale' in request.values:
            camera_scale = float(request.values['camera_scale'])
        show_input = False
        if 'show_input' in request.values:
            show_input = True  # request.form['show_input']
        show_cameras = False
        if 'show_cameras' in request.values:
            if request.values['show_cameras'].upper() in ('1', 'ON', 'TRUE'):
                show_cameras = True
        show_result_centroids = False
        if 'show_result_centroids' in request.values:
            show_result_centroids = True
        method_vertex = True
        # if 'method_vertex' not in request.values:
        #     method_vertex = False  # request.form['method_vertex']
        method_beam = True
        # if 'method_beam' not in request.values:
        #     method_beam = False  # request.form['method_beam']
        use_bag_panden = True
        use_kadaster_bebouwing = False
        if 'datasource' in request.values:
            if request.form['datasource'] == 'use_kadaster_bebouwing':
                use_kadaster_bebouwing = True
            else:
                use_bag_panden = True

        result_json = BlikVeld().run(camera_json,
                                     camera_scale,
                                     show_input=show_input,
                                     show_cameras=show_cameras,
                                     show_result_centroids=show_result_centroids,
                                     method_vertex=method_vertex,
                                     method_beam=method_beam,
                                     use_kadaster_bebouwing=use_kadaster_bebouwing,
                                     use_bag_panden=use_bag_panden)
        import urllib.parse
        result_json_encoded = urllib.parse.quote(result_json)
        return render_template('result.html', result_json=result_json, result_json_encoded=result_json_encoded)
    else:
        return render_template('camera.html')
    # if 'camera_json' in request.values:
    #     camera_json = request.values['camera_json']
    #     result_json = BlikVeld().run(camera_json)
    #     import urllib.parse
    #     result_json_encoded = urllib.parse.quote(result_json)
    #     return render_template('result.html', result_json=result_json,
    #                            result_json_encoded=result_json_encoded)

@app.route('/camera', methods=['POST', 'GET'])
def camera():
    if request.method == 'POST':
        camera_json = request.form['camera_json']
        camera_scale = float(request.form['camera_scale'])
        show_input = False
        if 'show_input' in request.form:
            show_input = True  # request.form['show_input']
        show_cameras = False
        if 'show_cameras' in request.form:
            show_cameras = True  # request.form['show_cameras']
        show_result_centroids = False
        if 'show_result_centroids' in request.form:
            show_result_centroids = True  # request.form['show_result_centroids']
        method_vertex = True
        if 'method_vertex' not in request.form:
            method_vertex = False  # request.form['method_vertex']
        method_beam = True
        if 'method_beam' not in request.form:
            method_beam = False  # request.form['method_beam']
        use_bag_panden = True
        use_kadaster_bebouwing = False
        if 'datasource' in request.form:
            if request.form['datasource'] == 'use_kadaster_bebouwing':
                use_kadaster_bebouwing = True
            else:
                use_bag_panden = True

        result_json = BlikVeld().run(camera_json,
                                     camera_scale,
                                     show_input=show_input,
                                     show_cameras=show_cameras,
                                     show_result_centroids=show_result_centroids,
                                     method_vertex=method_vertex,
                                     method_beam=method_beam,
                                     use_kadaster_bebouwing=use_kadaster_bebouwing,
                                     use_bag_panden=use_bag_panden)
        import urllib.parse
        result_json_encoded = urllib.parse.quote(result_json)
        return render_template('result.html', result_json=result_json, result_json_encoded=result_json_encoded)
    else:
        return render_template('camera.html')
