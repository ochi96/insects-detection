
import os
import glob
import cv2
from flask import Flask, render_template, flash, redirect, url_for, Response, request
from werkzeug.utils import secure_filename
from .model import insect_detection

app = Flask(__name__)

UPLOAD_FOLDER = "static/img/"
analysed_images_path = "static/img2/"
app.config['SECRET_KEY'] = "amateurstalktacticsprofessionalstalklogistics"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER                 #folder to upload the files
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024         #setting maximum file size to 16MB
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])      

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def resize_image(image, height=None, width=None, inter=cv2.INTER_AREA):
    image = cv2.imread('E:/uploads/5110009.jpg')
    resized_image = cv2.resize(image, (500,500), interpolation=inter)
    cv2.imwrite('E:/uploads/555.jpg', resized_image)
    return resized_image

@app.route("/")
def index():
    return render_template("layout.html")

@app.route('/', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('file uploaded successfully')
            return render_template('layout.html', filename=filename)
        else:
            flash('Allowed files are png, jpeg or jpg')
            return redirect(request.url)

@app.route('/detect/<filename>')
def detect_insect(filename, inter=cv2.INTER_AREA):
    list_of_files = glob.glob(UPLOAD_FOLDER+'*')
    latest_file = max(list_of_files, key=os.path.getctime)
    processed_image = insect_detection.detect(latest_file)
    resized_image = cv2.resize(processed_image, (500,500), interpolation=inter)
    cv2.imwrite(analysed_images_path+filename, cv2.cvtColor(resized_image, cv2.COLOR_RGB2BGR))
    return redirect(url_for('static', filename='img2/' + filename), code=301)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port = 8090)
