import mysql.connector
from flask import Flask
from flask import request
import json
import geopy.distance

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)
cnx = mysql.connector.connect(user='root',
                                password='jaki1234',
                                host='35.219.48.119',
                                database='jaki',
                                auth_plugin='mysql_native_password')

filter_sort_dict = {"id": '', "status": '', "title": '', "review_star": None, "longi": None, "lat": None, "created_at": '', "photo":''}
filter_sort_list = []

def listing (query_result):
    filter_sort_list.clear() # Clearing list from other query
    for x in query_result:
        count=0
        count_2 = 0
        for y in x:
            count += 1
            for k,v in filter_sort_dict.items():
                count_2 += 1
                if count == count_2:
                    filter_sort_dict[k] = y
                    count_2 = 0
                    break
        dict_copy = filter_sort_dict.copy()
        filter_sort_list.append(dict_copy)
    return filter_sort_list

def get_data_loc():
    cursor = cnx.cursor()
    cursor.execute("SELECT lat,longi FROM report")
    loc = cursor.fetchall()
    return json.dumps(loc, default=str)

@app.route('/')
def purpose():
    return 'This link is for passing the data from database to the Mobile App'

@app.route("/filter-date/<start_date>/<end_date>") # Route for Date Filtering
def filter_date(start_date,end_date):
    cursor = cnx.cursor()
    cursor.execute("SELECT id,status,title,review_star,longi,lat,created_at,photo FROM report WHERE created_at BETWEEN '{} 00:00:00' and '{} 23:59:59'".format(str(start_date),str(end_date)))
    data = cursor.fetchall()
    result = listing(data)
    return json.dumps(result, default=str) # default=str, it's used for Decimal and Datetime datatype because JSON can't serialize these things

@app.route("/filter-status/<status_1>/<status_2>/<status_3>/<status_4>/<status_5>/<status_6>") # If only 2 status get filtered, use random word at the rest of the parameter. Example: Selesai/Koordinasi/nope/nope/nope/nope
def filter_status(status_1,status_2,status_3,status_4,status_5,status_6):
    cursor = cnx.cursor()
    cursor.execute("SELECT id,status,title,review_star,longi,lat,created_at,photo FROM report WHERE status='{}' OR status='{}' OR status='{}' OR status='{}' OR status='{}' OR status='{}'".format(status_1,status_2,status_3,status_4,status_5,status_6))
    data = cursor.fetchall()
    result = listing(data)
    return json.dumps(result, default=str)

@app.route("/sort/<method>")
def sort(method):
    cursor = cnx.cursor()
    if method == 'latest': #For sorting from latest complaint
        cursor.execute("SELECT id,status,title,review_star,longi,lat,created_at,photo FROM report ORDER BY created_at DESC")
        data = cursor.fetchall()
    elif method == 'oldest': #For sorting from oldest complaint
        cursor.execute("SELECT id,status,title,review_star,longi,lat,created_at,photo FROM report ORDER BY created_at ASC")
        data = cursor.fetchall()
    elif method == 'comment': #For sorting from the most commented complaint
        cursor.execute("SELECT id,status,title,review_star,longi,lat,created_at,photo FROM report ORDER BY (SELECT COUNT(*) FROM discussion_report WHERE id_report=id) DESC")
        data = cursor.fetchall()
    elif method == 'support': #For sorting from the most supported complaint
        cursor.execute("SELECT id,status,title,review_star,longi,lat,created_at,photo FROM report ORDER BY support DESC")
        data = cursor.fetchall()
    result = listing(data)
    return json.dumps(result, default=str)

@app.route("/search/<keyword>")
def search(keyword):
    cursor = cnx.cursor()
    cursor.execute("SELECT id,status,title,review_star,longi,lat,created_at,photo FROM report WHERE id REGEXP '{}\*' OR title REGEXP '{}\*' OR category REGEXP '{}\*'".format(keyword,keyword,keyword))
    data = cursor.fetchall()
    result = listing(data)
    return json.dumps(result, default=str)

@app.route("/filter-loc/<my_longi>/<my_lat>/<km_choice>")
def filter_loc(my_longi,my_lat,km_choice):
    my_coor = (float(my_lat),float(my_longi))
    data_coor = json.loads(get_data_loc()) #Get data Location from database
    query = 'SELECT id,status,title,review_star,longi,lat,created_at,photo FROM report WHERE '
    matched_loc = []
    for x in data_coor:
        count = 0
        for y in x:
            count += 1
            if count == 1:
                lat = float(y)
            else:
                longi = float(y)
        comp_coor = (lat,longi)
        km = geopy.distance.vincenty(my_coor, comp_coor).km # Measure distance (in km) between user's location and location in database
        if km <= int(km_choice):
            matched_loc.append(comp_coor) # The coordinates that matched with condition will be added to the list
    for x in matched_loc:
        count = 0
        for y in x:
            count += 1
            if count == 1:
                lat = str(y)
            else:
                longi = str(y)
        query = query + "(lat={} AND longi={}) OR ".format(lat,longi)
    query = query + "id=\'wkwkwkkwwk\'" # Just ignore this, but don't delete it
    cursor = cnx.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    result = listing(data)
    return json.dumps(result, default=str)

@app.route("/filter")
def filter():
    query = "SELECT id,status,title,review_star,longi,lat,created_at,photo FROM report WHERE "
    if 'start_date' in request.args:
        start_date = request.args['start_date']
        if 'end_date' in request.args:
            end_date = request.args['end_date']
            query = query + "created_at BETWEEN '{} 00:00:00' AND '{} 23:59:59' ".format(str(start_date),str(end_date))
    if 'status_1' in request.args:
        status_1= request.args['status_1']
        if 'start_date' and 'end_date' in request.args:
            query = query + "AND (status='{}' ".format(str(status_1))
        else:
            query = query + "status='{}' ".format(str(status_1))
    if 'status_2' in request.args:
        status_2= request.args['status_2']
        query =  query + "OR status='{}' ".format(str(status_2))
    if 'status_3' in request.args:
        status_3= request.args['status_3']
        query =  query + "OR status='{}' ".format(str(status_3))
    if 'status_4' in request.args:
        status_4= request.args['status_4']
        query =  query + "OR status='{}' ".format(str(status_4))
    if 'status_5' in request.args:
        status_5= request.args['status_5']
        query =  query + "OR status='{}' ".format(str(status_5))
    if 'status_6' in request.args:
        status_6= request.args['status_6']
        query =  query + "OR status='{}' ".format(str(status_6))
    if 'my_lat' and 'my_longi' and'km_choice' in request.args:
        my_lat = request.args['my_lat']
        my_longi = request.args['my_longi']
        km_choice = request.args['km_choice']
        data_coor = json.loads(get_data_loc())
    if 'status_1' in request.args:
        if 'start_date' and 'end_date' in request.args:
            query = query + ")"
    cursor = cnx.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    result = listing(data)
    return json.dumps(result, default=str)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True) # This is just for testing in the Cloud Shell