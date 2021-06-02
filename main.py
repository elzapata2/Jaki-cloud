import mysql.connector
from flask import Flask
from flask import request
import json
import geopy.distance
from google.cloud import storage
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="cloudstorage.json"
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

@app.route("/predict",methods=['GET'])
def predict():
    import tensorflow 
    from tensorflow import keras
    from tensorflow.keras.models import load_model
    from tensorflow.keras.preprocessing.text import Tokenizer
    from tensorflow.keras.preprocessing.sequence import pad_sequences
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM,Dense, Dropout, SpatialDropout1D
    from tensorflow.keras.layers import Embedding
    # Configuration model
    vocab_size = 1000
    embedding_vector_length = 32
    model = load_model("JakiChan")
    '''model.add(Embedding(vocab_size, embedding_vector_length, input_length=100) )
    model.add(SpatialDropout1D(0.25))
    model.add(LSTM(50, dropout=0.5, recurrent_dropout=0.5))
    model.add(Dropout(0.2))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(loss='binary_crossentropy',optimizer='adam', metrics=['accuracy'])'''
    report = ['lampu jalanan mati di Jl. Cemara II RT08/08 Duri Kosambi, Cengkareng, Jakarta Barat'
    'parkir liar bikin sempit jalan...\nbelakang pom bensin slipi'
    'hallo admin mau lapor ada motor vespa modifikasi terpal biru parkir sampai setengah jalan bikin sempit tolong di TL .\nJalan Kran 2 \ntrims .'
    'sampah karung batu puingnya tolong diangkut dibersihkan biar lingkungan terlihat bersih dan rapih '
    'posisi di belakang Kelurahan  Petamburan, Tepatnya di RT. 010/RW.03. Mohon petugas pintu air untuk mengefektifkan fungsi pintu airnya. Terima kasih'
    'sangat berbahaya sekali besinya ke atas di depan halte bus tugu tani'
    'Sampah ex banjir. Aliran air dari jalan tol desari.  Jln mandala 2 bawah  rt008 rw02 Cilandak Barat Cilandak Jakarta selatan'
    'sampah kasur manusia tdk bertanggung jawab buang sembrangan ini laporan yg ke 2 rt006 rw 07 belakang hotel santika'
    'tidak ada tong sampah sepanjang jalan ini sehingga dampah dibuang sembarangan'
    'pohon miring ke jalan, di jln.menteng wadas timur rt 001 rw 009, tepatnya di samping usaha seven juice.tolong ditebang karena membahayakan pengguna jalan.'
    'Jln raya bina marga rt007/05 kelurahan ceger jln rusak tolong kepada pihak bina marga di perbaiki terimakasih'
    'warung di atas saluran air..\njalan pejagalan 1 samping tukang gas ..\nmohon di tindak lanjuti ..\nbilamana kebenarannya bener tolong dibenarkan .bila mana keadaannya salah tolong di salahkan terimakasih ..'
    'pohon yg terletak di jln SMA 14 RT.004/04 cililitan Kramatjati , sangat membahayakan warga sekitar & pengguna jln terutama saat hujan di sertai angin, sewaktu-waktu bisa tumbang di karenakan sdh sangat rindang & akarnya sdh keropos, mhn segera di tebang'
    'sampah buis beton saluran rusak tolong diangkut dibersihkan '
    'Jadi trotoar tempat parkir ya?'
    'rumah saya kebanjiran akibat saluran air yang mampat' 'testing  card\n'
    'ini pohon seri sudah terlalu malang melintang kekabel listrik dan sampah yang diakibatkan kemana mana...belum tentu ppsu mau menyapu setiap hari.mending ditebang atau dirapihkan.karna tidak ad kesadaran dari pemilik rumah.tolong ditanggapi secepatnya.'
    'mohon pemprov dki, ini jalur untuk lari di taman honda - tebet banyak yg rusak semoga diperbaiki '
    'tlg di tertibkan area parkir monas yg sdh ada parkir resmi tp di dlm msh bnyak premanisasi merekan mengkomersilkan lahan parkir, dengan buka tutup pagar parkir mreka khususkan untuk mobil, sdgkan org2 di srh muter cukup jauh yg hrs nya bs di tempuh dkt,tq'
    'ini toko bandel. masih aja parkir d trotoar. ada petugas yg jagain pula. tindak nih oknum jukirnya. duit aja orientasinya'
    'kerja bakti massal d wilayah rw 011 khususnya d rt 007/011 '
    'Tua Muda bersatu demi kebersihan lingkungan warga Warga komplek Tugu Permai RT 05 06 07 RW 02 Kel Tugu Utara KecKoja Jakarta Utara'
    'ini tepatnya didepan polres jatinegara plang dilarang berhentinya copot aja setiap hari begini mulu'
    'saluran air mampet banyak sampah'
    'jalan jadi sempit dan area wilayah taman dijadikan parkir mobil, semakin hari banyak pemilik rusun yang parkir mobil\n\nlokasi di rusun kapuk muara '
    'tolong di tindak banyak mobil parkir di pinggir jalan bikin sempit di jalan Bangka XI patokan deket agen buyung .\ntrims'
    'Jalan Panjang arteri (Kebon Jeruk arah permata hijau) Perempatan Pos Pengumben, Kelurahan Sukabumi Utara. Mohon Kaca Cembung Dibersihkan'
    'Tumpukan sampah di bundaran Komp. Greencourt ,perbatasan wilayah RT. 012dan 004 RW. 014 Kel. Cengkareng Timur Jakbar. \n\nMohon bantuannya untuk di TL, terimakasih. '
    "tolong diangkut, sampah didepan masjid nurul 'aliyah rt.003 RW 05.\n\nTerima Kasih\n\nSemoga Sukses Selalu"
    'sampah dan rumput '
    'parkir liar terjadi lagi krn tdk ada petugas (biasanya ada) Depan RSCM Kiara'
    'spanduk liar ' 'papan reklame gadai apakah ber ijin /pajak?'
    'sampah karung tolong diangkut dibersihkan ' 'reklame tak berijin'
    'parkir liar dibelakang rscm (pintu parkir motor - pinggir kali)'
    'sepanjang jalan menuju asrama DKI' 'umbul umbul ilegal tidak berizin'
    'mohon perampingan sdh musin hujan takut roboh, lokasi depan pln up3 marunda jaln sungai brantas no.1 semper brt jakarta utara'
    'sampah bambu dll tolong dibersihkan biar lingkungan terlihat bersih dan rapih ga terkesan kumuh '
    'Sosialisasi JakiMobile Kelapa Dua'
    'sosialisasi JAKI di kelurahan Jelambar Baru Bersama Pak Sekel '
    'Rumput liar sudah pada subur di cp tengah 30 harap di bersihkan'
    'Penyampaian Bhabinkamtibmas Kel. Kayu manis Matraman Jakarta timur pada Giat PSN Jumantik di RW.09 .'
    'Patokannya belakang RS.Mediros sepanjang Jl.Cinta sampai pasar pulogadung menjadi parkir liar motor/mobil dan juga pemotongan ayam semuah tolong di tertib kan pak .Jl.cinta Rt.04/rw.03 Pulogadung jakarta timur \n\nterimakasih . '
    'tolong pangkas daun bagian bawah supaya tidak kena kepala '
    'lampu jalan mati tolong di perbaiki terimakasih'
    'ini jga musim hujan rumput cepat lebat tolong di tindak'
    'sampah tali rafia di tiang listrik tolong dibersihkan '
    'trotoar baru jdi banyak yang markir apalagi dipasar paseban trotoar jdi tempat parkir HADEHHH'
    'bantu tl pohon terlalu rimbun dikwatir kan saat hujan akan tumbang.mohon dinas terkait di tindak lanjut.'
    'kanstain trotoar pos polisi rusak tolong diperbaiki dirapihkan permanen biar lingkungan terlihat bersih dan rapih '
    'mohon di tl bikin mampet saluran air got...di jln kalibaru barat 7 rt 12 rw 4..gg 1...pk mostupa no hp 088296218221....mohon di percepat .....'
    'tiang billboard tidak tuntas dibongkar nya... '
    'tolong buatkan got sehingga tidak lgi ada genangan lgi di jln raya cilincing kel cilincing kec cilincing jakarta utara....untuk dinas terkait....'
    'Jalan Rasuna Said depan Gedung BNI Syariah\n\nPatokannya Depan gedung Pavillion 1, nah di depan gedung tersebut terdapat halte yang sudah tidak layak karna banyak lobangnya pak kalau hujan menyebabkan bocor makanya butuh cepat ditambal agar bisa di tambal.'
    'masih ada parkir liar di depan itc dan ambasador mall kuningan, ampuun dah... \ntolong di tertibkan yang kaya gini biar gak jadi habbit... \nterima kasih... '
    'Jl. Raya Kresek blok E ext 4 mo. 2'
    'Terjadi genangan air di jalan di panjaitan, depan halte cawang sutoyo, tinggi genangan sebetis orang dewasa. \n'
    'pohon sudah tinggi, butuh toping'
    'Kembali lagi dini hari tadi tanggal 18 nop 2019 ada lagi yg membuang sampah karungan berbau bangkai di lingkungan Jl. Petamburan 5 Rt.16/05, mohon ditindaklanjuti, terimakasih atas tindakan yg kemarin.'
    'mohon segera dilakukan pemotongan pohon yg SDH lebat dan menyetujui kabel, Krn kondisi musim hujan dan angin, area sepanjang jalan baladewa kiri kelurahan tanah tinggi Johar baru Jakarta pusat'
    'selamat pagi pimpinan ijin melaporkan sepanjang jl pasar baru timur rt03 rw04 ada penopingan pohon di karenakan sudah terlalu tinggi,sudah mulai musim penghujan dan angin kencang,menghawatirkan akan tumbang,membahayakan jalur listri {kabel} dan kendaraan '
    'Alamat : gang H.Taisin RT 04/14.kmp pluis .Kel: Grogol Utara.'
    'Lokasi Pohon Mati di RT. 004/014 Kel. Cengkareng Timur. \n\nMohon di TL, pohon sudah mati takut tumbang atau patah dahan Menimpa Bangunan Warga'
    'pohon minta di tebang. soalnya di bawah banyak rumah warga takut pohonnya rubuh.   kp. kurus gang masjid RT 009 RW 006. ditengah2 rumah warga '
    'Penopingan pohon di jl kelinci raya rt08 rw04 pasar baru yg sangat membahayakan sudah musim penghujan dan angin cukup kencang riskan tumbang demikian dan terima kasih'
    'pasar rawajati kalibata. jakarta selatan. motor parkir bikin macet jalannan. tolong ditertibkan pak. terimakasih sebelumya. '
    'Penebangan Pohon || Membahayakan Mahasiswa terkait datangnya musim hujan\n\nKampus UBSI Fatmawati\nJl. RS. Fatmawati No. 24 Pondok labu , Jakarta Selatan'
    'jalan Cempaka Gg III, dan lingkungan Rw 04 Kel Cempaka Putih Barat, lampu penerangan PJU mati semua'
    'Sampah menumpuk di jalan antara lingkungan RT. 5 dan RT. 12 The Greencourt RW. 014  Cengkareng Timur. \n\nMohon bantuannya untuk di TL, terimakasih. '
    'Selasa, 10 Des 2019. sepanjang Jl. Jambrut depan Kelurahan Kenari mobil parkir sembarangan setiap hari. Tolong ditertibkan'
    'bantu cek saluran air..baru masuk musim penghujan udah kena banjir..kp penggilingan gang aim RT10 RW007 Penggilingan cakung jakarta timur'
    'halo admin ada lagi parkir liar mobil pribadi di atas trotoar yang baru selesai direnovasi di depan klinik utana fatwa. tolong tindak lanjut ya min terima kasih'
    'dekat dengan sekretariat rt 012 rw 03 kelurahan pinang ranti kecamatan makasar banyak sekali parkir liar dan rumah yg tdk memiliki garasi salah satunya seperti mobil ini.'
    'parkir liar jalan sabang depan istana wapres tolong ditindak terima kasih'
    'selamat pagi pak izin melaporkan, tolong di derek pak mobil ini sudah menggangu jalan umum, dulu rumah bekas bengkel tapi sudah tidak beroperasi lagi .\ndi Jalan Kran II ,Gunung sahari selatan '
    'kelurahan bidara cina Rt 13 Rw 08 gerobah sampah hancur, sudah lapor ke pihak Rt dan Rw tapi masih belum ada gerobak baru untuk angkut sampah warga. tolong pak kami butuh gerobak sampah baru'
    'tempat sampahnya hilang tolong diganti '
    'maaf, cek app.\nselama ada proyek sinyal hp susah'
    'parkir liar ... tindak tegas !!'
    'dari semalam lampu jalan mati, sudah sering terjadi kalau tiang kena bentur pasti mati, mohon di cek petugas terkait barang kali ada yg kendor, lokasi RT 11/06 penggilingan'
    'mampet bngt ni'
    'tempat sampahnya gk ada. pd kemana ini pak. tlg pasang yg baru'
    'Sampah belum diangkut selama satu minggu.\n\nTadi pagi ada petugas pengangkut sampah mohon maaf untuk tolong dicek masih ada sampah atau tidak, terima kasih.\n\nJl. Duri Barat No. 11 RT/RW 006/008 Kel. Duri Pulo Kec. Gambir.'
    'Jl. Taman Malaka Utara Raya.\nDekat klinik sapta mitra.\n\npohon menutupi lampu PJU yang mengarah ke dalam gang.'
    'parkir sembarangan di depan kantor orang'
    'Bendera partai sepanjang jalan rasuna'
    'terimakasih ppsu cipete selatan yg telah menoping pohon '
    'Dini hari tadi tanggal 17 nop 2019 seseorang telah membuang 4 karung sampah berbau bangkai di wilayah jl. Petamburan 5 Rt.16/05. Mohon tim PPSU terkait untuk menindaklanjuti sampah liar tsb.'
    'sosialisasi aplikasi jaki oleh Pak Eka Sofyan staf di Kel. Kelapa Dua , Kec Kebon Jeruk, jkt Barat'
    'Akses masuk sempit karna banyak warga memarkirkan motornya tidak teratur dan sembarangan, sangat membahayakan bagi anak2 yang sedang berjalan\n\nlokasi di rusun kapuk muara '
    'trotoar untuk tempat parkir?'
    'saya sedang beraktifitas di kawasan car free day. dan di sekitar bunderan HI ada pelayanan mobile bank dki.  dikarenakan  aplikasi jak one saya bermasalah dengan no hp nya,  dan mohon dibantu penggantian no baru.  ternyata tidak bisa dilayani.  thx'
    'Jl.Pualam Raya wilayah RT.009/04 , volume sampah sudah melebihi tempat penampungan nya, mohon pihak terkait menindak lanjuti, terima kasih'
    'sampah bambu tolong dibersihkan ' 'Sdh minta di tebang@dinas kehutanan '
    'Jalan Salihara, sepanjang jalan dari Universitas Nasional sampai GOR Pasar Minggu. Tidak adanya manfaat jalan berupa trotoar pak/bu. Bisa membahayakan pejalan kaki khususnya bagi Penyandang Disabilitas. Posisinya juga ramai karena ada sekolah dan ada unas'
    'pohon terlalu tinggi, sudah kropos di kober rawabunga'
    'tolong di perbaiki JPO gunung Sahari Mangga dua' 'jalan taruna raya'
    'setiap hujan dg intensitas sedang, air dr saluran sll meluap hingga nyaris masuk rumah. mohon utk diperluas saluran air di lingkungan kami. terimakasih'
    'sampah yang telah beberapa hari tidak di angkut petugas kebersihan\n\nalamat : jl.blimbing II RT.07/04 \nKEL.MANGGA BESAR\nKEC.TAMAN SARI'
    'banjir lontar kelurahan tugu Utara  RW010'
    'pohon sudah terlalu tinggi rawan tumbang'
    'jalanannya hancur, berlubang parah. semoga dapat di tindaklanjuti'
    'Mobil Ini Tiap Malam Sampai Ketemu Pagi Parkir Di Sini. Nggak Da Tempat Parkir. Macet Kalau Jam Sibuk. Terima Ksih.'
    'tanaman kering tolong dibenahi '
    'parkir liar d kolong roxy knp gk bs d tindak tegas?? balik lagi aja penuh parkiran d situ. angkut pak'
    'kanstain trotoar tolong dirapihkan kembali ... sepertinya dibongkar oleh oknum yg tidak bertanggung jawab u putaran sepeda motor '
    'parkir liar. lokasi di jl. abdulrahman ( tikungan gereja protestan)'
    'ini laporan yang ke dua kalinya karna dari kemaren cuma kordinasi aja gak ada realisasi...ini pohon nyampah dan ganggu kabel belum lagi tiang listrik yang makin bengkok'
    'halte rusak tidak ada lampu dan kursi. tlg perbaiki'
    'Parli....depan Menara Cardiq, ganggu makan badan jalan. Mhn ditertibkan.'
    'mohon dipangkas bagian bawahnya supaya tidak kena kepala pejalan kaki. di sekitar depan ex stasiun buaran'
    'batu puingnya tolong diangkut dibersihkan '
    'mohon sediakan tong sampah...(  jln otista Raya...  samping alfa midi).... sepanjang jln otista Raya blm ada tong sampah.. makasih.  '
    'tiang miring dilokasi jl raya Gongseng RT 04/09 di dekat JNE dekat masjid Al jadid mohon untuk PLN menindaklanjuti'
    ' Jl Danau Sunter Barat jajaran Seafood Sentosa di trotoarnya penutup saluran jebol masuk ke dalam'
    'Pohon yg ada depan rumah saya (bukan di dalam rumah) sudah sangat tinggi dan lebat. Tahun lalu pernah tumbang sebagian dan menimpa carport. Minta tolong Dinas Kehutanan segera menindaklanjuti untuk ditebang.\nLokasi: RT 006/06 Joglo No. 169, dekat SMP 219.'
    'Selamat sore pak, mohon di tindak sekali lagi sama mobil yang parkir sembarangan, sudah di tegur tapi masih parkir sembarang juga .\ndi Jalan kran II, Kelurahan Gunung Sahari Selatan Kecamatan Kemayoran \nterima kasih .'
    'wilayah untuk RT 006/010 Kel.Pejaten Timur, semua lampu PJU pada mati.'
    ' kepada instansi terkait mohon bantuannya untuk pemangkasan pohon di jln. jelambar utara raya. tepatnya di Rt. 001Rw06 depan rumah no. 1 dan rumah no. 3 dikarenakan pohon sudah terlalu tinggi dan lebat  terimakasih, '
    'parkir liar di dekat senen tolong ditindak lanjut terima kasih'
    'Berantakan'
    'pohon mengganggu pengguna jalanan & jaringan kabel listrik guna penerangan jalan pun terganggu oleh pengerjaan saluran air yang belum Tuntas di Komplek Pelindo II Tanjung Priok Rw. 01 sepanjang jl. anjungan kelurahan Rawabadak Utara'
    'Mohon dapat dibantu penebangan pohon di jl kebayoran lama no 2 RT 009/04 Kel. Sukabumi Utara, karena akar pohon sudah cukup besar dan tinggi dan akarnya merusak dinding saluran air dan mampet.'
    'sudah di TL tapi masih ada ya'
    'kebiasaan ...\npunya mobil ga punya parkiran'
    'Jalan petamburan 3 pertigaan' 'sampah tolong diangkut dibersihkan '
    'patokannya di pasar bojong raya deket orang jual sayur,dibeberapa saluran air banyak banget sampah, tepatnya di jalan madrasah, rawa buaya, '
    'Fasum di jadikan tempat parkir sekolahan'
    'parkir liar di depan DPRD tolong ditindak terima kasih'
    'bendera parpol golkar berizinkah??\njalan fly over slipi Jakarta barat titik gps error tidak sesuai gps laporan.'
    'Laporan ke 2. Ada pembakaran sampah illegal hampir setiap hari, mengganggu kesehatan warga sekitar, terutama bayi dan anak2. Mohon bantuannya menertibkan. Sepertinya yg bakar org dgn gangguan jiwa, mhn dinas sosial juga bertindak.. Terima kasih'
    'sampah asbes dll tolong diangkut dibersihkan '
    'Alamat Kejadian : Jl. Jatipadang Raya, Gang Yusuf Kelurahan Jatipadang. Pasar Minggu Jakarta Selatan.\n\nBanjir menggenangi hampir seluruh area Gang Yusuf RT 03/04. Banjir terjadi hampir setiap tahun, tetapi hingga saat ini masih belum ada tindak lanjut. '
    'banyak pohon di jalan ini yg daunnya terlalu rendah sehingga kena kepala pejalan kaki, tolong dipangkas dan bukan hanya pohonnya terfoto tapi tolong cek semuanya. Masak sih warga yg harus mengingatkan?? kan sudah ada yg punya tupoksi. ayo jangan malas '
    'rusun dakota habis hujan sampah daun berserakan... maklum ya'
    'tolong di rapihkan dah makan korban jiwa pak boss'
    'ijin melaporkan situasi jl pasar baru selatan ada pohon tumbang mohon segera di TL karena membahayakan pejalankaki maupun kendaraan yg lewat maupun yg parkir demikian dan terimakasij'
    'tolong dibersihkan'
    'jalan tanggul basmol RT.011/006 Kel. Kembangan Utara, Kec. Kembangan, jakarta barat. kampu penerangan jalan sudah 2 minggu tidak menyala, pohon di tindak lanjuti karena jalan jadi gelap.'
    'Toping pohon PPSU Kel. kayu manis Matraman Jaktim'
    'lampu jalan mati satu Rw mohon di perbaiki jln timbul jaya Rw. 04 kel. duri kosambi'
    'mampet parah'
    'Jalan Petamburan 2 RT. 010/RW.03 Jakarta Pusat, tepatnya di belakang Kelurahan Petamburan. Mohon petugas terkait untuk mengaktifkan pompa airnya agar air banjir bisa tersedot ke kali. Terima kasih'
    'sampah 3 hari tidak di angkut'
    'mohon bantuannya agar diperbaiki atau diganti tepat di lampu merah jl utan kayu'
    'parkir liar setiap hari menyempitkan ruas jalan'
    'Laporan parkir liar di Jalan Angkasa Dalam 1,tolong di tindak pak parkir di bahu jalan jelas jelas ada rambu dilarang parkir .\nTerima Kasih '
    'Jalan Cipinang Muara 2, Jatinegara. Patokan Persis disebrang JNE Tiara Cipinang Muara. \n\nIzin Lapor Bapak/Ibu, Parkir liar mobil tua dibahu jalan ramai. Menyebabkan macet dikala jam sibuk. sudah lebih dari 1 tahun mengganggu pengguna jalan.\n\nTerima Kasih.'
    'patokanya di cikajang, menumpuknya sampah. kalau hujan dapat menyebabkan kebanjiran pak.\nterimakasih'
    'harus segera di toping karena bisa membahayakan kendaraan dan orang. Taman Seluang Acordion RT05RW07 '
    'dahan sdh terlalu kebawah mengganggu publik'
    'jl pondok randu rt06/02 duri kosambi cengkareng jak bar p'
    'di bawah Stasiun MRT Blok A, depan Alfamart. Ubin pemandu disabilitas dihalangi oleh pagar, mohon diperbaki \n\nterima kasih.'
    'setiap pagi di lingkungan dekat rumah saya selalu ada yg membakar sampah dimana asap dan baunya sangat mengganggu, mohon ditertibkan.'
    'sampah pinggir jalan' 'tolong di toping sepanjang jalan'
    'mohon dahan dipangkas agar fungsi reflektor bisa maksimal.'
    'Parkir liar menutup 1 lajur jalan ' 'parah bngt'
    'jl nusa arah mw kepasar kramat jati tolong di tindak tegas'
    'jalan pendidikan raya. di sebelah bengkel AC mobil.\n\nsampah bekas patahan dahan pohon.'
    'sampah jalan'
    'trotoar dilebarin cuma buat lapak parkir? angkut, tindak tegas'
    'Mau sampe kapan Trotoar terus dijajah? Tindakan tegas dong'
    'sampah tali rafia di tiang rambu lalin tolong dibersihkan '
    'Jalan Ciranjang pohon rubuh, ada kabel2 juga'
    'Pohon di Jl. Taman Kosambi Timur, Perumahan Kosambi Baru depan Blok D2/19A, RT07/RW09, Duri Kosambi Cengkareng Jakbar. Sudah doyong kekali, kuatir roboh, longsor kekali dan ganggu lalulintas.'
    'pohon mengenai kabel listrik di khawatirkan terjadi korsleting listrik.jln.kemayoran gempol Rt 02/03 kel.kbn kosong kemayoran.mohon pihak terkait utk menanganinya.terima kasih?'
    'Bendera partai bikin jelek di jl flyover Mampang '
    'lokasi jl. h. domang Kelapadua. sering terjadi penderekan oleh ptgs dishub mobil yg prkir di lokasi ini. namun sebagian wrg bnyk yg kurang setuju dgn kebijakan ini Krn di lokasi jln ini  tdk terjadi kemacetan mengingat bila ada tamu yg dtg tuk prkir mobil'
    'papan reklame usang tinggal kerangkanya saja bila tidak terpakai dan tidak ada ijin nya dibongkar saja bikin kumuh lingkungan '
    'izin melaporkan parkir liar di atas trotoar di dekat sarinah saat cfd. mungkin parkiran bisa diarahnkan ke gedung pemerintah atau ke dalam sarinah pak. terima kasih'
    'waspada banjir.. tingkat hujan di DKI jakarta mulai meningkat,'
    'rumput liar pinggir jalan'
    'Sy Merasa terganggu dgn Bau pipis dan Reyak bpk ini sdh sy Laporkan ke tingkat kecamatan dan di beri waktu 1 Minggu tp malah disaNgajain dgn bpk ini pdhl enk sy ajak ke panti tp dia Gak mau malah di rumah sy dijadikan tempat tidur tmpt pipis'
    'jalan menteng wadas timur RT.09/RW.07 kelurahan Pasar Manggis Kecamatan Setiabudi Jakarta Selatan'
    'Rumput liar ' 'motor sudah bertahun tahun tanpa pemilik'
    'pot tatanaman kering tolong dibenahi '
    'Pju padam jln raya pasar minggu '
    'Jalan Boulevard Raya, Kelapa Gading, Jakarta Utara. tanaman penghijauan banyak yg kering, mati, akibat tidak dipelihara dan disirami.'
    'lampu jalan masih baru tp tdk dipasang automatic switch agar bisa mati di siang hari'
    'tolong tindak tegas , dan di ingati derek kalo perlu . jl. kayu mas utara 6 sepanjang jaln ini hingga ke pasar pulo gadung parkir liar di bahu jalan\n\nterimakasih. '
    'parkir liar di lapangan banteng, setiap pengunjung dimintakan uang sebesar 5ribu-10ribu dengan tidak ada kerta tanda retribusi. tolong ditindak lanjut min thanks'
    'Jalan kayumanis 1 baru RT 012/01 matraman jakarta\n\n\nKader jumantik RT 012/01 sedang merawat penghijauan di sekitar lingkungan kayumanis 1 '
    'perlu dipangkas karena menutupi rambu penunjuk arah jalan '
    'lahan untuk taman digunakan oleh warga rusun kapuk muara untuk parkir mobil\n\n'
    'Sampah berserakan di pinggir Jalan Palem RW.007'
    'Parkir Liar. Pemaksaan bayar parkir harus 4000 tidak ada karcis resmi. '
    'pohon sudah tinggi, tolong dipangkas bagian atas nya supaya gak makin tinggi, bahaya kalau akarnya gak kuat, bentar lagi masuk musim hujan '
    'Sampah menumpuk di samping jalan gaga deket sawah RT 006 RW 004'
    'reklame liar??' 'deket jalan kramat 4, perempatan, deket masjid'
    'billboard tinggal kerangkanya saja tidak terawat tidak diurus oleh pengelola nya indikasi pasti bermasalah dgn ijin dan pajak reklamenya bermasalah proses bongkar saja bikin terlihat kumuh lingkungan '
    'Padahal sudah dibuat pangakalan di eks ps blora namun tetap saja mangkal di pinggir jalan, menutupi setidaknya 1/3 badan jalan'
    'ini terletak disepanjang jalan at taqwa dekat dengan biro jasa, kalo bisa di tindak lanjut semua karena hampir sepanjang jalan pada parkir nutup hampir serengah jalan, terima kasih'
    "lama2 bs jadi penampungan sampah'liar" 'lampu penerangan jalan mati'
    'saluran mampet bikin banjir. lokasi. jln.raya cilincing, pintu masuk ke kalibaru. kel.kalibaru kec.cilincing jakarta utara'
    'KOMP UNJ BLOK BZ RT13 RW 02. tks direspon dgn cepat dgn action yg nyata. maju kotanya bahagia warganya'
    'Kader Jumantik RW.09 Kel. Kayu manis Matraman Jakarta timur'
    'maaf sisa tebangan pohon di jl kikir 20 blm di angkut mohon bantuannya Mksh rt01/04 kayuputih '
    'Kenapa rambu P coret nya tidak.juga dicopot?? buat apa rambu kalau justru banyak yg parkir. Ini namanya pelecehan thd rambu lalu lintas'
    'Tanaman merambat hingga mengganggu jalur kendaraan terutama mobil. Mohon bantuannya untuk dilakukan pemangkasan.\n\nJl. Gunuk 2, arah ke masjid Al Khairiyah dari Jl. Gunuk Raya, Pejaten Timur, Pasar Minggu, Jakarta Selatan.'
    'Jl.Arabikal RT 004/010 Kel.Pekojan Kec.Tambora Jakarta barat PJU mati mohon di TL'
    'beberapa Lampu PJU mati di RT.001/08 Kel.DuriKosambi , Kec.Cengkareng Jakarta Barat.Mohon di TL.terimakasih'
    'masih di jln.pratekan ry03.03 kel.rawamangun kec.pulogadung pohonan yg rindang mohon di tl penopingan dgn dinas kehutanan.terima kasih'
    'papan reklame ada ijinnya ga tolong ditertibkan ... kalau ga ada ijinnya dan juga ga bayar pajak bongkar saja. bikin terlihat kumuh lingkungan dan juga tidak memberikan pemasukan bagi pemda DKI dari Pajak Reklame nya '
    'Jl. Jagakarsa Raya arah turunan ke Pasar Lenteng Agung, angkot ngetem di bahu jalan kejadian hampir tiap hari, personil Dishub ada tapi mengatur lalu lintas di jalan lenteng agung.'
    'tumpukan sampah disaluran tolong dibersihkan'
    'Tanaman Sayuran Hidroponik di RT.007 RW.08 Kel. Kelapa Dua, Kec. Kebon Jeruk, Jkt Barat siap panen hari Sabtu 30.11.2019, diharapkan kehadiran Pak Lurah ato jajarannya.\ntks.'
    'Parkir di bahu jalan raya Cempaka Putih Timur Raya, Jakarta Pusat oleh pihak tak bertanggung jawab yg selalu mengganggu kelancaran lalu lintas. Mohon ditertibkan'
    'sampah berantakan' 'jalan kotor tidak disapu'
    'mohon dilakukan toping pohon di jl. Budi mulia raya RT2/RW11 mengingat sudah musim hujan & ranting banyak kena kabel'
    'iklan liar '
    'Sosialisasi dr.Uci Puskesmas kecamatan Matraman di RW.09 Kel. Kayu manis Matraman Jakarta timur'
    'gg teladan 2 Rt 03/02 banjir merata d seluruh GG....dan sebagian rmh kemasukan air semata kaki....'
    'papan nama kodim miring tolong dirapihkan diperbaiki permanen '
    'selamat siang izin melaporkan, banyak parkir motor di atas trotoar dan sudah ada rambu dilarang parkir .\ndi Jalan K.H Mas Mansyur sebrangan sama JLNT \nTerima Kasih'
    'Sudah 3 hari PJU padam. \nLokasi: Gg.  Hj.  Niot Rt.  011 RW.  08, Lenteng Agung,  Jakarta Selatan '
    'Rumli sudah rimbun' 'sampah di got Dan dijalan tolong dibersihkan'
    'spanduk liar?' 'parkir di atas trotoar '
    'tiang telpon di gg. cemara Rt 005 rw 06 kel. pisangan baru roboh membahayakan warga \n'
    'hallo admin mau melaporkan ini mobil udah di peringatin udah sempet gak parkir sekarang udah 4hari parkir di situ lagi sedangkan sudah ada spanduk himbauan dilarang parkir tolong di TL \nalamat jalan kran 2\nterima kasih'
    'sampah berserakan di trotoar, aromanya sangat tidak sedap, tolong ditangani'
    'pohon rindang dan rawan patah...dimohon penopingan dari dinas kehutanan untuk di TL.di jln ampera II rt.08 rw.03 kel.rawamangun kec.pulogadung jaktim'
    'Jl. Sunter jaya VIB RT001 RW07  Kel. Sunter Jaya, tj priok Jakarta  utara\n\nMohon kiranya dapat diberikan Tempat sampah roda ukuran 120 Liter di lingkungan kami sebanyak 2(dua)  unit... Terima kasih \n\nHormat kami\nPengurus  RT001 '
    'billboard tinggal kerangkanya saja tidak terawat indikasi pasti bermasalah dgn ijin dan pajak reklamenya .... bongkar saja bikin kumuh lingkungan '
    'saluran air ada sampah'
    'Jl. Masjid Tanzilul Huda, RW. 10 Kel. Cibubur, Kec. Ciracas, Jakarta Timur. (Dekat SMP 258)\n\nSudah lama terjadi, orang2 warga kel. cibubur rw. 10 selalu buang sampah disini lalu dibakar.'
    'KOMP UNJ BLOK BZ RT13 RW 02. lanjutan... puing-puing diantara sampahnya'
    'bendera biru ... masih aja belum dicabut, sudah nyampah begitu dan pemandangan kota jadi kumuh. '
    'pot tanaman pecah tolong diganti atau diAngkut dibersihkan dan rambu nama jalannya dirapihkan permanen biar lebih baik dilihat pengguna jalan '
    'rapihkan ranting pohon agar pada saat hujan dan angin kencang tidak roboh ke jalan Kayu manis timur, Kel. kayu manis Matraman Jakarta timur'
    'Fasilitas mainan anak. perosotan rusak berbulan bulan di Taman Mahoni kelapa Dua Wetan tidak ada perbaikan. Padahal taman ini sangat ramai dengan anak anak. '
    'perlu dipangkas karena menutupi lampu merah '
    'rumput pada subur tolong di tindak'
    'parkir liar di depan mangga dua square'
    'Pohon Miring kejalan, membahayakan pengguna jalan umum. Lokasi Jln. Basuki Rahmat Depan Bengkel Motor dan Warung Padang No. 24 RT. 002 / RW. 009 Kelurahan Rawabunga, Kecamatan Jatinegara Jakarta Timur 13350.'
    'Uda lapor masalah ini ratusan kali di berbagai kanal pelaporan ga ada tindakan '
    'sepanjang jalur ini tidak ada tong sampah sehingga banyak sampah dibuang sembarangan'
    'pasar palmeriam , matraman banyak yg bocor'
    'Pos Ormas Tidak Berfungsi di atas taman dan trotor'
    'papan reklame usang tidak terawat lebih baik dibongkar saja biar lingkungan terlihat bersih '
    'tiang ex papan reklame tidak terpakai lebih baik dibongkar saja biar lingkungan terlihat bersih dan rapih '
    'banjir di lingkungan rt 08/02 Rawa buaya cengkareng jakarta barat'
    'parkir liar ojek daring' 'masih banyak yg blm dipangkas bagian bawahnya'
    'spanduk ada ijin nya ga tolong ditertibkan ' 'wilayah masjid Astra '
    'pohon sudah terlalu tinggi, sangat membahayakan apa bila tumbang, mohon bantuan pemangkasan.\nterima kasih.'
    'reklame liar?'
    'sampah batu puingnya karung dll tolong diangkut dibersihkan biar lingkungan terlihat bersih dan rapih '
    'parkir liar di sepanjang jalan cempaka baru tengah... mengganggu arus lalin apalagi di jam2 brgkt skolah dan kerja.'
    'depan pasar ular permai koja'
    'papan reklame ada ijinnya ga tolong ditertibkan dibongkar saja bila ijin tidak ada bikin terlihat kumuh lingkungan '
    'pembuangan sampah warga sebarangan . itu di sebabkan tempat sampah sementara belum tersedia.'
    'Billboard tinggal kerangka tidak terawat tidak diurus oleh pemilik nya.... seperti ada pembiaran oleh aparat dinas terkait.\n\ncek perizinannya dan pajak reklamenya ... proses bongkar saja bikin terlihat kumuh lingkungan, tanggung jawab siapa ya ? \n'
    'papan reklame tinggal kerangkanya saja tidak terawat bila ijin dan pajak reklamenya bermasalah proses bongkar saja bikin terlihat kumuh lingkungan '
    'jl. warung buncit raya / jl. warung jati barat\n\nposisi sebelum masjid Assalafiyah..\n\nPapan reklame rubuh, menutupi jalan Raya..\n\nAlhamdulillah sudah dengan cepat ditanggapi oleh  petugas dr berbagai Dinas dari Pemprov DKI.. Terimakasih Pak'
    'rusun kapuk muara \n'
    'lokasi kelurahan Kebayoran lama Utara pintu pelayanannya susah untuk dibuka dan bunyinya mengganggu sampai harus dibantu petugas.. tolong diperbaiki '
    'kali sudah penuh dengan Lumpur mohon segera lakukan pengerukan sampai tuntas hingga air kali tidak naik, lokasi rt 07 rw 13 kelurahan cipinang'
    'Jl. Cemp. Putih Tengah I No.1, RT.11/RW.5, Cemp. Putih Tim., Kec. Cemp. Putih, Kota Jakarta Pusat, Daerah Khusus Ibukota Jakarta 10510\n\ndi depan masjid jami yarsi ada sarang tawon'
    'tananam kering tidak dirawat dan disiram'
    'Mohon pohon di sekitar jalan kebon jeruk, di revitalisasi karena jika hujan angin bisa terjadi pohon tumbang yang dapat menimbulkan korban. terima kasih'
    'Obyek pohon rimbun bila hujan angin sangat berbahaya Krn banyak jalur listrik bertegangan tinggi, di Jl Pinang Ranti 1, RT013 RW002 Kel. Pinang Ranti Kec. Makasar - Jakarta Timur'
    'parli d soto ngatidjo itu'
    'tolong ditindak parkir liar di depan warung sederhana jalan jaksa terima kasih'
    'Banyak sampah dan rumput liar di pinggir jalan merusak keindahan lingkungan dan membuat lingkungan menjadi kumuh. Tolong di bersihkan juga saluran air nya penuh semua dengan sampah.. Sepanjang Jl. Deplu 1 No.5B yang masuk dari Toko lukisan'
    'Tumpukan ban bekas ini dikhawatirkan akan menjadi sarang nyamuk di musim penghujan ini. Lokasi di lahan pool taxi, depan SMU 9 Jakarta Timur.'
    'Orang meninggalkan tumpukan karung di atas saluran air di pertigaan Jl Murdai III dan Jl Murdai. Tolong ditertibkan'
    'sampah karung dll tolong diangkut dibersihkan biar lingkungan terlihat bersih dan rapih '
    'Saya kadang bingung sama yang suka bikin pos beginian. Secara fu gsi tidak begitu kelihatan, belum lagi selalu mengambil hak pejalan kaki. Trotoar cuman 1 meter diambil 100% utk hal yang sangat useless. Tlg pemerintah jangan abai. Ini melanggar UU '
    'PSN Jumantik RW.09 Kel. Kayu manis Matraman Jakarta timur'
    'sampah kering tolong dibersihkan '
    'pohon sangat tinggi, tolong dipangkas bagian atas supaya tidak tambah tinggi. Bukan bagian bawah yg dipangkas'
    'kondisi pohon sdh sangat lebat dan membahayakan kabel listrik, mohon ditindaklanjuti'
    'spanduk baliho ada ijinnya ga tolong ditertibkan ..bila tidak ada ijin atau kadaluarsa dibongkar saja biar lingkungan terlihat bersih dan rapih'
    'Jl alur laut'
    'jalan Pisangan lama barat, terusan pos PDIP. Setiap hari mobil parkir liar disini.'
    'rel kereta pagar pengaman tidak ada.... berbahaya deket stasiun buaran lama'
    'tolong di potong, penopingan pohon di jalan durikosambi, sekitar 200 meter dr jalan durikosambi menuju pusdiklat garuda. mengganggu pengguna jalan, apalagi bila musim hujan. terimakasih'
    'Jalan Pisangan lama barat dekat pos PDIP. Patokan Pintu keluar tol ada belokan kedalam jalan tikus. Setiap hari selalu ada mobil,bus, truck parkir sembarangan dan Kios kios illegal ditepi jalan. (Memakan 1 ruas jalan)'
    'Selamat malam,\nLapor, ada lampu jalan yang berkedip-kedip di Jalan Lapangan Bola. Patokannya tukang gorengan atau Gang Cemara.\n\nTolong diperbaiki, ya. Terima kasih banyak :)'
    'Trotoar = tempat dagang '
    "Pohon di sepanjang jalan Baladewa kiri sudah terlalu besar mengingat kondisi sekarang sudah masuk waktu penghujan..mohon untuk segera di sosialisasi'kan..posisi di sepanjang jalan Baladewa kiri depan Alfamart. trima kasih"
    'sebelum nya terimakasih telah menanggapi Laporan saya perihal batu disamping got ini. tp batu batu kecil ditengah got bikin sampah jadi kesangkut pak. \n\nlokasi : Got dpn pos rw 04 kp rawa johar baru . \n\nterima kasih '
    'pohon sudah lebat, sudah masuk musim hujan, bahaya kalau tumbang'
    'Bahu jalan dan trotoar dikuasai unt parkiran pribadi.. Sangat mengganggu kelancaran lalu lintas... Di Jl. Cempaka Putih Timur Raya no. 6..Jakarta Pusat... '
    'posisi di pintu masuk universitas negeri jakarta. jl. pemuda.. Akses trotoar di pakai.'
    'Sampah diatas saluran air got Klu hujan masuk got ini penyebab terjadinya banjir\nlokasi Jalan Asem RT,006/08'
    'ada rambu tapi sengaja parkir, jadi lebih baik pemilik mobil ditindak ataukah rambu nya dicopot saja?? '
    'Patokannya samping St.Manggarai di haltenya terdapat lobang pak. Kalo hujan juga menyebabkan bocor dan genangan air makanya butuh cepat di tambal dulu lobangnya pak'
    'Laporan untuk ke 2 kalinya, karena Laporan 1 statusnya sudah dikerjakan ternyata belum pernah sama sekali di kerjakan bahkan proses TL pun juga tidak pernah ada, Mohon perhatianya kpd Pemerintah Setempat Khususnya Sudin yg terkait. Thx'
    'lokasi di perempatan tegal alur pak, minta tolong pemangkasan dan merapikan pohon,krn ranting nya ud ke mana mana. sudah mengganggu tiang listrik dan jalanan'
    'Sampah Hasil Air Rob ( Pasang Surut Air Laut ) masih mampet di saluran Air Warga Rt 002 Rw 01 Kamal Jakarta Barat'
    'tutup saluran air rusak sehingga jadi tempat pembuangan sampah orang tidak yg tidak bertanggung jawab, bikin mampet saluran air, mohon di tindak lanjuti...!\nlokasi Jln Cempaka Putih Barat XI Gg. E  Rt 008/04 Kel Cempaka Putih Barat, Jakarta Pusat'
    'usul pak..itu tengah2 nya trotoar  mending kasih pohon tabebuya ...pasti cantik..biar adem.moga diterima usulan saya posisi dpn itc Kuningan dan Kuningan city. makasih '
    'reklame liar'
    'Depan gerbang pintu utama ragunan dan arah ke kantor kecamatan ragunan ojol parkir sembarangan. Terimakasih. '
    'Tetangga yg tdk punya lahan garasi mobil setiap harinya parkir di dpn pintu garasi mobil kami, menghalangi akses keluar masuknya mobil kami dan angkutan umum lainnya. Jl. Enim no.64 RT 04/003 Kel. Sungai Bambu Kec. Tanjung Priuk Jakarta Utara.'
    'pengangkatan sampah di RW 03 kebonpala makasar'
    'toping pohon Babinsa bersama PPSU Kel. kayu manis ,ranting ,dahan pohon yg menjorok ke jalan ,agar tidak patah pada saat hujan dan angin kencang'
    'Pohon di jalan H. Sidik RT07/06 Karet Kuningan, mohon di pangkas, karena sudah masuk musim hujan di khawatirkan tumbang menimpa rumah warga.'
    'Alamat gg.darussalam Jl.Bangka II F RT 02. Rw.013\n\nTempat ini mengakibatkan sarang nyamuk Dan sarang tikus . mohon bantuanya untuk menindak lanjutin pembersihan . sudah 2x anak menjadi korban DBD .apakah harus Ada KORBAN baru di TL ?'
    'sosialisasi aplikasi JAKI '
    'hampir setiap hari jalan umum dibuat parkiran pernah ada warga yg sakit sampe ambulan tidak bisa masuk..tolong ditertibkan\nalamat.warakas 4 gg 19 Rt004/013\n'
    'kaca cembung sekitar wilayah jl.pualam raya RT.09/04 terlihat kusam, kurang terawat dan kurang perhatian dari dinas terkait.'
    'sampah kerja bakti di rt 20/03 sampai hari ini belum diangkat. mohon perhatiannya. tks'
    'pohon yg semakin besar dan batang yg sudah mulai keropos, di jakarta barat, kecamatan kembangan kelurahan srengseng rt.002 rw.04 no 42 (samping rumah pak rt damin)'
    'parkir liar samping ITC Kuningan ..( ini parkir dr jaman baheula, preman nya kayak kebal hukum )mohon di tertipkan..sayang trotoar dah bagus tp msh ada parkir liar..sangat menganggu..  makasih. '
    'kegiatan kerja bakti' 'butuh penopingan'
    'cek perizinannya dan pajak reklamenya karena tidak ada stiker merah bukti bayar pajaknya tolong ditertibkan selama ini seperti ada pembiaran '
    'Parkir liar sepeda motor di atas trotoar. Jl. Kramat Raya tepat di bawa JPO ke Plaza Kenari Mas Kamis, 5 Des 2019 12:22 WIB. Mohon ditertibkan'
    'Daun pohon menutup rambu dilarang parkir '
    'lokasi jln bambu asri rt010/03 perum bambu asri.laporan sisa proyek tanggul sudah sebulan lebih.tanah dan lumpurnya tdk di angkat.mengakibatkan air tergenang.dan seputaran perum airny tdk berjlan,akan mengakibatkan jentik nyamuk dbd'
    'Belm dibersihkan ' 'pohon mengenai kabel listrik'
    'perlu dipangkas karena menghalangi pejalan kaki lewat trotoar '
    'selamat siang izin melaporkan, banyak mobil parkir di sepanjang jalan kali ciliwung dr arah mall season city sampe roxy tolong di tindak .\nterima kasih'
    'KOMP UNJ BLOK BZ RT13 RW 02 No32C. musim penghujan dimana nyamuk,ular dan tikus mencari sarang di tempat tumpukan sampah lembab,sebelum ada korban Kami mohon pihak terkait untuk membantu membuat lingkungan kembali asri,bersih dan sehat. tks atas perhatian'
    'Jalan Hidup Baru Raya, antara Hidup Baru IV dan Gang J.\nParkir depan gerbang rumah \nwarga.'
    'Sampah dijl batu tulis 15,sampah sudah hampir 2 minggu.PPSU yang lewat y lewat aja bahkan sampah yg satu kantong plastik jd bertambah karna sampah tdk diambil malah ditumpuk.sampah yang ada tidak tau siapa yang buang.PPSU cuma lewat aja'
    'Selamat siang, izin melaporkan mobil yang parkir persis di depan gang di jalan kran 2 depan bengkel mobil, sebelumnya sudah 3kali dilaporkan dan ditindak dishub, alasannya akan dicarikan parkir, tapi sampai sekarang mobil tsb 24 jam parkir disana'
    'Sampah sudah 2 hari tdk diangkut, apalagi skarang ada Hajatan di jalan tsb, sdh pasti tdk terakut lagi deh olehbTruck sampah\nlokasi di jalan Gabus Rt. 10/07 Subter Jaya deket Kabtor Rw. 07'
    'parkir di atas trotoar'
    'billboard tinggal kerangkanya saja tidak terawat tidak diurus oleh pengelola nya indikasi pasti bermasalah dgn ijin dan pajak reklamenya... proses bongkar saja bikin terlihat kumuh lingkungan '
    'Pohon lebat melintasi kabel listrik di JL. Pademangan 3 Raya RW.09. '
    'sampah batu puingnya tali rafia di tiang tolong dibersihkan biar lingkungan terlihat bersih dan rapih '
    'jalan penbina, matraman jakarta timur banyak parkir liar'
    'spanduk ada ijinnya ga kalau udah selesai tolong ditertibkan '
    'lampu PJU padam 1ttk jl.h.abu RT.005/007 cipete selatan'
    'hujan yg terjadi sejak dini hari td,membuat sebagian wilayah tergenang'
    'selamat siang mohon perampingan,mau musim hujan takut roboh lokasi jln sungai brantas no.1semper barat jakarta utara dpn pln up3 marunda tks'
    'tanamannya mati, tolong ganti dengan yg baru'
    'disamping sekolah sdn 13 pagi semper barat'
    'pohon LIAR tumbuh dipot bunga #kurang pengawasan'
    'billboard tinggal kerangkanya saja tidak terawat tidak dipasarkan indikasi pasti bermasalah dgn ijin dan pajak reklamenya bermasalah proses bongkar saja bikin terlihat kumuh lingkungan dan juga tidak memberikan pemasukan bagi pemda DKI dari Pajak Reklame '
    'hasil musrembang rt 001 dan 002 rw 013 th 2018  d realisasikan tahun ini sudah turun tapi kenyataan.a sampai sskarang gangan kami belum juga d tinggiin jalan.a mengakibatkan kalau hujan air langsung meluber ke jalanan'
    'pohon tumbang terus ada kabel listrik yang hampir putus. maaf fotonya gelap karena buru2'
    'tanaman kering tolong ditanam'
    'wilayah gang kp. Sukasari RT 07 RW 04 \n\npenyumbatan sampah di selokan diakibatkan dengan derasnya volume air ketika hujan.\n\nmohon tindakan untuk pengangkutan sampah dari selokan agar tidak timbul dampak negatif bagi warga sekitar.\n\nterima kasih'
    'tolong tindak'
    'manusia g punya adab buang kasur sembrangan disamping rmh warga'
    'pohon lebat di rumah kosong di wilayah Pademangan barat RT 03/04 berharap bisa ditebang karena merembet dirumah warga'
    'rumput liar sepanjang jalan tikus jalur alternatif'
    'Mau sampe kapan? Lelah nih '
    'sampah saluran hanya ditaruh saja dan rumput jg sudh pada lebat'
    'sampah batang pohon tolong diangkut dibersihkan ' 'spanduk reklame'
    'ranting pohon menutupi reflektor n mengurangi fungsinya'
    'apakah seperti itu sop pekerjaan PJU?? tiang yg dicopot digeletakin gitu aja di trotoar?? sudah 2 mgg seperti itu '
    'Graha Kirana dan Wisma SMR sudah ada rute Mikrotrans dan 10 F tapi tidak dipasang rambu bus stop / halte. Penumpang seringkali kebingungan mau turun dan naik dimana'
    'lampu penerang jalan udah 3 hari mati wilayah kembangan pondok cabe jl kh hasyim...mohon bantuan nya'
    'Permohonan tempat pilah merah kuning hijau di Jalan Sunter Jaya VIB RT 001 RW 07 Kelurahan Sunter jaya kecamatan Tanjung Priok Jakarta Utara'
    'tolong banget batu dipinggiran itu Di angkut krn udah tahunan n bikin kumuh.\n\nalamat : jl. kp rawa selatan V Saluran Air sebrang Pos RW 04 . (johar baru jakpus)\n\nRW nya cuek jd harus lapor kesini kayanya.\nterimakasih.'
    'Jl Adityawarman Raya . Kebayoran  , Jakarta Selatan. dekat kantor pusat PLN'
    'izin melaporkan parkir lias di dekat pom bensin di dekat Pom Bensin Menteng.'
    'pot tanaman pecah tolong diperbaiki permanen '
    'sering bakar sampah, sudah di infokan ke RT dan RW tetapi tidak ada hasil, mungkin karena sesama betawi jadi tidak menghiraukan. Asap dari sampah mengakibatkan orang tua saya sakit batuk, harap ditindaklanjuti, jln bunga melati cip sel, samping 007'
    'billboard tidak ada stiker merah bukti bayar pajaknya tolong di cek perizinannya dan pajak reklamenya bayar ga ... bila bermasalah, tindakan segel atau proses bongkar '
    'kerja bakti rutin Rw03 Biduri Pandan di kelurahan galur jakpus 10530'
    'pohon dpn rt 01/04 kayuputih jl,kikir 20  sdh ganggu kabel listrik ,mohon di pangkas'
    'Rumput sudah pada lebat '
    'sampah di saluran air/got JL. petamburan 4,depan SD bethel/samping kantor Dinas Kehutanan DKI JAKARTA'
    'sampah kayu batu puingnya tolong diangkut dibersihkan biar lingkungan terlihat bersih dan rapih ga terkesan kumuh '
    'mohon bantuannya untuk diangkut  pak\n\nterima kasih\n\nsemoga berkah sukses selalu'
    'halte tidak ada lampu penerangan. mohon perbaiki. halte kemenyan'
    'imbas..air saluran kali yg tanah dan sisa bahan yg tdk di angkat..sehingga airny gotny tergenang'
    'reklame gadai, adakah ijinnya?'
    'Di menteng dalam dekat mesjid jami asy syarif, dekat rumah no 10, parkir sembarangan, menyebabkan macet'
    'kata nya sudah di beresi, hasil nya.....'
    'Selamat sore izin melaporkan, ada mobil tua parkir terbengkalai bikin jalan sempit tolong di tindak, banyak mobil pribadi juga yg parkir.\nalamat di Jalan Bungur Besar 17 arah pasar kombongan .\nTerima kasih'
    'sampah liar dekat SDN 20' 'perlu dipangkas karena menutupi rambu lalin '
    'tanaman pot mati tolong dibenahi '
    'kampung pulo kambing rt 007 rw 02..sampai saat ini blm ada tindak lanjut untuk penebangannya..\n'
    '2 batang pohon tumbuh tidak pada tempatnya'
    'billboard cek perizinannya bila ijin tidak ada proses bongkar saja bikin terlihat kumuh lingkungan dan juga tidak memberikan pemasukan bagi pemda DKI dari Pajak Reklame nya... '
    'Tolong satpol PP dan kepolisian setempat menertibkan parkir liar di depan Gate II Apartemen Kalibata City. Selain TAXI seringkali motor online mangkal dan pedagang kaki lima berjualan. Sangat mengganggu dan menimbulkan kemacetan. Tks.'
    'banjir dilontarV111RT006/010'
    'Mohon penopingan pohon Jl Raya Pademangan 3 wilayah Rt 09 Rw 07'
    'jalan arah masuk gading griya ada pohon sudah rindang dan ranting2nya dekat dengan jalan\n\nsangat membahayakan penguna jalan'
    'Jln. Gadang I No. 13                 Rt. 004/07 Kelurahan Sungai Bambu. Tg. Priok Jakarta Utara.... Mohon di Toping karena mengganggu penerangan lampu jalan. '
    'tanaman liar pada tinggi tolong petugas kelurahan untuk dibabat '
    'baliho tanpa ijin sudah expired masih aja dibiarkan'
    'wah Di samping sekolah menjadi sangat Sejuk Dan tidak Panas maupun gersang'
    'pohon miring Jl.Pademangan IV gg.34 pinggir kali RW.01'
    'parkir liar di dekat cempaka mas.'
    'pohon sdh lebat depan sekolah Tk impian bunda\njl.Rasamala hijau II perumahan kosambi baru jakarta barat'
    'jalan Kayu Tinggi Kp Kandang Sapi RT.001/06 Kelurahan Cakung Timur, persis depan SDN 04 Cakung Timur.\n\nmohon bantuan dinas terkait, dahan pohon menghalangi Penerangan Jalan. tks'
    'Bajaj parkir di jalan, membuat kumuh dan macet.'
    'sampah ditimbun di trotoar'
    'jln kemang raya diresto mama rossy,parking mobil sembarangan dan mengambil 2 jalur arah ke mcdonald dan kearah ampera mengakibatkan kemacetan dan juga sangat mengganggu jalan warga yang ingin masuk ke jln kemang selatan II mhn segera di tinjak lanjuti .'
    'Lokasi rw 06 cipinang muara, lahan kosong belakang tower pemancar. Lahan ini menjadi tempat pembuangan/penumpukan sampah ilegal,sering ada pembakaran sampah ganggu kesehatan warga terutama anak-anak, gampang batuk, bau busuk sampah, mohon bantuan petugas'
    'Banjir tidak surut dari pagi dikarenakan saluran yang menyempit akibat bangunan liar di Sungai kelurahan Cilincing.\n\nJl. Cilincing Bakti VII RT/RW:06/07\n\nTolong segera ditangani jika diperlukan lakukan sterilisasi Sungai Cilincing sebagai KSD 2020 '
    'di sekitaran tanah abang sebrang hotel pharmin , deket halte transjakarta .  ini ojek online apa ojek pangkalan pada ngetem bikin macet ajja tindak tegas '
    'pohon yg rindang dan rawan patah atau tumbang...mohon di tl untuk penopingan dari dinas kehutanan lokasi jln pratekan rt.03 rw03 kel.rawamangun kec.pulogadung jaktim'
    'rangka kayu tolong dibongkar saja biar lingkungan terlihat bersih '
    'rumput pada subur musim hujan tolong dibabat'
    'kenapa kantor kelurahan ini justru menjadi pelanggar parkir liar?? memakan separuh jalan lagi, memang nya jalan umum itu lahan parkir kelurahan??'
    'Tiang informasi lintasan sepeda roboh, patokan dekat bundaran Walikota jakarta selatan ke arah Blok M. Jl.prapanca raya'
    'pohon rindang dan lebat di khawatirkan patah..mohon penopingan dgn dinas kehutanan dan di TL.di jln.ampera II rt.08 rw.03 kel.rawamangun kec.pulogadung jaktim'
    'Sampah Janur, sudah kering\n\njl Griya wartawan'
    'kelurahan bidara cina Rt 13 Rw 08 jakarta timur. butuh gerobak sampah untuk angkut sampah. sudah lapor Rt dan Rw tapi blum ada penggantian. terpaksa selama ini tukang sampah kami harus menyewa gerobak dari RW lain, ad biaya Rp. 20rb setiap sewa gerobak'
    'jalan tkp /alternatif dari sahabat'
    'sampah tali rafia di tiang rambu lalin tolong dibersihkan biar lingkungan terlihat bersih ga kumuh '
    'Dahan sudah terlalu rindang mengganggu kendaraan yg akan keluar dari Masjid Al azhar\n.. Lokasi depan Halte Busway Walikota Jakarta timur'
    'tanaman mengganggu plang penunjuk jalan\ntolong dirapikan'
    'sampah layangan di atas kabel listrik '
    'Ojol ngetem di jalur sepeda dpn arion'
    'ini aduan yang ke 3 kalinya setelelah aduan 1 dan ke minta pohon ditebang karna nyampah dan ganggu kabel.sekarang setelah pohon ditebang malah sampah pohon n dahan gak diambil.ini ngebahayain orang lewat dan anak.kalo ngerjain tlg pak jangan setengah2'
    'Juru parkir liar sering gonta-ganti + diatas trotoar, pungutan liar parkir depan warung bakso. Keberadaan juru parkir liar jam 13:00 sampai dengan jam 21:00, juru parkir liar kemungkinan dari ormas sekitar, mohon ditertibkan pada jam 13:00 ke bawah.'
    'sisa galian tidal di rapihkan kembali, berbahaya ketika hujan deras, tanah berceceran di trotoar dan jalan. lokasi jln kebon sirih seberang Bank indonesia'
    'Pepohonan menutupi penerangan jalan gang persis dpn gang Utama'
    'beton tutup saluran tolong diangkut dibersihkan biar trotoar terlihat bersih dan rapih '
    'Pertigaan telkom pademangan Timur,menempel ke kabel,jika angin kencang suka mengeluarkan percikan api'
    'tolong ditindak parkir liar di depan warung di jalan jaksa terima kasih'
    'Nih saya lapor lagi karena yang kemarin DI TL sembarangan jam 5 pagi coba. Ckckck'
    'bikinin halte dong untuk nunggu transjakarta biar gak kepanasan nunggu bus'
    'lakban tali rafia dll di tiang listrik telpon tolong dibersihkan kerok dan di cat biar lingkungan wisata kota tua terlihat bersih ga kumuh '
    'sampah tak bertuan' 'tolong pangkas daun bagian bawah '
    'parkir liar di atas trotoar di depan JSC hive' 'parkir liar'
    'sampah batu puingnya tolong diangkut dibersihkan '
    'pohon di jalan bambu APUS Raya. pondok bambu dekat masjid Al-Huda sangat rimbun. mengingat musim hujan dan angin. takut terjadi yang tidak di inginkan.'
    'Parkir liar mobil dinas, tolong ditindak lanjuti' 'Spanduk liar'
    'lokasi di kolong atrium senen , ngaku nya online kok pada mangkal dah kaya ojek pangkal . tindak tegas bikin macet'
    'mohon sediakan tong sampah ukuran besar... jln Letjend Suprapto no 100. \nposisi DPN dealer Honda ( Galur motor) ... jgn di angkut aja tp sediakan tong sampah ukuran besar... makasih.'
    'Lampu penyebrangan jalan bundaran HI sisi hotel Pullman, 1 detiknya setara 2 detik kehidupan nyata dan suara peringatannya tidak terdengar, tolong dibenahi :)'
    'saluran air yg menyempit di ujung jln kebagusan 3 mengkibatkan air meluap ke jln yg akhirnya menggenangi jalanan. mohon dpt sgr ditindaklanjuti...terimakasih'
    'Permohonan tempat sampah roda ukuran 120 Liter..dua Unit\n\nJL. Sunter Jaya VIB RT 001 RW 07 Kelurahan Sunter jaya kecamatan Tanjung Priok Jakarta Utara'
    'jl prof dr satrio depan mall ambasador. selalu dijadikan parkir liar. '
    'Sosialisasi Jaki oleh Lurah Kayu manis di RW.09 di ikuti oleh seluruh Kader PSN Jumantik Kel. Kayu manis Matraman Jakarta timur'
    'sampah karung dll tolong diangkut dibersihkan '
    'banyak banget warga buang sampah ke kali akibat jembatan ditutup'
    'penaataan taman sudah bagus bantaran sungai di beri lampu hias\ntapi sangat di sayangkan di rusak oleh tingkah laku dari pada PEMBORONG yang masih MEMBUANG SAMPAH bekas KARDUS LAMPU di lokasi tersebut di temukan Banyak bekas sisa kardus lampu, SEGERA DI TL'
    'ijin melaporkan dahan pohon yg tumbang di jl dr sutomo rw08 rt03 kel pasar baru{ke kali ciliwung} tepatnya depan hotel bintang baru'
    'billboard tinggal kerangkanya saja tidak terawat tidak diurus oleh pengelola nya... cek perizinannya bila ijin dan pajak reklamenya bermasalah proses bongkar saja bikin terlihat kumuh lingkungan dan juga tidak memberikan pemasukan bagi pemda DKI '
    'pohon mohon dipangkas bagian bawahnya supaya tidak kena kepala pejalan kaki. di depan stasiun buaran'
    'Sampah kiriman di saluran PHB depan Blok E10'
    'Alamat : Jl. Peta Selatan RT. 10/01, Kalideres Jakarta Barat'
    'pohon dtepi jalan sudah terlalu rindang dan sudah masuk musim penghujan takut rubuh bila tertiup angin besar alamat jl. mabes TNI Delta 5 Rt002 Rw 06 kelurahan cilangkap kecamatan cipayung jakarta timur.tolong pohon tersebut d pangkas atas nya'
    'semakin hari semakin banyak warga rusun kapuk muara membawa mobil pribadinya, banyak warga yg sudah mampu tinggal dirusun yang memiliki mobil pribadi \nlahan taman pun digunakan untuk parkir mobil \n\nlokasi di rusun kapuk muara '
    'fasilitas jalan rusak, tolong segera diperbaiki'
    'Antisipasi keamanan lingkungan ,wilayah RW 02.cawang'
    'Batang pohon mangga mengganggu kabel tilpon, listrik n utility lainnya, mohon dipangkas dgn seijin pemilik rumah yg punya pohon'
    'coba deh kesininya siang atau sore ktanya sih udh diurus tapi masih terjadi lagi.'
    'tolong di rapihkan atau di tebang di jalan batu sulaiman kelurahan kayu putih kecamatan pulogadung'
    'pohon yg rindang khawatir patah...mohon diadakan penopingan dari dinas kehutanan di jln.ampera 2 rt08 rw03 kel.rawamangun kec.pulogadung jaktim'
    'mohon bantuannya untuk diangkut  1 plastik besar sampah sehabis acara. lokasi sebrang pangkas rambut nabawi RT 003/05, Cip Muara.\n\nTerima Kasih\n\nsemoga sukses dan berkah selalu'
    'Jln petojo binatu 6 rt 04 rw 08 kel petojo utara kec gambir jakarta pusat.\n\nSamping smpn 72'
    'Ini bekas galian kabel yg di tinggal begitu saja tolong di perbaiki tks'
    'laporan sudah ke 4 kali ga ada respon tindak lanjut cm dinyatakan selesai laporan palsu'
    'sampah tali rafia di tiang listrik tolong dibersihkan kerok dan di cat '
    'dijalan SD 01 LAMA PONDOK RANGGON..KABEL TELPON/LISTRIK MENJUNTAI KEJALAN'
    'Mohon ditertibkan pohon & taman liar di pertigaan Jl Mardani III dan Jl Murdai yg berdiri di atas saluran air. Karena jd tempat orang tidak dikenal nongkrong hingga larut malam, aksi vandalisme tembok warga, sarang tikus, ulat & mengganggu tiang telepon.'
    'komplek bungur indah'
    'sepanjang jalan cililitan kecil 3 sampai jalan cililitan kecil 1 jakarta timur banyak mobil parkir liar di bahu jalan..padahal itu jalanan umum'
    'usia buleh Tua\n\nSemangat ttp luar biasa\n'
    'Pohon warga yang sudah mati di khawatirkan rubah, diminta utk di tebang,  jalan Kebon Kosong 6 rt 006/01 kel kebon kemayoran Jakarta Pusat '
    'parkir liar motor vespa modifikasi ' 'tolong ditindak'
    'Ada ijinya ga papan reklame di bawah kabel'
    'kapan warga sadar buang sampah, untk tdk buang ke Saluran '
    'reklame berijin?'
    'Pembangunan pasar Munjul Kecamatan Cipayung yg tertunda kapan mau dilanjutkan kebai.'
    'lampu PJU padam jl.pelita RT.006/007 kel.cipete selatan'
    'pohon menyebabkan, atap rumah bocor dan membahayakan. Lokasi Gedung Dinas Pemakaman dan Pertamanan DKI jakarta, Jl Petamburan 4,Jakarta Pusat. \nTolong ditndak '
    'parkir liar di mangga dua tolong ditindak' 'saluran mampet'
    'tolong lakukan pengerukan lumpur dan sendimen disepanjang kali ini karna Air sudah mulai meluap di karnakan pendangkalan kali lokasi rt 07 rw 13 kel cipinang'
    'sampah karung'
    '*Laporan Kegiatan* :\nKerja bakti rutin mingguan Kelurahan Johar Baru di RW.09. Dilanjutkan bincang 2x persiapan lomba PHBS tahun 2020 Tingkat Nasional mewakili Provinsi DKI Jakarta & Persiapan Rembuk RW bersama Camat, Lurah, Pengurus RW, Ketua RT.001-015,'
    'parkir inap'
    'jl prof dr satrio dekat putaran U turn. parkir liar menghambat arus lalu lintas, buat macet'
    'Halte Stasiun KA Jatinegara'
    'JALAN KESEJAHTERAAN RT.014/08 \nPATOKAN SAMPING GEDUNG GRAND PARAGON \n#SAMPAH BERHARI HARI TIDAK DI ANGKAT#'
    'batu puing kanstain dll nya tolong dibersihkan diangkut biar terlihat bersih dan rapih lingkungan nya '
    'sampah kering'
    'Parkir liar di atas trotoar di depan Ampera 2 Tak Jl. Cikini Raya Rabu, 4 Desember 2019 12:21 WIB'
    'Taman Maju Bersama Jalan PPA Bambu Apus\n\nMasalah : Pekerja yang melakukan pekerjaan renovasi taman merokok dan membuang sampah seenaknya. Satpam dan petugas keamanan acuh dan tidak menegur karena mereka juga ikut merokok. Mohon ditindak lanjuti secepatnya'
    'beginikah prosedur kerja yg benar?? geletakin tiang PJU sembarangan ?? harusnya kerja itu punya prosedur yg jelas, begitu dicopot seharusnya langsung diangkut. Begini ini kan mengganggu fungsi trotoar?? pengawasnya kerja apa gak sih?'
    'batu puing nya tolong dibersihkan diangkut biar terlihat bersih lingkungannya '
    'jalanan tercipta untuk lahan parkir , tolong  tindak tegaas pak , '
    'parkir liar para pengunjung mbloc memakan satu lajur jalan.Harus ditindak agar tidak terus menerus terjadi.'
    'Jalan Pisangan lama barat Depan pos PDIP keluar tol, posisi mobil memakan separuh jalan dan menganggu mobil masuk.'
    'Patokannya Alfamidi sumur batu depan SMPN 10 JAKARTA PUSAT, ini yg di resahkan di buat trotoar yang luas hasil nya NIHIL, karna tempat kita berjalan kaki sama saja tertutupi maupun di pagi, siang, sore dan malam. Mohon pemrov di selesaikan kegunaannya'
    'trotoar sempit dipasang pot besar. pejalan kaki hrs tirin ke jalan unt lewat. bahaya!'
    'ToT utk penggunaan aplikasi JAKI' 'Bendera liar'
    'parkir dan kaki lima liar di jalan BDN, ayo segera dibereskan dan dicegah sblm tambah besar dan jadi boomerang untuk pak anies'
    'butuh zebra cross untuk nyebrang dari tambal ban samping jembatan pegangsaan dua ke trotoar depan stasiun LRT'
    'tolong pangkas daun bagian bawah' 'operasi kali sunter'
    'Lurah Kayu manis, berserta Jajaran , Babinsa , Bhabinkamtibmas Kel. Kayu manis , Puskesmas Matraman Giat PSN Jumantik di RW.09 Kel. Kayu manis Matraman Jakarta timur'
    'sampah kanstain tolong diangkut dibersihkan '
    'pohon beringin dan seri tumbuh membahayakan pejalan kaki dan orang-orang yg ada di bawahnya, karena tumbuh di pinggir tebing,  sehingga dikhawatirkan rubuh dan juga mengganggu kabel telepon dan listrik. '
    'kabel yg semrawut sangat mengganggu pemandangan..'
    'kelurahan baru tepatnya di sepanjang jl masjid Al jadid telah melakukan perombakan dan perbaikan saluran air. perbaikan dilakukan oleh dinas terkait'
    'PELECEHAN thd rambu lalu lintas'
    'jalan rawa kedaung kober Rt 4 Rw 14 kelurahan cengkareng timur kec cengkareng jakarta barat, pohon sudah mati minta tolong untuk di tebang/di tumbangkan agar tidak terjadi roboh ketika angin kencang takut di khawatirkan menimpah rumah warga\n\nterima kasih'
    'kerja Bakti wargaTugu permai Rw 02 Kel Tugu Utara.\nsebelum banjir datang'
    'Trotoar dijajah terus. Lapor kesekian ratus sia"? '
    'patokannya depan klinik utama salamat medical center .\nsebelum stasiun Tebet.\n\nmohon dipangkas rentan tumbang'
    'ada sampah d jalanan hingga warga terganggu'
    'papan reklame Rimbo berijin? ' 'sampah rumput liar'
    'parkir derek liar di belakang Jakarta Islamic Centre, mengganggu kenyamanan'
    'Hasil kerja bakti di lokasi saluran kali gawe depan Masjid Al Muttaqin jalan Bakti 55'
    'pohon tumbang dikali..'
    "RENOVASI Kantor RW.08 Kebon Pala......mohon Do'anya."
    'tolong dipotong rumput liar sudah pada lebat '
    'pohon sudah lebat sampe keatap rumah, minta tolong dirampingkan'
    'Depan sekolah SMAN 75 Semper Barat'
    'lampu PJU Mati Sudah Hampir Dua Minggu Belum Juga Di Perbaiki Lokasi Di Jalan Kemang Utara IX RT 001 RW 01Kelurahan Duren Tiga Kecamatan Pamcoran Jaksel'
    'pohon rindang dan rawan patah..mohon ijin dinas kehutanan untuk di TL di jln.ampera II rt.08 rw.03 kel.rawamangun kec.pulogadung jakarta timur.'
    'rambu dilarang berhenti dan petunjuk jalan warna hijau terhalang ranting pohon'
    'sampah disaluran air dilingkungan rt 04 rw 03 yang terbawa arus hujan semalam'
    'papan reklame tidak tuntas dibongkar nya ... tolong tiang reklame dibongkar dibersihkan '
    'luar biasa, 2 baris jalan hanya untuk parkir sekolah SDK 6 penabur, SITUASI DI BUAT MACET. Mohon di tindaklanjuti aturan yg jelas. Di depan SDK 6 penabur kelapa gading.'
    'kanstain pembatas jalan rusak tolong diperbaiki dirapihkan permanen '
    'karung sampah / Bekas Lumpur berjejer di pinggir jalan  benda raya alpa'
    'KOMP UNJ BLOK BZ RT13 RW 02 No32C. tks...maju kotanya bahagia warganya'
    'Trotoar sepanjang jalan Paus Rawamangun , sudah rapi tapi digunakan oleh pedagang Makanan di malam hari jadi terlihat kotor.. mohon perhatiannya'
    'sore admin tolong di tindak mobil parkir sembarangan, hampir 24jam parkir di situ tolong di TL\nJalan Kran 2'
    'pohon depan rumah sudah terlalu besar depan jalan gg'
    'eh ad motor pak pol. contohin yg baik dong pak. brani TL gak nih???'
    'jl kerja bakti depan LBUK kampung makasar'
    'perlu nya peningkatan jalan karena selokan sudah berjalan lancar tapi jalan nya rendah ..depan jalan RT006)010 Kel tugu Utara kec koja'
    'Tamu hotel sll parkir dijalur sepeda jl rs fatmawati'
    'papan nama sekolah dan kelurahan miring disangga bambu ... tolong diperbaiki dirapihkan permanen '
    'pot rusak\ndidpn mesjid attaqwa'
    'pohon mangga di RT 14 RW 07 tlg di tebang karena musim hujan takut roboh menimpa rumah warga'
    'Jalan Kran II Kelurahan Gunung Sahari Selatan, Kecamatan Kemayoran .\nTolong mobil ini di tindak pak, mobil baru beli tapi gak punya parkira kalo bisa sepanjang jalan kran II mobil mobil di derek banyak mobil parkir se enaknya .\nTerima Kasih.'
    'PELECEHAN TERHADAP RAMBU LALU LINTAS'
    'sampah tolong d angkat dekat seketariat rw002'
    'pot tanaman menghalangi trotoar pejalan kaki tolong ditertibkan '
    'trotoar rusaj tanahnya amblas. di depan halte BPKP'
    'pintu menuju gedung parkir motor kantor walikota jakarta barat....engsel sdh patah...sangat berbahaya...pintu dr besi yg cukup berat..mohon TL'
    'halo admin tolong ditindak ya parkir liar di atas trotoar jalan Jaksa. terima kasih'
    'Sudah 3 hari PJU menyala terus. \nLokasi : Gg.  Hj.  Niot Rt.  011 Rw.  08 Lenteng Agung,  Jakarta Selatan.  \nPatokan: deket rumah pak RW 08'
    'mohon dibantu u buangannya'
    'lokasi di jalan makaliwe raya. terima kasih.'
    'pohon mati tolong dipotong dibersihkan saja biar terlihat lingkungannya bersih rapih '
    'mohon dipasang penerangan ... karena gelap dan banyak yang nongkrong di jembatan atau pinggir kali perbatasan RW 04 dan RW. 05 ... terletak di RT. 007 RW. 04'
    'epanjang jalan cililitan kecil 3 sampai jalan cililitan kecil 1 jakarta timur banyak mobil parkir liar di bahu jalan..padahal itu jalanan umum'
    'Trotoar yg sudah dibangun Pemda, selalu digunakan unt parkir kepentingan pribadi. Lokasi Jl. Cempaka Putih Tengah 33 Raya. Pemilik yg sama dengan CPT Raya no. 6. Sangat mengganggu dan melanggar peraturan peruntukan fasilitas umum. Mohon bisa ditertibkan..'
    'Bendera partai liar' 'depan RSCM Parkir liar'
    'tolong pangkas daun bagian bawah dan supaya rambu tidak tertutup'
    'got mampet'
    'mohon ijin kepada intansi terkait . kami sbagai pengurus wilayah rt 011/03 kel .kapuk kec.cengkarereng JAk.BAR. bahwa saluran air di wilayah kami sudah tidak berpungsi . kami berharap segera di tindak lajuti '
    'batu puing karung dll tolong diangkut dibersihkan biar lingkungan terlihat bersih dan rapih '
    'sampah kering tolong diangkut dibersihkan biar lingkungan terlihat bersih dan rapih ga terkesan kumuh '
    'jln pademangan 5 gang 22 RT 018/08 pohon mohon tebang habis akarnya merusak dinding gapura'
    'mohon dan tolong lampu pju yg mati di perbaiki sdh hampir enam bulan lbih lampu tsb blum jga di perbaiki. '
    'iklan reklame tolong ditertibkan ' 'parkiran milik pribadi ..'
    'Butuh topingan'
    'Permohonan pengadaan tempat sampah dua unit ukuran 120 liter,..untuk kerja bakti warga\n\nJl.Sunter Jaya VIB RT001 RW07 Blok L Kelurahan Sunter Jaya Kecamatan Tanjung Priok Jakarta Utara'
    'parkir sembarangan padahal jln sempit... mohon perhatiannya didepan RS dan Univ YARSI JAKPUS'
    'sampah ban tolong diangkut dibersihkan '
    'Belum ada tindakan dari Dinas terkait menengani Laporan JPO Buswy diJembatan Baru Cengkareng banyak yg rusak dan membahayakan Pengguna Jembatan Tersebut, Keluhan ini berdasarkan Permintaan Masyarakat yang sering melintas jembatan tersebut'
    'batu puing kanstain tolong diangkut dibersihkan '
    'baliho reklame ada ijinnya ga tolong ditertibkan dan dibongkar dibersihkan biar lingkungan terlihat bersih dan rapih '
    'cek perizinannya bila ijin bermasalah pajaknya ga dibayar proses bongkar saja.... jangan sampai terjadi pembiaran selama ini '
    'halo admin tolong tindak parkir liar di depan tempat makan ayam berempah paha dada sumur batu. Banyak parkir liar di atas trotoar yang baru selesai direnovasi. terima kasih'
    'Sampah di depan Gedung Galenium\n, di Jl Adityawarman Raya, Kebayoran Baru. Jakarta Selatan'
    'papan reklame ada ijinnya ga tolong di cek perizinannya dan pajak reklamenya... bila ijin dan pajak reklamenya bermasalah proses bongkar saja ... biar trotoar bersih berfungsi maksimal u pejalan kakinya '
    'Jl. Auri di samping gedung sopo dell mega kuningan\n\nJalan rusak, jika hujan banjir dikarenakan tidak ada drainase dijalan tersebut'
    'lokasi di jl. abdul rahman cibubur. terima kasih.'
    'Menggangu kabel2 listrik.lokasi pas di depan gereja katolik St Alfonsus'
    'kayu batu puingnya tolong diangkut dibersihkan ' 'kerja bakti '
    'Mohon tertibkan, depan sate kambing kasolo' 'sampah bengkel'
    'cek perizinannya dan pajak reklamenya... ga ada stiker merahnya tanda bayar pajak reklamenya . tolong ditertibkan jangan sampai terjadi pembiaran selama ini '
    'sampah kering dll tolong diangkut dibersihkan biar lingkungan terlihat bersih dan rapih '
    'di jl gg musholla rt 003 rw 015 no 4 kel cipinang muara kec jatinegara,jakarta timur ada sarang tawon dipohon mangganya sudah besar ukurannya mohon di bantu.'
    'segera di tindak lanjut.parkir liat menyebakban kemacetan.dan memakan trotoar hak pejalan kaki'
    'Lurah Kayu Manis Heru Suryonno SH menerangkan Aplikasi Jaki kepada kader PSN Jumantik RW.09 Kel. kayu manis Matraman Jakarta timur'
    'kp. kurus gang masjid RT 009 RW 006. jalur kali \n'
    'Apartemen Belmont Residences tdk ada saluran air penampung air hujan sehingga air hujan dari kawasan Apartemen turun ke jalan Kebon Jeruk Indah Utama menggenangi jalan warga.'
    'Batang pohon sudah mengenai kabel listrik.\nlokasi depan RPTRA Bawang Putih, Kebon Bawang'
    'parkir liar motor di atas trotoar '
    'tolong dinas pertamanan kecamatan tamansari utk menebang pohon atau dahan yg sdh lebat krn ada kabel PLN dibawahnya terima kasih']
    tokenizer = Tokenizer(num_words=1000, oov_token="<OOV>")
    tokenizer.fit_on_texts(report)
    test_word = "Pohon di sepanjang jalan Baladewa kiri sudah terlalu besar mengingat kondisi sekarang sudah masuk waktu penghujan..mohon untuk segera di sosialisasi'kan..posisi di sepanjang jalan Baladewa kiri depan Alfamart. trima kasih" 
    tw = tokenizer.texts_to_sequences([test_word])
    tw = pad_sequences(tw,maxlen=100)
    #prediction = int(model.predict(tw).round().item())
    prediction = model.predict(tw)
    return str(prediction)  

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
                  <div><pre>user    :               <input type="text" name="user"></pre></div>
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