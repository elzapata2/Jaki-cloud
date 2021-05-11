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

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True) # This is just for testing in the Cloud Shell