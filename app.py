import os
from secrets import token_urlsafe

from flask import Flask, flash, request, redirect, render_template, send_from_directory, send_file
from flask_scss import Scss

import utilities

UPLOAD_FOLDER = './static/uploads/'
ALLOWED_EXTENSIONS = {'pdf', 'csv'}

app = Flask(__name__)
# !!! Dont forget to generate it manually nex time, if this shit doesnt work !!!
Scss(app, static_dir='static', asset_dir='assets')
app.secret_key = "posielaj vsetky testy 223 unihack"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024


def allowed_file(file_name):
    return '.' in file_name and \
           file_name.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
                print(path_to_token)
                file_scan.save(path_to_token + ".pdf")
                path_to_zip = utilities.process_scanned_pdf(path_to_token, "")
                print('file_scan')
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
                # TODO: change dummy to useful
                path_to_zip = utilities.process_template(path_to_token)
                # path_to_zip = utilities.dummy_empty_zip(path_to_token)
                print('file_header')
                return uploaded_file(path_to_zip)
        else:
            flash('Žádná část souboru')
            return redirect(request.url)

    return render_template('index.html')


@app.route(UPLOAD_FOLDER[1:] + '<filename>')
def uploaded_file(filename):
    print(filename)
    # return send_from_directory(UPLOAD_FOLDER, filename)
    return send_file(filename, as_attachment=True, attachment_filename='vysledek.zip')


@app.route('/upload/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        # if file and allowed_file(file.filename): # previous
        if file:
            token = token_urlsafe(32)
            # instead of saving file with original name, create random token
            path_to_token = os.path.join(app.config['UPLOAD_FOLDER'], token)
            file.save(path_to_token + ".pdf")

            path_to_csv_student_info = ''  # todo NEED TO GET CSV FROM SERVER

            # gerenate zip inside
            path_to_zip = utilities.process_scanned_pdf(path_to_token, path_to_csv_student_info)

            # todo delete zip afterwards - some kind of garbage collector?

            return uploaded_file(path_to_zip)
    return render_template('templates_/upload.html')


@app.route('/upload_clean/', methods=['GET', 'POST'])
def upload_clean():
    if request.method == 'POST':
        print(request.__dict__)
        # check if the post request has the file part
        if 'file1' not in request.files or 'file2' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file1 = request.files['file1']
        file2 = request.files['file2']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file1.filename == '' or file2.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if (file1 and allowed_file(file1.filename)) and (file2 and allowed_file(file2.filename)):
            filename1 = token_urlsafe(32)
            filename2 = token_urlsafe(32)
            file1.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
            file2.save(os.path.join(app.config['UPLOAD_FOLDER'], filename2))

            filename_zip = utilities.process_students_and_template(filename1, filename2)

            return uploaded_file(filename_zip)
    return render_template('templates_/upload_clean.html')


@app.route('/upload_template/', methods=['GET', 'POST'])
def upload_template():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        # if file and allowed_file(file.filename): # previous
        if file:
            # filename = secure_filename(file.filename) # previous
            token = token_urlsafe(32)
            filename = token + ".pdf"
            # instead of saving file with original name, create random token
            path_to_pdf = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path_to_pdf)

            filename_zip = utilities.process_template(path_to_pdf)

            # return redirect(url_for(os.path.join(app.config['UPLOAD_FOLDER'], filename + ".zip")))
            # return redirect("../" + UPLOAD_FOLDER + filename + ".zip")
            return uploaded_file(filename_zip)
    return render_template('templates_/upload.html')


if __name__ == '__main__':
    app.run()
