import os
import random

# from secrets import token_urlsafe
from flask import Flask, flash, request, redirect, render_template, send_file
from flask_scss import Scss
import string

import utilities

UPLOAD_FOLDER = '/tmp/uploads_poslitesty/'
ALLOWED_EXTENSIONS = {'pdf', 'csv'}

app = Flask(__name__)
# !!! Dont forget to generate it manually nex time, if this shit doesnt work !!!
Scss(app, static_dir='static', asset_dir='/assets')
app.secret_key = "posielaj vsetky testy 223 unihack"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 40 * 1024 * 1024


def token_urlsafe(num):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(num))


def allowed_file(file_name):
    return '.' in file_name and \
           file_name.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/uploads/" + '<filename>')
def uploaded_file(filename):
    return send_file(filename, as_attachment=True, attachment_filename='vysledek.zip')


@app.route("/uploads/overlay_template")
def download_template():
    return send_file("static/assets/overlay_template.pdf", as_attachment=True, attachment_filename='podpisova_hlavicka.pdf')


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if 'file_scan' in request.files:
            file_scan = request.files['file_scan']
            if file_scan.filename == '':
                flash('Žádná část souboru')
                return redirect(request.url)
            if file_scan and allowed_file(file_scan.filename):
                token = token_urlsafe(32)
                path_to_token = os.path.join(app.config['UPLOAD_FOLDER'], token)
                file_scan.save(path_to_token + ".pdf")
                path_to_zip = utilities.process_scanned_pdf(path_to_token, "")
                return uploaded_file(path_to_zip)
        elif 'file_header' in request.files:
            file_header = request.files['file_header']
            if file_header.filename == '':
                flash('Žádná část souboru')
                return redirect(request.url)
            if file_header and allowed_file(file_header.filename):
                token = token_urlsafe(32)
                path_to_token = os.path.join(app.config['UPLOAD_FOLDER'], token)
                file_header.save(path_to_token + ".pdf")
                path_to_zip = utilities.process_template(path_to_token)
                return uploaded_file(path_to_zip)
        else:
            flash('Žádná část souboru')
            return redirect(request.url)

    return render_template('index.html')


if __name__ == '__main__':
    app.run()
