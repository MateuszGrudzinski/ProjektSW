import cv2

# import the modules
import argparse
import json
from pathlib import Path
import os
from os import listdir
import numpy as np
from reszta_kodu import Tuning_functions
from reszta_kodu import Proccesing

parser = argparse.ArgumentParser()
parser.add_argument('images_dir', type=str)
parser.add_argument('results_file', type=str)
args = parser.parse_args()

images_dir = Path(args.images_dir)
results_file = Path(args.results_file)
images_paths = sorted([image_path for image_path in images_dir.iterdir() if image_path.name.endswith('.jpg')])
# get the path or directorye
znak_index_total = 0
json_dict = {}
for images in images_paths:
    img = cv2.imread(str(images))
    if img is None:
        print(f'Error loading image {images}')
        continue
    img = cv2.resize(img,(3968,2976))
    img_grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    pts, screenCnt = Proccesing.find_lincense_plate(img_grey)
    if screenCnt is None:
        print(f'No license plate detected')
        continue
    tablica = Proccesing.get_license_plate(pts,img)
    tablica_preprocesed = Proccesing.preprocces_license_plate(tablica)

    res = Proccesing.find_chars(tablica_preprocesed,tablica)

    """
    cv2.namedWindow("TABLICA_TH")

    Tuning_functions.Tablica_TH_tune("TABLICA_TH",tablica_filtered_HSV)
    """
    img = cv2.drawContours(img, [screenCnt], 0, (0, 255, 0), 20)

    cv2.imshow("IMG COLOR", cv2.resize(img, (int(img.shape[1]//4), int(img.shape[0]//4))))
    cv2.imshow("TABLICA", tablica)

    detected_string = Proccesing.parse_license_plate(res)

    json_dict[images.name] = detected_string
    #print(json_dict)
    cv2.waitKey(10)
with results_file.open('w') as output_file:
    json.dump(json_dict, output_file, indent=4)
cv2.destroyAllWindows()

