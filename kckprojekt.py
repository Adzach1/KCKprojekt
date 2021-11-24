import cv2 as cv
import numpy as np
from skimage.metrics import structural_similarity as ssim

def rescale(img, scale):
    width=int(img.shape[1]*scale)
    height=int(img.shape[0]*scale)
    dimensions=(width,height)
    return cv.resize(img, dimensions, interpolation=cv.INTER_AREA)

def rescale_card(img, width, height):
    dimensions=(width,height)
    return cv.resize(img, dimensions, interpolation=cv.INTER_AREA)

def image_sim(img1, img2):
    (score, diff) = ssim(img1, img2, full=True)
    return score

def crop_rotate(img, rect):
    rows, cols = img.shape[0], img.shape[1]
    angle = rect[2]
    matrix = cv.getRotationMatrix2D((cols/2,rows/2),angle,1)
    img = cv.warpAffine(img,matrix,(cols,rows))

    box = cv.boxPoints(rect)
    pts = np.int0(cv.transform(np.array([box]), matrix))[0]
    pts[pts < 0] = 0
    img=img[pts[1][1]:pts[0][1], pts[1][0]:pts[2][0]]
    w=abs(pts[0][1]-pts[1][1])
    h=abs(pts[2][0]-pts[1][0])
    return img, h, w

def load_img(path):
    img = cv.imread(path, cv.IMREAD_GRAYSCALE)
    img = rescale_card(img, 500, 500)
    #img = cv.cvtColor(img, cv.COLOR_BGR2GRAY) # convert to grayscale
    img = cv.subtract(255,img)
    retval, img = cv.threshold(img, 100, maxval=255, type=cv.THRESH_BINARY_INV)
    return img

def find_cards(img):
    cards=[]
    contours, hierarchy = cv.findContours(img,cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
    for cont in contours:
        trect = cv.minAreaRect(cont)
        tarea = trect[1][0]*trect[1][1]
        if tarea > 10000:
            cards.append(trect)
    rdy_cards=[]
    for card in cards:
        img1, width, height = crop_rotate(img, card)
        if (width > height):
            img1 = cv.rotate(img1, cv.ROTATE_90_CLOCKWISE)
        img1=rescale_card(img1, 210, 300)
        rdy_cards.append(img1)
    return rdy_cards

def crop_symbol(cards):
    symbols=[]
    for card in cards:
        card=card[10:50,8:34]
        symbols.append(card)
    return symbols

def crop_color(cards):
    colors=[]
    for card in cards:
        card=card[50:80,8:34]
        colors.append(card)
    return colors

def patterns():
    tab_sym=['2wzor.jpg', '3wzor.jpg', '4wzor.jpg', '5wzor.jpg', '6wzor.jpg', '7wzor.jpg', '8wzor.jpg', '9wzor.jpg', '10wzor.jpg', 'jwzor.jpg', 'dwzor.jpg', 'kwzor.jpg', 'awzor.jpg']
    tab_col=['pikwzor.jpg', 'karowzor.jpg', 'kierwzor.jpg', 'treflwzor.jpg']
    sym_patt=[]
    col_patt=[]
    for path in tab_sym:
        img_patt = cv.imread(path, cv.IMREAD_GRAYSCALE)
        #img_patt = cv.cvtColor(img_patt, cv.COLOR_BGR2GRAY)  # convert to grayscale
        img_patt = cv.subtract(255, img_patt)
        retval, img_patt = cv.threshold(img_patt, 100, maxval=255, type=cv.THRESH_BINARY_INV)
        sym_patt.append(img_patt)
    for path in tab_col:
        img_patt = cv.imread(path, cv.IMREAD_GRAYSCALE)
        #img_patt = cv.cvtColor(img_patt, cv.COLOR_BGR2GRAY)  # convert to grayscale
        img_patt = cv.subtract(255, img_patt)
        retval, img_patt = cv.threshold(img_patt, 100, maxval=255, type=cv.THRESH_BINARY_INV)
        col_patt.append(img_patt)
    return sym_patt, col_patt
def recognize_cards(symbols, colors, sym_patt, col_patt):
    number_of_cards=0
    list_of_cards=[]
    for i in range(len(symbols)):
        best_sym = 0
        sym_sim=image_sim(symbols[i],sym_patt[0])
        best_col = 0
        col_sim = image_sim(colors[i], col_patt[0])
        for j in range(len(sym_patt)):
            sim=image_sim(symbols[i],sym_patt[j])
            print(sim)
            if(sim>sym_sim):
                best_sym=j
                sym_sim=sim
        print('----------------------------')
        for j in range(len(col_patt)):
            sim=image_sim(colors[i],col_patt[j])
            print(sim)
            if(sim>col_sim):
                best_col=j
                col_sim=sim
        print('-------------------------------')
        if(sym_sim>0.3 and col_sim>0.3):
            rec_card=dictionary(best_sym,best_col)
            cv.imshow("wzor1", sym_patt[best_sym])
            cv.imshow("wzor2", col_patt[best_col])
            list_of_cards.append(rec_card)
            number_of_cards+=1
    print("Number of cards: "+str(number_of_cards))
    if(number_of_cards>0):
        print("List of cards:")
    for card in list_of_cards:
        print(card)

def dictionary(sym, col):
    if(sym==0):
        symbol='2 '
    elif(sym==1):
        symbol='3 '
    elif (sym == 2):
        symbol = '4 '
    elif (sym == 3):
        symbol = '5 '
    elif (sym == 4):
        symbol = '6 '
    elif (sym == 5):
        symbol = '7 '
    elif (sym == 6):
        symbol = '8 '
    elif (sym == 7):
        symbol = '9 '
    elif (sym == 8):
        symbol = '10 '
    elif (sym == 9):
        symbol = 'WALET '
    elif (sym == 10):
        symbol = 'DAMA '
    elif (sym == 11):
        symbol = 'KROL '
    elif (sym == 12):
        symbol = 'AS '
    if(col==0):
        color='PIK'
    elif(col==1):
        color='KARO'
    elif (col == 2):
        color = 'KIER'
    elif (col == 3):
        color = 'TREFL'
    rec_card=symbol+color
    return rec_card



img=load_img('hard8.jpg')
cv.imshow("idk", img)
#cv.imwrite("krok2.jpg", img)
sym_patt, col_patt=patterns()
cards=find_cards(img)
#cv.imwrite("krok3.jpg", cards[0])
cv.imshow("1231312", cards[0])
symbols=crop_symbol(cards)
#cv.imwrite("krok4.jpg", symbols[0])
colors=crop_color(cards)
#cv.imwrite("krok5.jpg", colors[0])
recognize_cards(symbols,colors,sym_patt,col_patt)
cv.imshow("wynik1", symbols[0])
cv.imshow("wynik2", colors[0])
#cv.imshow("wynik3", symbols[1])
#cv.imshow("wynik4", colors[1])
cv.waitKey(0)