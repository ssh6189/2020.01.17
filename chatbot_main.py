from flask import Flask, escape, request
import pickle
import pprint
import urllib
import numpy as np
import math
import cv2
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

#set FLASK_APP=<파일명>.py
#flask run
#db가 바뀔때마다 바로바로 쓰면, 안전하지만, 성능은 떨어진다.
#주기적으로 저장,
app = Flask(__name__) #플라스크를 실행하면, 앱이 만들어진다.

db = {}
namecard_db = []
id = 0

@app.route('/users', methods = ['POST'])
def create_user():
    global id
    body = request.json

    print(body)
    body ['id'] = id
    #body = ....
    #todo body에 id를 넣어준다.


    db[str(id)]=body
    id = id + 1
    print(db)
   # pickle.dump('./db.bin')
    return body


@app.route('/users/<id>', methods = ['GET'])
def select_user(id):
    if id not in db:
        return {}, 404
    print(db)
    return db[id]

@app.route('/users/<id>', methods = ['DELETE'])
def delete_user(id):
   # pickle.dump('./db.bin')
    del db[str(id)]
    return db

@app.route('/users/<id>', methods = ['PUT'])
def update_user(id):
    body = request.get_json()
    if id in db.keys():
        db[str(id)].update(body)
    else:
        db[str(id)]=body
    return db

@app.route('/')#uri부분
def hello():
    name = request.args.get("name", "World")
    return f'Hello, {escape(name)}!'

@app.route('/hi', methods = ['GET', 'POST'])
def hi():
    return {
        "version":"2.0",
        "template":{
            "outputs":[
                {
                    "simpleText":{
                        "text":"서환01 : 반가워~(발그레)."
                    }
                }
            ]
        }
    }


@app.route('/br', methods=['GET', 'POST'])
def bar():  
    global namecard_db           
    with open('namecard_db.pickle', 'rb') as f:
        namecard_db = pickle.load(f)

    print(namecard_db[0][1])
    return {
	"version": "2.0",
	"template": {
		"outputs": [{
			"carousel": {
				"type": "basicCard",
				"items": [{
						"title": "명함1",
						"description": "정보가 표시됩니다.",
						"thumbnail": {
							"imageUrl": "https://ifh.cc/g/hCphm.png"
						},
						"buttons": [{
								"action": "message",
								"label": namecard_db[0][0],
								#"messageText": "짜잔! 우리가 찾던 보물입니다"
							},
							{
								"action": "phone",
								"label": namecard_db[0][10],
								"phoneNumber": namecard_db[0][10]
							},
                            {
								"action": "share",
								"label": "공유하기"
							}
						]
					},
					{
						"title": "명함2",
						"description": "정보가 표시됩니다.",
						"thumbnail": {
							"imageUrl": "https://ifh.cc/g/d7Txi.png"
						},
						"buttons": [{
								"action": "phone",
								"label": namecard_db[1][0],
								#"messageText": "짜잔! 우리가 찾던 보물입니다"
							},
							{
								,
								"label": namecard_db[1][10],
								"phoneNumber": namecard_db[1][10]
							},
                            {
								"action": "share",
								"label": "공유하기"
							}
						]
					},
					{
						"title": "명함3",
						"description": "정보가 표시됩니다.",
						"thumbnail": {
							"imageUrl": "https://ifh.cc/g/slF0l.png"
						},
						"buttons": [{
								"action": "message",
								"label": namecard_db[2][0],
								#"messageText": "짜잔! 우리가 찾던 보물입니다"
							},
							{
								"action": "phone",
								"label": namecard_db[2][10],
								"phoneNumber": namecard_db[2][10]
							},
                            {
								"action": "share",
								"label": "공유하기"
							}
						]
					}
				]
			}
		}]
	}
    }

@app.route('/namecard', methods = ['POST'])
def namecard():
    body = request.json
    pprint.pprint(body)
    img_url = body['userRequest']['params']['media']['url']

    if img_url.startswith('http://dn-m.talk.kakao.com/talkm'):
        with urllib.request.urlopen(img_url) as input:
            with open('./img.jpg','wb') as output:
                output.write(input.read())

    text=ocr('img.jpg')           
    return {
        "version":"2.0",
        "template":{
            "outputs":[
                {
                    "simpleText":{
                        "text": text
                    }
                }
            ]
        }
    }

def ocr(file):    
    global namecard_db           
    #with open('namecard_db.pickle', 'rb') as f:
    #    namecard_db = pickle.load(f)

    img = cv2.imread('img.jpg')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_blur = cv2.GaussianBlur(gray, (3,3), 0)
    _, binary = cv2.threshold(img_blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    cnts, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in cnts:
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02*peri, True)
        height, width = img.shape[:2]
        area=cv2.contourArea(cnt)
  
        if len(approx) == 4 and area > 4:
            cv2.drawContours(img, [approx], -1, (0, 255, 0), 10)
            pts1 = np.float32([approx[0][0][:], approx[3][0][:], approx[1][0][:], approx[2][0][:]])
            width = (math.sqrt((approx[3][0][0]-approx[0][0][0])**2 + (approx[3][0][1]-approx[0][0][1])**2)
                    + math.sqrt((approx[2][0][0]-approx[1][0][0])**2 + (approx[2][0][1]-approx[1][0][1])**2))/2
            height = (math.sqrt((approx[1][0][0]-approx[0][0][0])**2 + (approx[1][0][1]-approx[0][0][1])**2)
                    + math.sqrt((approx[3][0][0]-approx[2][0][0])**2 + (approx[3][0][1]-approx[2][0][1])**2))/2
            pts2 = np.float32([[0,0], [width, 0], [0,height], [width, height]]) 
            M = cv2.getPerspectiveTransform(pts1, pts2)
  
    img_result = cv2.warpPerspective(img, M, (int(width), int(height)))
    cv2.imwrite("out.png", img_result)
    text = pytesseract.image_to_string("out.png", lang="eng+kor")
    print(text)

    #global id
    namecard_text = text
    print(namecard_db)
    namecard_text = namecard_text.split("\n")
    tel = namecard_text[10].split(':')
    namecard_text[10] = tel[1]
    namecard_db.append(namecard_text)
    print(namecard_text)
    #print("답 : ", namecard_db[0][1], namecard_db[0][10])
    #print("답 : ", namecard_db[1][1], namecard_db[1][10])
    #print("답 : ", namecard_db[2][1], namecard_db[2][10])
    #id += 1


    with open('namecard_db.pickle', 'wb') as f:
        pickle.dump(namecard_db, f, pickle.HIGHEST_PROTOCOL)

    return text  



