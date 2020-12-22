from flask import Flask
from flask import request
from flask import render_template
from flask import redirect
from flask import url_for

from blikveld.camera import BlikVeld

app = Flask(__name__)

@app.route('/blikveld')
def blikveld():
    return BlikVeld().run()

@app.route('/')
def root():
    return redirect(url_for('camera'))

@app.route('/camera', methods=['GET'])
def camera():
    return render_template('camera.html')

# http://127.0.0.1:5000/api?camera_json={%22type%22:%20%22Feature%22,%22properties%22:%20{%22angle%22:%2038.876645504061116,%22bearing%22:%2031.979981482645943,%22distance%22:%2087.9921646359149},%22geometry%22:%20{%22type%22:%20%22GeometryCollection%22,%22geometries%22:%20[{%22type%22:%20%22Point%22,%22coordinates%22:%20[4.646878838539124,52.3969167956431]},{%22type%22:%20%22LineString%22,%22coordinates%22:%20[[4.647177386477727,52.39773567907421],[4.647953579015309,52.39743995473123]]}]}}&camera_scale=1.5&show_cameras=true
@app.route('/api', methods=['POST', 'GET'])
def api():
    # get values BOTH from POST and from GET!!!
    # https://stackoverflow.com/questions/10434599/get-the-data-received-in
    # -a-flask-request
    camera_json = None
    if 'camera_json' in request.values:
        camera_json = request.values['camera_json']
    camera_scale = 1
    if 'camera_scale' in request.values:
        camera_scale = float(request.values['camera_scale'])
    # BlikVeld.OUTPUT_ADRES_PUNTEN=0 BlikVeld.OUTPUT_PAND_VLAKKEN=1 BlikVeld.OUTPUT_PAND_PUNTEN=2
    output = BlikVeld.OUTPUT_ADRES_PUNTEN
    if 'output' in request.values:
        if request.values['output'].upper() in ('1', 'BLIKVELD.OUTPUT_PAND_VLAKKEN', 'OUTPUT_PAND_VLAKKEN'):
            output = BlikVeld.OUTPUT_PAND_VLAKKEN
        elif request.values['output'].upper() in ('2', 'BLIKVELD.OUTPUT_PAND_PUNTEN', 'OUTPUT_PAND_PUNTEN'):
            output = BlikVeld.OUTPUT_PAND_VLAKKEN
    show_input = False
    if 'show_input' in request.values:
        show_input = True  # request.values['show_input']
    show_cameras = False
    if 'show_cameras' in request.values:
        if request.values['show_cameras'].upper() in ('1', 'ON', 'TRUE'):
            show_cameras = True
    # TODO !!
    method_vertex = True
    # if 'method_vertex' not in request.values:
    #     method_vertex = False  # request.values['method_vertex']
    method_beam = True
    # if 'method_beam' not in request.values:
    #     method_beam = False  # request.values['method_beam']

    # use_bag_panden = True
    # use_kadaster_bebouwing = False
    # if 'datasource' in request.values:
    #     if request.values['datasource'] == 'use_kadaster_bebouwing':
    #         use_kadaster_bebouwing = True
    #     else:
    #         use_bag_panden = True

    b = BlikVeld()
    result_json = b.run(camera_json=camera_json,
                        camera_scale=camera_scale,
                        output=output,
                        show_cameras=show_cameras,
                        show_input=show_input,
                        method_vertex=method_vertex,
                        method_beam=method_beam,
                        use_bag_panden=True)

    if 'format' in request.values and request.values['format'].upper() == 'FORMAT_QGIS':
        b.show_in_qgis(result_json)

    import urllib.parse
    result_json_encoded = urllib.parse.quote(result_json)
    if 'format' in request.values and request.values['format'].upper() == 'FORMAT_GEOJSON_IO':
        return render_template('geojsonio.html', result_json=result_json, result_json_encoded=result_json_encoded)
    elif 'format' in request.values and request.values['format'].upper() == 'FORMAT_GEOJSON_HTML':
        return render_template('result.html', result_json=result_json, result_json_encoded=result_json_encoded)
    else:  # default to sending back geojson (as this is an api...)
        response = app.response_class(
            response=result_json,
            status=200,
            mimetype='application/json'
        )
        return response

