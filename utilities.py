import os

import csv
import numpy as np
import argparse
import imutils
import cv2
import PyPDF2 as pypdf
import shutil
import time

from imutils import contours
from pdf2image import convert_from_path, convert_from_bytes
from imutils.perspective import four_point_transform
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)
from PyPDF2 import PdfFileReader, PdfFileWriter
from zipfile import ZipFile

PATH = './templates/'


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
    # shutil.rmtree(path_to_token)

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
    return


def process_page(page, file_path, csv_student_info):
    print(page)
    temp_writer = PdfFileWriter()

    # bad for asynchronous
    # temp write to pdv to handle opencv
    temp_writer.addPage(page)

    with open(file_path + 'temp.pdf', 'wb') as out:
        temp_writer.write(out)

    is_header = check_header(file_path + 'temp.pdf')

    print('1111111111111111')

    if not is_header:
        return False, None

    print('222222222222')

    student_results = get_results(file_path + 'temp.pdf')

    print(f'RESULTS ------------- {student_results}')

    # remove temp pdf
    os.remove(file_path + 'temp.pdf')

    result = {
        "student_id": student_results[0],
        # "student_name": 'Karel',  # todo get it from table
        "score": student_results[1],
        "grade": student_results[2],  # todo map grade to mark
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
            print(f'Writing!!!!! to {file_path + "/" + str(one_result["student_id"])}')
            with open(file_path + '/' + str(one_result['student_id']) + '.pdf', 'wb') as out:
                pdf_writer.write(out)
            # Create new empty pdffilewriter
            pdf_writer = PdfFileWriter()
        pdf_writer.addPage(page)

    keys = exam_results[0].keys()
    with open(file_path + '/' + 'results.csv', 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(exam_results)


# --------------------------- OpenCV and image processing ----------------------------------

# todo scalable
def get_results(pdf_path):
    rectangle_elements, gray_cropped = parse_header_elements(pdf_path);

    student_id_table = four_point_transform(gray_cropped, rectangle_elements[0].reshape(4, 2))
    student_id_table = threshold_image(student_id_table)
    student_id_table = delete_outher_box(student_id_table)
    student_id = get_number(student_id_table, 6, 10)
    print(student_id)

    exam_points_table = four_point_transform(gray_cropped, rectangle_elements[1].reshape(4, 2))
    exam_points_table = threshold_image(exam_points_table)
    exam_points_table = delete_outher_box(exam_points_table)
    exam_points = get_number(exam_points_table, rows=2, cols=10)
    print(exam_points)

    grade_table = four_point_transform(gray_cropped, rectangle_elements[2].reshape(4, 2))
    grade_table = threshold_image(grade_table)
    grade_table = delete_outher_box(grade_table)
    grade = get_number(grade_table, rows=1, cols=6)
    print(grade)

    return [student_id, exam_points, grade]

def pdf2opencv(path_pdf):
    # TODO: prerobit mozno do ineho, nech nepouzivame opencv
    pil_images = convert_from_path(path_pdf, dpi=200)
    for pil_image in pil_images:
        open_cv_image = np.array(pil_image)
        # Convert RGB to BGR
    return open_cv_image[:, :, ::-1].copy()


def delete_outher_box(thresh):
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    print("Number of contours:", len(cnts))

    if len(cnts) == 1:
        cv2.drawContours(thresh, cnts, -1, (0, 0, 0), 3)
    return thresh


def get_contours(image):
    cnts = cv2.findContours(image.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return imutils.grab_contours(cnts)


def get_recognized_circles(cropped_header):
    cnts = get_contours(cropped_header)
    questionCnts = []

    for c in cnts:
        (x, y, w, h) = cv2.boundingRect(c)
        ar = w / float(h)

        if w >= 20 and h >= 20 and ar >= 0.9 and ar <= 1.1:
            questionCnts.append(c)

    # top to bottom sort
    questionCnts = contours.sort_contours(questionCnts, method="top-to-bottom")[0]

    return questionCnts


def threshold_image(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]


def get_number(thresh, rows, cols):
    number = 0

    questionCnts = get_recognized_circles(thresh)

    for (q, i) in enumerate(np.arange(0, len(questionCnts), cols)):
        cnts = contours.sort_contours(questionCnts[i:i + cols])[0]
        bubbled = None

        for (j, c) in enumerate(cnts):
            mask = np.zeros(thresh.shape, dtype="uint8")
            cv2.drawContours(mask, [c], -1, 255, -1)

            mask = cv2.bitwise_and(thresh, thresh, mask=mask)
            total = cv2.countNonZero(mask)

            if bubbled is None or total > bubbled[0]:
                bubbled = (total, j)

        number += bubbled[1] * pow(10, rows - 1 - q)
    return number


def check_header(pdf_path):
    rectangle_elements, _ = parse_header_elements(pdf_path)
    if len(rectangle_elements) >= 3:
        return True
    else:
        return False


def parse_header_elements(pdf_path):
    image = pdf2opencv(pdf_path)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 75, 200)

    # get dimensions of the page
    (x, y, w, h) = cv2.boundingRect(edged)
    edged_cropped = edged[y:y + h // 5, :]
    gray_cropped = gray[y:y + h // 5, :]

    cnts = get_contours(edged_cropped)
    docCnt = None

    print("[INFO] --- Number of contours found:", len(cnts))

    docCntArr = []

    if len(cnts) > 0:
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

        for c in cnts:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)

            if len(approx) == 4 and cv2.contourArea(c) > 9000:

                docCntArr.append(approx)
    return docCntArr, gray_cropped
