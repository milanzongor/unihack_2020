
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
    return
import os

import numpy as np
import argparse
import imutils
import cv2
import PyPDF2 as pypdf

from imutils.perspective import four_point_transform
from imutils import contours
from pdf2image import convert_from_path, convert_from_bytes
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)
from PyPDF2 import PdfFileReader, PdfFileWriter

PATH = './uploads'


def get_result_zip(pdfs, results):
  # todo result
  zipfile = ''
  return zipfile



def solve(file_path):
  pdf_reader = PdfFileReader(file_path, "rb")

  num_pages = pdf_reader.getNumPages()

  # todo save results to csv
  exam_results = []
  for i in range(num_pages):
    is_header_present()
  split_pdf(filename)

  zipfile = get_result_zip(pdfs_locations, results)
  return zipfile


def pdf2opencv(path_pdf):
  pil_images = convert_from_path(path_pdf, dpi=200)
  for pil_image in pil_images:
    open_cv_image = np.array(pil_image)
    # Convert RGB to BGR
  return open_cv_image[:, :, ::-1].copy()

def header_check(input_image):
  template = cv2.imread(PATH + "template.png",0)
  w, h = template.shape[::-1]

  res = cv2.matchTemplate(input_image,template,cv2.TM_CCOEFF_NORMED)
  threshold = 0.8
  loc = np.where( res >= threshold)
  if len(loc[0]) > 0:
    return True
  else:
    return False

def crop_header(input_image):
  template = cv2.imread(PATH + "template.png",0)
  w, h = template.shape[::-1]

  res = cv2.matchTemplate(input_image,template,cv2.TM_CCOEFF_NORMED)
  threshold = 0.8
  loc = np.where(res >= threshold)

  for pt in zip(*loc[::-1]):
      # cv2.rectangle(image, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)
      box = input_image[pt[1]:pt[1] + h, pt[0]:pt[0] + w] # [y, x]
  return box

def get_recognized_circles(cropped_header):
  cnts = cv2.findContours(cropped_header.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  cnts = imutils.grab_contours(cnts)
  questionCnts = []

  for c in cnts:
    (x, y, w, h) = cv2.boundingRect(c)
    ar = w / float(h)

    if w >= 20 and h >= 20 and ar >= 0.9 and ar <= 1.1:
      questionCnts.append(c)

  # top to bottom sort
  questionCnts = contours.sort_contours(questionCnts,method="top-to-bottom")[0]

  return questionCnts

def delete_outher_box(thresh):
  cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE)
  cnts = imutils.grab_contours(cnts)
  # print(len(cnts))

  cv2.drawContours(thresh, cnts, -1, (0, 0, 0), 3)
  return thresh

def get_student_id(questionCnts):
  student_id = 0
  # each question has 10 possible answers, to loop over the
  # question in batches of 10
  for (q, i) in enumerate(np.arange(0, len(questionCnts), 10)):
    # sort the contours for the current question from
    # left to right, then initialize the index of the
    # bubbled answer
    cnts = contours.sort_contours(questionCnts[i:i + 10])[0]
    bubbled = None

    # loop over the sorted contours
    for (j, c) in enumerate(cnts):
      # construct a mask that reveals only the current
      # "bubble" for the question
      mask = np.zeros(thresh.shape, dtype="uint8")
      cv2.drawContours(mask, [c], -1, 255, -1)

      # apply the mask to the thresholded image, then
      # count the number of non-zero pixels in the
      # bubble area
      mask = cv2.bitwise_and(thresh, thresh, mask=mask)
      total = cv2.countNonZero(mask)

      if bubbled is None or total > bubbled[0]:
        bubbled = (total, j)

    color = (0, 0, 255) # RED
    student_id += bubbled[1]*pow(10, 5-q)
    # print(student_id)
    cv2.drawContours(cropped_header, [cnts[bubbled[1]]], -1, color, 3)
  return student_id

def threshold_image(image):
  # apply Otsu's thresholding method to binarize the cropped_header
  return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
  return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
