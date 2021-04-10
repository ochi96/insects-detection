import os
import glob
import cv2
from flask import Flask, render_template, flash, redirect, url_for, Response, request
from werkzeug.utils import secure_filename
from .model import insect_detection
from .insect_info import damage_info

app = Flask(__name__)

UPLOAD_FOLDER = "static/img/"
analysed_images_path = "static/img2/"
app.config['SECRET_KEY'] = "amateurstalktacticsprofessionalstalklogistics"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/",methods=['GET'])
def index():
    '''entry point of the application'''
    return render_template("layout.html")

@app.route('/', methods=['POST'])
def upload_file():
    '''file validation'''
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
            flash('File uploaded successfully')
            return redirect(url_for('detect_insect', filename=filename))
        else:
            flash('Allowed files are png, jpeg or jpg')
            return redirect(request.url)

@app.route('/detect/<filename>')
def detect_insect(filename, inter=cv2.INTER_AREA):
    '''detecting insect and providing info on associated damage'''
    list_of_files = glob.glob(UPLOAD_FOLDER+'*')
    latest_file = max(list_of_files, key=os.path.getctime)
    results, processed_image = insect_detection.detect(latest_file)
    selected_insect_info = insect_damage(results)
    resized_image = cv2.resize(processed_image, (500,500), interpolation=inter)
    cv2.imwrite(analysed_images_path + filename, cv2.cvtColor(resized_image, cv2.COLOR_RGB2BGR))
    return render_template('detect.html', results = results, selected_insect_info = selected_insect_info, filename=filename)


def insect_damage(results):
    '''retrieving detected info from "database" '''
    label_name = results[0].label
    info = damage_info.damage_info()
    selected_insect_info = [0]
    for item in info:
        if item['name']==label_name:
            stage = item['stage']
            damage = item['damage']
            photos = item['damage_photos']
            selected_insect_info.extend([stage, damage, photos])

    return selected_insect_info


if __name__ == "__main__":
    app.debug = False
    port = int(os.environ.get('PORT', 33507))
    waitress.serve(app, port=port)
