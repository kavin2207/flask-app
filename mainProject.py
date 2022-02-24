import os
import psycopg2
from PIL.ImageFile import ImageFile
from werkzeug.utils import secure_filename, redirect
from flask import Flask, render_template, request, url_for, flash, send_from_directory
import mysql.connector
import base64
from PIL import Image
import io
import MySQLdb
import json

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
# UPLOAD_FOLDER = 'C:\\Users\\abhbhatn\\PycharmProjects\\pythonProject\\images'
app = Flask(__name__)
app.config['SECRET_KEY'] = 'abhijeet'
app.config['UPLOAD_FOLDER'] = APP_ROOT

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# db Connection
mydb = psycopg2.connect(
    host= "abhijeet123098.mysql.pythonanywhere-services.com",
    user="abhijeet123098",
    password="gameabhijeet",
    database="abhijeet123098$test1"
)

mycursor = mydb.cursor()


# first
@app.route('/')
def home():
    return render_template('reg.html')


# input from reg.html form
@app.route('/valid', methods=['POST'])
def valid():
    fName = request.form.get('fName')
    lName = request.form.get('lName')
    gen = request.form.get('gen')
    sql = "INSERT INTO user (name, last, gender) VALUES (%s, %s,%s)"
    val = (fName, lName, gen)
    mycursor.execute(sql, val)
    mydb.commit()
    # record = mycursor.fetchall()
    return render_template('uploadProfile.html')


# for extension check
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploads/<name>')
def download_file(name):
    file_path=APP_ROOT+'\\outputImage\\'
    print(file_path)
    return send_from_directory(file_path,name)


# to check data
@app.route("/show", methods=["POST", "GET"])
def retriveImage():
    print("sssssss")
    if request.method == "GET":
        return render_template("Complete.html")
    id = request.form.get('uID')
    sql = "select * from user where id = {} ".format(id)
    #print(sql)
    # val = (destination_image_name)
    # print(val)
    mycursor.execute(sql, )
    record = mycursor.fetchall()
    file_name='img{}.jpg'.format(id)
    storeFile = APP_ROOT + '\\outputImage\\'+file_name
    #print("sssss : ", record, " : dhudn")
    img = record[0][4]
    binary_data = base64.b64decode(img)
    # Convert the bytes into a PIL image
    image = Image.open(io.BytesIO(binary_data))

    # Display the image
    rgb_im = image.convert('RGB')
    rgb_im.save(storeFile)
    return redirect(url_for('download_file', name=file_name))


# for image storage
@app.route('/uploadProfile', methods=['GET', 'POST'])
def upload_file():
    print(request.method)
    try:
        if request.method == 'POST':
            # retrive the latest ID
            q = "select name,id from user where id = (select MAX(id) from user)"
            mycursor.execute(q)
            result = mycursor.fetchall()
            Fname = result[0][0]
            uID = result[0][1]
            # check if the post request has the file part

            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # If the user does not select a file, the browser submits an
            # empty file without a filename.
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)

                file.save(os.path.join(app.config['UPLOAD_FOLDER']+'\\images', filename))
                #print("filename : ", filename)

                # upload to db
                # print(open(UPLOAD_FOLDER + '\\' + filename))
                #print("app : ", APP_ROOT)
                #print("root : ",APP_ROOT + "\\images\\" + filename)
                root_dir=APP_ROOT + "\\images"
                #print(os.path.exists(APP_ROOT))
                x = open(root_dir+"\\" + filename, 'rb').read()
                file = base64.b64encode(x)


                sql = "update user set profile_pic='{}' where id={}".format(file.decode(), uID)
                # print(open(UPLOAD_FOLDER+'\\'+filename))
                # val = (destination_image_name)
                # print(val)
                mycursor.execute(sql, )
                mydb.commit()

                return render_template('Complete.html', latestUID=uID, name=Fname)
    except OSError as err:
        print("OS error: {0}".format(err))
    except ValueError:
        print("Could not convert data to an integer.")
    except BaseException as err:
        print(f"Unexpected {err=}, {type(err)=}")
        raise

    return "done"


print("sksksk : ", app.url_map)
# main functiom or starting function
if __name__ == "__main__":
    app.run(debug=True)
