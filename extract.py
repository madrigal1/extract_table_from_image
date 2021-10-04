from math import sqrt,ceil,floor

import pytesseract
import argparse
import cv2
import os
import re
import csv

try:
    from PIL import Image
except ImportError:
    import Image

ap =argparse.ArgumentParser()
ap.add_argument("-i","--image",required=True,help="path to image to be ocr'ed")
ap.add_argument("-p","--preprocess",type=str,default="thresh",help="type of preprocessing to be done")
args = vars(ap.parse_args())
#print(args)


#load example image into mem and convert it into gray scale
image = cv2.imread(args["image"])
gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)


#check to see if we need to apply threshholding
if args["preprocess"] == "thresh":
    gray=cv2.threshold(gray,0,255,
        cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1] # to seprate foregraound from background
elif args["preprocess"] == "blur":
    gray = cv2.medianBlur(gray,3) # reduce salt and peper noise


filename = "{}.png".format(os.getpid())
cv2.imwrite(filename,gray)

#load image and fed to tesseract
#tessdata_dir_config = r'--tessdata-dir "/usr/share/tessdata/"'
text = pytesseract.image_to_string(Image.open(filename))
os.remove(filename)
#print(text)
words = re.split(r'[\s | j]',text)
def remove_punctuation(word):
    return re.sub(r'[|!?_:;,"\[()-]', "", word)

words_striped = list(map(remove_punctuation,words))
single_row = [word for word in words_striped if len(word)> 0]
def oned_to_2d(arr,num_columns):
    res = []
    temp = []
    for i in range(0,len(arr)):
        if len(temp) >= num_columns:
            if i != 0 and temp[0] != "age":
                if temp[2] == "ves":
                    temp[2] = "yes"
                ss = len(temp[0])
                value = temp[0]
                temp.pop(0)
                if ss > 5:
                    interval= value.split("...")
                    assert(len(interval) == 2)
                    temp.insert(0,interval[1])
                    temp.insert(0,interval[0])
                elif ss > 3 and ss <=5:
                    temp.insert(0, re.sub(r"[^0-9]", "", str(value)))
                    temp.insert(0, str(-1000000000))
                elif ss <= 3:
                    temp.insert(0, str(1000000000))
                    temp.insert(0, re.sub(r"[^0-9]", "", str(value)))
            else:
                temp.remove("age")
                temp[-2] = "credit_rating"
                temp.insert(0,"age_end")
                temp.insert(0,"age_start")
            res.append(temp)
            temp = []
        temp.append(arr[i])
    return res
result = oned_to_2d(single_row,5)
for row in result:
    for val in row:
        print(str(val)+" ",end=" "),
    print()

with open("data.csv","w+") as my_csv:
    csvWriter = csv.writer(my_csv,delimiter=',')
    csvWriter.writerows(result)



#show output image
# cv2.imshow("Image",image)
# cv2.imshow("Output",gray)
# cv2.waitKey(0)