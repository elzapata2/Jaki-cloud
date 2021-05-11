import mysql.connector
from flask import Flask
import json

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)
cnx = mysql.connector.connect(user='root',
                                password='jaki1234',
                                host='35.219.48.119',
                                database='jaki',
                                auth_plugin='mysql_native_password')

@app.route('/')
def purpose():
    return 'This link is for passing the data from database to the Mobile App'

@app.route("/filter-date/<start_date>/<end_date>") # Route for Date Filtering
def filter_date(start_date,end_date):
    cursor = cnx.cursor()
    cursor.execute("SELECT id,status,title,review_star,longi,lat,created_at,photo FROM report WHERE created_at BETWEEN '{} 00:00:00' and '{} 23:59:59'".format(str(start_date),str(end_date)))
    data = cursor.fetchall()
    return json.dumps(data, default=str) # default=str, it's used for Decimal and Datetime datatype because JSON can't serialize these things

@app.route("/filter-status/<status_1>/<status_2>/<status_3>/<status_4>/<status_5>/<status_6>") # If only 2 status get filtered, use random word at the rest of the parameter. Example: Selesai/Koordinasi/nope/nope/nope/nope
def filter_status(status_1,status_2,status_3,status_4,status_5,status_6):
    cursor = cnx.cursor()
    cursor.execute("SELECT id,status,title,review_star,longi,lat,created_at,photo FROM report WHERE status='{}' OR status='{}' OR status='{}' OR status='{}' OR status='{}' OR status='{}'".format(status_1,status_2,status_3,status_4,status_5,status_6))
    data = cursor.fetchall()
    return json.dumps(data, default=str)

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
    return json.dumps(data, default=str)

@app.route("/search/<keyword>")
def search(keyword):
    cursor = cnx.cursor()
    cursor.execute("SELECT id,status,title,review_star,longi,lat,created_at,photo FROM report WHERE id REGEXP '{}\*' OR title REGEXP '{}\*' OR category REGEXP '{}\*'".format(keyword,keyword,keyword))
    data = cursor.fetchall()
    return json.dumps(data, default=str)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True) # This is just for testing in the Cloud Shell