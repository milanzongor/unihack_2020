from imutils import contours
from imutils.perspective import four_point_transform
import cv2
import imutils
import numpy as np
from pdf2image import convert_from_path

# todo scalable
def get_results(pdf_path):
    rectangle_elements, gray_cropped = parse_header_elements(pdf_path)

    student_id_table = four_point_transform(gray_cropped, rectangle_elements[0].reshape(4, 2))
    student_id_table = threshold_image(student_id_table)
    student_id_table = delete_outher_box(student_id_table)
    student_id = get_number(student_id_table, 6, 10)

    exam_points_table = four_point_transform(gray_cropped, rectangle_elements[1].reshape(4, 2))
    exam_points_table = threshold_image(exam_points_table)
    exam_points_table = delete_outher_box(exam_points_table)
    exam_points = get_number(exam_points_table, rows=2, cols=10)

    grade_table = four_point_transform(gray_cropped, rectangle_elements[2].reshape(4, 2))
    grade_table = threshold_image(grade_table)
    grade_table = delete_outher_box(grade_table)
    grade = get_number(grade_table, rows=1, cols=6)

    return [student_id, exam_points, grade]


def pdf2opencv(path_pdf):
    pil_images = convert_from_path(path_pdf, dpi=200)
    for pil_image in pil_images:
        open_cv_image = np.array(pil_image)
        # Convert RGB to BGR
    return open_cv_image[:, :, ::-1].copy()


def delete_outher_box(thresh):
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

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
        print('Header is ok')
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

    docCntArr = []

    if len(cnts) > 0:
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

        for c in cnts:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)

            if len(approx) == 4 and cv2.contourArea(c) > 9000:
                print('IS OK !!!!!!!!!!!!!!!!!!')
                docCntArr.append(approx)
    return docCntArr, gray_cropped
