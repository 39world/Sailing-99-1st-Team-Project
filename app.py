from pymongo import MongoClient
import jwt
import datetime
import hashlib
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

client = MongoClient('localhost', 27017)
db = client.dbsparta_plus_week4

#------------------------------------------------------랜딩페이지 index.html------------------------------------------------------
@app.route('/')
def getMain():
    return render_template('/index.html')

# ------------------------------------------------------로그인/회원가입------------------------------------------------------
@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)
    
@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
         'id': username_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    # 회원가입
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    # PW해시(암호화)
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,                               # 아이디
        "password": password_hash,                                  # 비밀번호
        "profile_name": username_receive,                           # 프로필 이름 기본값은 아이디
        "profile_pic": "",                                          # 프로필 사진 파일 이름
        "profile_pic_real": "profile_pics/profile_placeholder.png", # 프로필 사진 기본 이미지
        "profile_info": ""                                          # 프로필 한 마디
    }
    # DB 저장
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})

#  ID중복확인
@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})

# ------------------------------------------------------메인 페이지 상위 15개 전시------------------------------------------------------
@app.route('/info', methods=['GET'])
def read_info():
    all_info = list(db.exhibition.find({}, {'_id': False}))
    return jsonify({'all_info': all_info})

# ------------------------------------------------------인기 전시------------------------------------------------------
@app.route('/show', methods=['GET'])
def show():
    shows = list(db.exhibition.find({}, {'_id': False}))
    return render_template("show.html", shows=shows)


# ------------------------------------------------------마이페이지------------------------------------------------------
@app.route('/mypage')  # 마이페이지 연결
def mypage_diary():
    return render_template('mypage.html')


@app.route('/mypage/diary', methods=['GET'])  # 마이페이지 리뷰 보여주기 API
def show_diary():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    user_info = db.users.find_one({"username": payload["id"]})["username"]
    print(payload['id']);
    diaries = list(db.diary.find({'username': user_info}, {'_id': False}))

    return jsonify({'all_diary': diaries})


@app.route('/mypage/diary', methods=['POST'])  # 마이페이지 리뷰 작성하기 API
def save_diary():
    title_receive = request.form['title_give']
    content_receive = request.form['content_give']

    file = request.files["file_give"]  # 파일저장
    extension = file.filename.split('.')[-1]

    today = datetime.now()
    mytime = today.strftime('%y-%m-%d-%H-%M-%S')

    filename = f'file-{mytime}'

    save_to = f'static/{filename}.{extension}'

    file.save(save_to)

    # id와 같이 저장
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    user_info = db.users.find_one({"username": payload["id"]})["username"]

    doc = {
        'username': user_info,
        'title': title_receive,
        'content': content_receive,
        'file': f'{filename}.{extension}'
    }

    db.diary.insert_one(doc)
    return jsonify({'msg': '저장 완료!'})


@app.route('/show/wannadiary', methods=['POST'])  # 찜한 전시회 보여주기 API
def find_wannadiary():         
     title_receive = request.form['title_give'].text();
     print(title_receive);
     wannadiaries = list(db.exhibition.find({'title': title_receive}, {'_id': False}))     
     return jsonify({'all_wannadiary': wannadiaries})



@app.route('/mypage/wannadiary', methods=['GET'])  # 찜한 전시회 보여주기 API
def show_wannadiary():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    user_info = db.users.find_one({"username": payload["id"]})["username"]
    wannadiaries = list(db.wannadiary.find(
        {'username': user_info}, {'_id': False}))

    return jsonify({'all_wannadiary': wannadiaries})


# @app.route('/show/wannadiary', methods=['POST'])  # 찜하기 저장
# def save_wannadiary():
#     title_receive = request.form['title_give']
#     location_receive = request.form['location_give']
#     date_receive = request.form['date_give']
#     img = request.form['img_give']
#     title_url = request.form['title_url_give']

#     # id와 같이 저장
#     token_receive = request.cookies.get('mytoken')
#     payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
#     user_info = db.users.find_one({"username": payload["id"]})["username"]

#     doc = {
#         'username': user_info,
#         'title': title_receive,
#         'location': location_receive,
#         'date' : date_receive,
#         'img': img,
#         'title_url': title_url
#     }

#     db.wannadiary.insert_one(doc)

#     return jsonify({'msg': '저장 완료!'})


@app.route('/mypage/wannadelete', methods=['POST'])  # 찜리스트 삭제 API
def delete_wannadiary():
    title_receive = request.form['title_give']
    db.wannadiary.delete_one({'title': title_receive})
    return jsonify({'msg': '삭제 완료!'})


@app.route('/mypage/delete', methods=['POST'])  # 리뷰리스트 삭제 API
def delete_diary():
    file_receive = request.form['file_give']
    db.diary.delete_one({'file': file_receive})
    return jsonify({'msg': '삭제 완료!'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)