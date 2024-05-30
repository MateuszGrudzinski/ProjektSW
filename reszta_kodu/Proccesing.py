import cv2
import numpy as np
import os
def find_lincense_plate(img):
    """Rozmycie tablicy filtrem medianowym, następnie wykorzystanie progowania adaptacyjnego w celu z progowania obrazów w różnych
    warunkahc oświetleniowych, morflologia w celu domknięcia konturów. kontury sortowane są od największego do najmniejszego następie mierzona jest ich długość
    oraz dokonywana jest aproksymacja kształtu. Jeżeli kontur udało się opisać przy pomocy 4 punktów nie zmieniając jego rozmiaru o więcej niż 1,2%
    zakładamy iż ten kontur jest tablicą."""
    cv2.medianBlur(img, 11, img)
    th3 = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 41,
                                5)
    kernel = np.ones((3,1))
    cv2.morphologyEx(th3, dst=th3, op=cv2.MORPH_CLOSE, kernel=kernel, iterations=5)
    contours, hierarchy = cv2.findContours(th3, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.012* peri, True)
        if len(approx) == 4:
            screenCnt = approx
            break
    pts = approx[:,0,:]
    return pts, screenCnt
def get_license_plate(pts,img):
    """Z znalezionych punktów tablicy, sortuje odpowiednio wierzchołki a następnie prostuje znaezioną tablicę, przy pomocy
    przekształcenia perspektywicznego"""
    pts_sorted = pts[pts[:, 0].argsort()]
    pts_left = pts_sorted[:2,:]
    pts_left = pts_left[pts_left[:, 1].argsort()]
    pts_right = pts_sorted[2:, :]
    pts_right = pts_right[pts_right[:, 1].argsort()]

    pts1 = np.float32([pts_left[0],pts_right[0], pts_left[1], pts_right[1]])
    pts2 = np.float32([[0, 0], [520, 0], [0, 114], [520, 114]])

    M = cv2.getPerspectiveTransform(pts1, pts2)

    tablica = cv2.warpPerspective(img, M, (520, 114))
    return tablica

def preprocces_license_plate(img):
    """
    Przygotowanie znalezionej tablicy do dalszej analizy. Rozmycie przy pomocy filtru medianowego, progowanie po value
    w przestrzeni HSV, wartości progów dobrane przy pomocy funckji z pliku Tuning_functions. Dodatkowa morfologia w celu
    zamknięcia konturów tablicy.
    """
    tablica_filtered = cv2.medianBlur(img, 5)
    tablica_filtered_HSV = cv2.cvtColor(tablica_filtered, cv2.COLOR_BGR2HSV)
    tablica_closed = cv2.cvtColor(tablica_filtered,cv2.COLOR_BGR2GRAY).copy()
    lower_hsv_c = np.array([0, 0, 120])
    higher_hsv_c = np.array([179, 255, 255])
    tablica_thresholded = cv2.inRange(tablica_filtered_HSV, lower_hsv_c, higher_hsv_c)
    kernel = np.ones((1, 3), np.uint8)
    cv2.morphologyEx(tablica_thresholded, dst=tablica_closed, op=cv2.MORPH_CLOSE, kernel=kernel, iterations=3)
    Mask = cv2.bitwise_not(tablica_closed)
    return Mask

def find_chars(img_preprocesed,img):
    """
    Znajdywanie znaków na tablicy odbywa się poprzez znalezienie odpowiednich konturów. Kontury te sortowane są w kolejności
    Występowania na obrazie od lewej do prawej. Odpowiedni kontur musi mieć dopuszczalną powierzchnię, szerokość oraz wysokość aby uznany został za literę.
    """
    contours, hierarchy = cv2.findContours(img_preprocesed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:15]

    rect_areas = []
    for c in contours:
        (x, y, w, h) = cv2.boundingRect(c)
        rect_areas.append(w * h)
    avg_area = np.mean(rect_areas)
    res = []
    order = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cnt_area = w * h
        if cnt_area > 0.15 * avg_area and w < 75 and h > 60:
            resB = img[y:(y + h), x:(x + w), 0]
            resG = img[y:(y + h), x:(x + w), 1]
            resR = img[y:(y + h), x:(x + w), 2]
            res.append(cv2.merge([resB, resG, resR]))
            order.append(x)
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        # cv2.drawContours(drawing, contours, i, (0, 255, 255), 2)
    order, res = zip(*sorted(zip(order, res)))
    return res

def parse_license_plate(res):
    #Templete matching wykorzystywany do rozpoznawania znaków, funcja jako wejście przyjmuje listę znaków wykrytych na tablicy.
    znaki_dir = "dane/Znaki_do_matchingu_2/"
    dict = {}
    detected_string = ""
    index = 0
    for r in res:
        result = []
        for znaki in os.listdir(znaki_dir):
            dict[str(index)] = znaki
            index += 1
            znak = cv2.imread(znaki_dir + znaki)
            TM = cv2.matchTemplate(cv2.resize(r, (50, 100)), cv2.resize(znak, (50, 100)), cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(TM)
            # print(znaki +": " + str(max_val))
            result.append(max_val)
        index_max = result.index(max(result))
        detected_string += dict[str(index_max)][0]
        #cv2.imwrite("dane/Znaki/" + "Znak_" + str(znak_index_total) + ".jpg", r)
        #znak_index_total += 1
    return detected_string