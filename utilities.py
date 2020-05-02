from zipfile import ZipFile


# TODO: split pdf from scanner and return path to sorted exams in zip
def process_scanned_pdf(path_to_pdf: str):
    # TODO: split pdf

    path_to_zip = path_to_pdf + ".zip"
    with ZipFile(path_to_zip, 'w') as zipObj:
        # TODO: Add multiple files to the zip
        zipObj.write(path_to_pdf + ".pdf")
    return path_to_zip


# TODO: OPTIONAL: given students list (f1) and template of exam (f2)
#  return path to zipped pdfs with sticked qr code unique per each student
def process_students_and_template(filename1: str, filename2: str):
    # if str.endswith(filename1, ".csv") and str.endswith(filename2, ".pdf"):

    path_to_zip = filename1 + filename2 + ".zip"
    with ZipFile(path_to_zip, 'w') as zipObj:
        # TODO: Add multiple files to the zip
        zipObj.write(filename1 + ".pdf")
    return path_to_zip



# TODO: stick template to given pdf
#  return path to pdf with sticked number form
def process_template(filename: str):
    return