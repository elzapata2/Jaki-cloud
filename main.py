import mysql.connector
from flask import Flask
from flask import request
import json
import geopy.distance
from google.cloud import storage

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)
cnx = mysql.connector.connect(user='root',
                                password='jaki1234',
                                host='35.219.48.119',
                                database='jaki',
                                auth_plugin='mysql_native_password')

filter_sort_dict = {"id": '', "status": '', "title": '', "review_star": None, "longi": None, "lat": None, "created_at": '', "photo":''}
get_status_dict = {"id_report": '', "status": '', "who": '', "text": '', "created_at": '', "photo":''}
view_all = {"id": '', "title": '', "created_at": '', "category":'', "longi": None, "lat": None, "support":None, "status": '', "review_text":'', "review_photo":'', "review_star":None, "photo":''}
status_view = {"status":'', "created_at":'', "who":''}
inserted_status = {"id_report" : '', "status":'', "who":'',"text":'',"created_at":'',"photo": ''}
inserted_comment = {"id_report":'',"username":'', "discuss":'', "created_at":''}
comments = {"comments": None}
total_comments={"total_comments":None}
comment_view = {"username":'', "discuss":'', "created_at":''}
current_status = {"current_status":None}
disc_dict = {"username":'',"discuss":'',"created_at":''}
filter_sort_list = []

def listing (query_result,dict):
    filter_sort_list.clear() # Clearing list from other query
    for x in query_result:
        count=0
        count_2 = 0
        for y in x:
            count += 1
            for k,v in dict.items():
                count_2 += 1
                if count == count_2:
                    dict[k] = y
                    count_2 = 0
                    break
        dict_copy = dict.copy()
        filter_sort_list.append(dict_copy)
    return filter_sort_list

def get_data_loc():
    cursor = cnx.cursor()
    cursor.execute("SELECT lat,longi FROM report")
    loc = cursor.fetchall()
    return json.dumps(loc, default=str)

def get_query_loc_filter(my_lat,my_longi,km_choice,data_coor):
    query = ''
    my_coor = (my_lat,my_longi)
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
    return query

@app.route("/")
def home():
        return '''
                <p>For filtering data you can use <url>/filter. For Example:\n<p>
                <li><a href="/filter?start_date=2021-05-09&end_date=2021-05-13">https://deft-haven-312422.et.r.appspot.com/filter?start_date=2021-05-09&end_date=2021-05-13</a></li>
                <li><a href="/filter?status_1=Koordinasi&status_2=Selesai&my_lat=-6.23219700&my_longi=106.84370700&km_choice=4">https://deft-haven-312422.et.r.appspot.com/filter?status_1=Koordinasi&status_2=Selesai&my_lat=-6.23219700&my_longi=106.84370700&km_choice=4\n</a></li>
                <p>The parameters:\n</p>
                <li>start_date & end_date (use both of them if you want to filter date)</li>
                <li>status_1, status_2, ... , status_6</li>
                <li>my_lat, my_longi, km_choice (use all of them if you want to filter location)</li><br><br>
                <p> For sorting use <url>/sort/(method). For example:\n<p>
                <li><a href="/sort/latest">https://deft-haven-312422.et.r.appspot.com/sort/latest</a></li>
                <p>The (method)s:\n</p>
                <li>latest (sorting from latest complaint)</li>
                <li>oldest (sorting from oldest complaint)</li>
                <li>comment (sorting from the most commented complaint)</li>
                <li>support (sorting from the most supported complaint)</li><br><br>
                <p> For search filtering use <url>/search/(keyword). For example:\n<p>
                <li><a href="/search/pohon">https://deft-haven-312422.et.r.appspot.com/search/pohon</a></li>
                <p>For now you can search by ID, title, and category</p><br><br>
                <p>For Viewing the complaint use /detail/(id). For Example:\n</p>
                <li><a href="/detail/TS0000000001">https://deft-haven-312422.et.r.appspot.com/detail/TS0000000001</a></li><br><br>
                <p>For inserting and updating data complaint use <url>/insert-data.\n</p>
                <li><a href="/insert-data">https://deft-haven-312422.et.r.appspot.com/insert-data</a></li>
                <p>For inserting/updating support and status, there will be anouter route.\n</p><br><br>
                <p>For getting all status report from a complaint use <url>/status/(id) For example:.\n</p>
                <li><a href="/status/TS0000000002">https://deft-haven-312422.et.r.appspot.com/status/TS0000000002</a></li><br><br>
                <p>For inserting support use <url>/insert-status.\n</p>
                <li><a href="/insert-status">https://deft-haven-312422.et.r.appspot.com/insert-status</a></li>
                <p>This will insert into history_report table and update status in report table.<p><br><br>
                <p>For adding or decreasing support use <url>/add-dec-support.\n</p>
                <li><a href="/add-dec-support">https://deft-haven-312422.et.r.appspot.com/add-dec-support</a></li><br><br>
                <p>For getting every comments in a complaint use <url>/get-comment/(id). For example:\n</p>
                <li><a href="/get-comment/TS0000000002">https://deft-haven-312422.et.r.appspot.com/get-comment/TS0000000002</a></li><br><br>
                <p>For inserting comment use <url>/insert-comment/.\n</p>
                <li><a href="/insert-comment">https://deft-haven-312422.et.r.appspot.com/insert-comment</a></li><br><br>
              '''

@app.route("/filter-date/<start_date>/<end_date>") # Route for Date Filtering
def filter_date(start_date,end_date):
    cursor = cnx.cursor()
    cursor.execute("SELECT id,status,title,review_star,longi,lat,created_at,photo FROM report WHERE created_at BETWEEN '{} 00:00:00' and '{} 23:59:59'".format(str(start_date),str(end_date)))
    data = cursor.fetchall()
    result = listing(data,filter_sort_dict)
    return json.dumps(result, default=str) # default=str, it's used for Decimal and Datetime datatype because JSON can't serialize these things

@app.route("/filter-status/<status_1>/<status_2>/<status_3>/<status_4>/<status_5>/<status_6>") # If only 2 status get filtered, use random word at the rest of the parameter. Example: Selesai/Koordinasi/nope/nope/nope/nope
def filter_status(status_1,status_2,status_3,status_4,status_5,status_6):
    cursor = cnx.cursor()
    cursor.execute("SELECT id,status,title,review_star,longi,lat,created_at,photo FROM report WHERE status='{}' OR status='{}' OR status='{}' OR status='{}' OR status='{}' OR status='{}'".format(status_1,status_2,status_3,status_4,status_5,status_6))
    data = cursor.fetchall()
    result = listing(data,filter_sort_dict)
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
    result = listing(data,filter_sort_dict)
    return json.dumps(result, default=str)

@app.route("/search/<keyword>")
def search(keyword):
    cursor = cnx.cursor()
    cursor.execute("SELECT id,status,title,review_star,longi,lat,created_at,photo FROM report WHERE id REGEXP '{}\*' OR title REGEXP '{}\*' OR category REGEXP '{}\*'".format(keyword,keyword,keyword))
    data = cursor.fetchall()
    result = listing(data,filter_sort_dict)
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
    result = listing(data,filter_sort_dict)
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
            query = query + "(status='{}' ".format(str(status_1))
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
    if 'status_1' in request.args:
        query = query + ")"   
    if 'my_lat' and 'my_longi' and 'km_choice' in request.args:
        my_lat = request.args['my_lat']
        my_longi = request.args['my_longi']
        km_choice = request.args['km_choice']
        data_coor = json.loads(get_data_loc())
        query_loc = get_query_loc_filter(my_lat,my_longi,km_choice,data_coor)
        if 'status_1' in request.args:
            if ('start_date' and 'end_date') in request.args:
                query = query + ' AND ' + '(' + query_loc + ')'
            else:
                query = query + ' AND ' + '(' + query_loc + ')'
        elif ('start_date' and 'end_date') in request.args:
            query = query + ' AND ' + '(' + query_loc + ')'
        elif 'status_1' or ('start_date' and 'end_date') not in request.args:
            query = query + query_loc         
    cursor = cnx.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    result = listing(data,filter_sort_dict)
    return json.dumps(result, default=str)
    #return query

@app.route("/detail/<id>")
def detail(id):
    cursor = cnx.cursor()
    cursor.execute("SELECT * FROM report WHERE id='{}'".format(id))
    data = cursor.fetchall()
    result = listing(data,view_all)
    result_copy=result.copy()
    cursor.execute("SELECT status,created_at,who FROM history_report WHERE id_report='{}' ORDER BY created_at DESC LIMIT 1".format(id))
    data2 = cursor.fetchall()
    result2 = listing(data2,status_view)
    result2_copy=result2.copy()
    current_status["current_status"]=result2_copy
    current_status_copy=current_status.copy()
    list_status=[]
    list_status.append(current_status_copy)
    list_status_copy=list_status.copy()
    cursor.execute("SELECT username,discuss,created_at FROM discussion_report WHERE id_report='{}' ORDER BY created_at DESC LIMIT 3".format(id))
    data3 = cursor.fetchall()
    result3 = listing(data3,comment_view)
    result3_copy=result3.copy()
    comments["comments"]=result3_copy
    comments_copy=comments.copy()
    list_comment = []
    list_comment.append(comments_copy)
    list_comment_copy=list_comment.copy()
    cursor.execute("SELECT COUNT(*) FROM discussion_report WHERE id_report='{}'".format(id))
    data4 = cursor.fetchall()
    result4 = listing(data4,total_comments)
    result4_copy=result4.copy()
    #print(result_copy)
    #print(result2_copy)
    #print(list_status_copy)
    #print(result3_copy)
    #print(list_comment_copy)
    #print(result4_copy)
    for x in result_copy:
        for a in list_status_copy:
            z = {**x,**a}
    for x in result_copy:
        for a in list_comment_copy:
            c = {**z,**a}
    for x in result_copy:
        for a in result4_copy:
            d = {**c,**a}
    complete_list = []
    complete_list.append(d)
    #print (complete_list)
    return json.dumps(complete_list, default=str)

@app.route("/insert-data",methods=['GET', 'POST'])
def insert_data():
    if request.method == 'POST':
        title=request.form.get('title')
        if title == '':
            return 'please insert title'
        cat=request.form.get('category')
        if cat == '':
            return 'Please insert category'
        longi=request.form.get('longitude')
        if longi == '' :
            return 'Please insert longitude'
        lat=request.form.get('latitude')
        if lat == '' :
            return 'Please insert Latitude'
        photo=request.files.get('photo')
        if photo.filename == '':
            return 'Please upload photo'
        gcs = storage.Client()
        bucket = gcs.get_bucket('image-jaki')
        blob = bucket.blob('image/{}'.format(photo.filename))
        blob.upload_from_string(photo.read(),content_type=photo.content_type)
        photo_url = blob.public_url
        #rev_text=request.form.get('review_text')
        #if rev_text == '':
            #rev_text = 'NULL'
        #rev_photo=request.files.get('review_photo')
        #if rev_photo == None :
            #rev_photo_url = 'NULL'
        #else:
            #blob_rev = bucket.blob('rev_image/{}'.format(rev_photo.filename))
            #blob_rev.upload_from_string(rev_photo.read(),content_type=rev_photo.content_type)
            #rev_photo_url = blob_rev.public_url
        #rev_star=request.form.get('review_star')
        #if rev_star == '':
            #rev_star = 'NULL' 
        cursor = cnx.cursor()
        cursor.execute("INSERT INTO report (title,created_at,category,longi,lat,photo) VALUES ('{}',NOW(),'{}',{},{},'{}')".format(title,cat,longi,lat,photo_url))
        cnx.commit()
        cursor.execute("SELECT * FROM report ORDER BY created_at DESC LIMIT 1")
        data = cursor.fetchall()
        result = listing(data,view_all)
        return json.dumps(result, default=str)
        #return rev_photo_url    
    return '''
              <form method="POST" enctype="multipart/form-data">
                  <div><pre>title:              <input type="text" name="title"></pre></div>
                  <div><pre>category:           <input type="text" name="category"></pre></div>
                  <div><pre>longitude:          <input type="number" step="any" name="longitude"></pre></div>
                  <div><pre>latitude:           <input type="number" step="any" name="latitude"></pre></div>
                  <div><pre>photo:              <input type="file" name="photo"></pre></div>
                  <input type="submit" value="Submit">
              </form>'''

@app.route("/status/<id>")
def status(id):
    cursor = cnx.cursor()
    cursor.execute("SELECT * FROM history_report WHERE id_report='{}'".format(id))
    data = cursor.fetchall()
    result = listing(data,get_status_dict)
    return json.dumps(result, default=str)

@app.route("/get-comment/<id>")
def get_comment(id):
    cursor = cnx.cursor()
    cursor.execute("SELECT username,discuss,created_at FROM discussion_report WHERE id_report='{}'".format(id))
    data = cursor.fetchall()
    result = listing(data,disc_dict)
    return json.dumps(result, default=str)

@app.route("/insert-comment",methods=['GET', 'POST'])
def insert_comment():
    if request.method == 'POST':
        id=request.form.get('id')
        user=request.form.get('user')
        comment=request.form.get('comment')
        cursor = cnx.cursor()
        cursor.execute("INSERT INTO discussion_report VALUES ((SELECT id FROM report WHERE id={}),'{}','{}',NOW())".format(id,user,comment))
        cnx.commit()
        cursor.execute("SELECT * FROM discussion_report ORDER BY created_at DESC LIMIT 1")
        data = cursor.fetchall()
        result = listing(data,inserted_comment)
        return json.dumps(result, default=str)    
    return '''
              <form method="POST">
                  <div><pre>id      :               <input type="text" name="id"></pre></div>
                  <div><pre>username:               <input type="text" name="user"></pre></div>
                  <div><pre>comment :               <input type="text" name="comment"></pre></div>
                  <input type="submit" value="Submit">
              </form>'''

@app.route("/add-dec-support",methods=['GET', 'POST'])
def add_dec_support():
    if request.method == 'POST':
        if request.form["action"] == 'Add':
            id=request.form.get('id')
            cursor = cnx.cursor()
            cursor.execute("UPDATE report SET support=IFNULL(support + 1,1) WHERE id='{}'".format(id))
            cnx.commit()
            return 'Support successfully added'
        elif request.form["action"] == 'Decrease':
            id=request.form.get('id')
            cursor = cnx.cursor()
            cursor.execute("UPDATE report SET support=IF(support=1,support=NULL,support - 1) WHERE id='{}'".format(id))
            cnx.commit()
            return 'Support successfully decreased'     
    return '''
              <form method="POST">
                  <div><pre>id      :               <input type="text" name="id"></pre></div>
                  <div><input type="submit" name="action" value="Add"></div> <br>
                  <div><input type="submit" name="action" value="Decrease"></div>
              </form>'''

@app.route("/insert-status",methods=['GET', 'POST'])
def insert_status():
    if request.method == 'POST':
        id=request.form.get('id')
        status=request.form.get('status')
        who=request.form.get('who')
        text=request.form.get('text')
        photo=request.files.get('photo')
        if photo.filename == '':
            photo_url='NULL'
        else:
            gcs = storage.Client()
            bucket = gcs.get_bucket('image-jaki')
            blob = bucket.blob('status_image/{}'.format(photo.filename))
            blob.upload_from_string(photo.read(),content_type=photo.content_type)
            photo_url = blob.public_url    
        cursor = cnx.cursor()
        cursor.execute("INSERT INTO history_report VALUES ((SELECT id FROM report WHERE id={}),'{}','{}','{}',NOW(),'{}')".format(id,status,who,text,photo_url))
        cnx.commit()
        cursor.execute("UPDATE report SET status='{}' WHERE id='{}'".format(status,id))
        cnx.commit()
        cursor.execute("SELECT * FROM history_report ORDER BY created_at DESC LIMIT 1")
        data = cursor.fetchall()
        result = listing(data,inserted_status)
        return json.dumps(result, default=str)  
        #print (photo_url)
        #return photo_url     
    return '''
              <form method="POST" enctype="multipart/form-data">
                  <div><pre>id      :               <input type="text" name="id"></pre></div>
                  <div><pre>status  :               <input type="text" name="status"></pre></div>
                  <div><pre>who     :               <input type="text" name="who"></pre></div>
                  <div><pre>text    :               <input type="text" name="text"></pre></div>
                  <div><pre>photo   :               <input type="file" name="photo"></pre></div>
                  <input type="submit" value="Submit">
              </form>'''

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True) # This is just for testing in the Cloud Shell