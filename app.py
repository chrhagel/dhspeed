from flask import Flask
from flask import request, render_template, jsonify
from trails import trails as tr

app = Flask(__name__)
# ###############################


@app.route('/')
@app.route('/index')
def index():
    ''' Get rides from db. send to index template. show as list. '''
    rides = tr.get_rides()

    return render_template('index.html', 
        rides = rides)



@app.route('/ride.html/<int:id>', methods=['GET', 'POST'])
def ride(id=1):
    ''' Shows a single ride '''
    map_height = '500'
    ride = tr.get_ride_and_json(id)
    
    return render_template('ride.html', 
        ride = ride[0],
        map_height = map_height,
        ride_data = ride[1])



@app.route('/trail_details.html/<int:ride_id>/<int:start_point>/<int:end_point>', methods=['GET', 'POST'])
def trail_details(ride_id, start_point, end_point):
    ''' GET trail id, start and end point. 
        Make a new page that lets you refine the selection. 
        You get 100 points before and 100 points after your original selection.
    '''
    map_height = '300'
    deviation, trail_start_lat, trail_start_lon, trail_details = tr.get_calibrated_subset(ride_id, start_point, end_point)

    return render_template('trail_details.html', 
        ride_id = ride_id,
        deviation = deviation,
        start_lat = trail_start_lat,
        start_lon = trail_start_lon,
        map_height = map_height,
        trail_details = trail_details)



@app.route('/savetrail', methods=['POST'])
def savetrails():
    ride_id = int(request.form['ride_id'])
    trail_name = str(request.form['name'])
    start_point = int(request.form['trail_start'])
    end_point = int(request.form['trail_end'])

    if tr.save_trail(ride_id, trail_name, start_point, end_point):
        return jsonify({'result':True})
    else:
        return jsonify({'result':False})


# ###############################
if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)


# https://github.com/datademofun/heroku-basic-flask/blob/master/README.md