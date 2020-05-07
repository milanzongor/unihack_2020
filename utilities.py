import csv
import os
import shutil
from zipfile import ZipFile
import PyPDF2 as pypdf
from PyPDF2 import PdfFileReader, PdfFileWriter

from image_processing import check_header, get_results

# from pdf2image import convert_from_path, convert_from_bytes # problems with poppler


PATH = './templates/'  # Toto nakonec potrebuju :D


def dummy_empty_zip(path):
    if not os.path.exists(path):
        os.makedirs(path)

    shutil.make_archive(path, 'zip', path)

    path_to_zip = path + ".zip"
    return path_to_zip


# TODO: split pdf from scanner and return path to sorted exams in zip
def process_scanned_pdf(path_to_token: str, path_to_csv_student_info: str):
    # create temp directory
    if not os.path.exists(path_to_token):
        os.makedirs(path_to_token)

    # split pdf info same name created dictionary
    split_pdf(path_to_token, path_to_csv_student_info)

    # make zip file
    shutil.make_archive(path_to_token, 'zip', path_to_token)

    # delete files and directory
    shutil.rmtree(path_to_token)

    path_to_zip = path_to_token + ".zip"
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
def process_template(filename_path: str):
    # merge two pdfs together. Use overlay template

    with open(filename_path + '.pdf', "rb") as inFile, open("static/assets/overlay_template.pdf", "rb") as overlay:
        original = pypdf.PdfFileReader(inFile)
        background = original.getPage(0)
        foreground = pypdf.PdfFileReader(overlay).getPage(0)

        # merge the first two pages
        background.mergePage(foreground)

        # add all pages to a writer
        writer = pypdf.PdfFileWriter()

        # writer.addPage(foreground)

        for i in range(original.getNumPages()):
            page = original.getPage(i)
            writer.addPage(page)

        # write everything in the writer to a file
        modified_filename = filename_path + "modified"

        with open(modified_filename + '.pdf', "wb") as outFile:
            writer.write(outFile)

        path_to_zip = modified_filename + ".zip"
        with ZipFile(path_to_zip, 'w') as zipObj:
            # TODO: Add multiple files to the zip
            zipObj.write(modified_filename + '.pdf')
        return path_to_zip


def process_page(page, file_path, csv_student_info):
    # print(page)
    temp_writer = PdfFileWriter()

    # bad for asynchronous
    # temp write to pdv to handle opencv
    temp_writer.addPage(page)

    with open(file_path + 'temp.pdf', 'wb') as out:
        temp_writer.write(out)

    is_header = check_header(file_path + 'temp.pdf')

    # print('Header')

    if not is_header:
        # print('returning header is false')
        os.remove(file_path + 'temp.pdf')
        return False, None

    student_results = get_results(file_path + 'temp.pdf')

    # print(f'RESULTS ------------- {student_results}')

    # remove temp pdf
    os.remove(file_path + 'temp.pdf')

    result = {
        "student_id": student_results[0],
        # "student_name": 'Karel',  # todo get it from table
        "skore": student_results[1],
        "znama": student_results[2],  # todo map grade to mark
    }

    return True, result


def split_pdf(file_path, csv_student_info):
    pdf_reader = PdfFileReader(file_path + '.pdf', "rb")

    num_pages = pdf_reader.getNumPages()
    pdf_writer = PdfFileWriter()

    exam_results = []
    for i in range(num_pages):
        page = pdf_reader.getPage(i)
        is_header, one_result = process_page(page, file_path, csv_student_info)
        if is_header:
            exam_results.append(one_result)
            # todo append more info into name
            pdf_writer.addPage(page)
            with open(file_path + '/' + str(one_result['student_id']) + '.pdf', 'wb') as out:
                pdf_writer.write(out)
            # Create new empty pdffilewriter
            pdf_writer = PdfFileWriter()
        else:
            pdf_writer.addPage(page)

    if len(exam_results) != 0:
        keys = exam_results[0].keys()
        with open(file_path + '/' + 'results.csv', 'w') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(exam_results)
