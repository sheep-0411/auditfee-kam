from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import render_template , request
from flask_bootstrap import Bootstrap

from dotenv import find_dotenv, load_dotenv
import os
import datetime as dt
import pandas as pd

# Googleスプレッドシートとの連携に必要なライブラリ
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 設定
file_name = 'audit-fee-bot'

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

# .envファイルを探して読み込む
load_dotenv(find_dotenv())

# 辞書オブジェクト。認証に必要な情報をHerokuの環境変数から呼び出している
credential = {
"type": "service_account",
"project_id": os.environ['SHEET_PROJECT_ID'],
"private_key_id": os.environ['SHEET_PRIVATE_KEY_ID'],
"private_key": os.environ['SHEET_PRIVATE_KEY'],
"client_email": os.environ['SHEET_CLIENT_EMAIL'],
"client_id": os.environ['SHEET_CLIENT_ID'],
"auth_uri": "https://accounts.google.com/o/oauth2/auth",
"token_uri": "https://oauth2.googleapis.com/token",
"auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
"client_x509_cert_url":  os.environ['SHEET_CLIENT_X509_CERT_URL']
}
# スプレッドシートにアクセス
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credential, scope)
gc = gspread.authorize(credentials)
sh = gc.open(file_name)


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:19387887ab@127.0.0.1:5432/main'
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)

wks5 = sh.worksheet('save_data')

# シートから全部から読み込み
def get_records(wks):
    record = pd.DataFrame(wks.get_all_records())
    return record

# df1 = get_records(wks1)
# df2 = get_records(wks2)
# df3 = get_records(wks3)
# df4 = get_records(wks4)
df5 = get_records(wks5)
df5['監査報酬'] = df5['当年度監査報酬'] + df5['当年度監査報酬（ネットワークファーム）']
df5 = df5[pd.to_datetime(df5['期末日'])  > dt.datetime(2021,4,1)]
df5 = df5[['会社名','期末日','監査報酬','当年度監査報酬（ネットワークファーム）','監査法人','KAM1','KAM2','KAM3','KAM4','KAM5']].sort_values('監査報酬',ascending=False)
# df6 = get_records(wks6)
# df7 = get_records(wks7)
auditor = df5['監査法人'].drop_duplicates().tolist()

print(auditor)

header = df5.columns # DataFrameのカラム名の1次元配列のリスト
record = df5.values.tolist() # DataFrameのインデックスを含まない全レコードの2次元配列のリスト

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

@app.route("/", methods=['GET'])
def hello_world():
    return render_template('hello.html',header=header, record=record, auditor=auditor)

@app.route("/", methods=['POST'])
def post_world():
    name = request.form.get('flexRadioDefault')
    df5 = get_records(wks5)
    df5['監査報酬'] = df5['当年度監査報酬'] + df5['当年度監査報酬（ネットワークファーム）']
    df5 = df5[pd.to_datetime(df5['期末日'])  > dt.datetime(2021,4,1)]
    df5 = df5[['会社名','期末日','監査報酬','当年度監査報酬（ネットワークファーム）','監査法人','KAM1','KAM2','KAM3','KAM4','KAM5']].sort_values('監査報酬',ascending=bool(int(name) == 1))
    header = df5.columns # DataFrameのカラム名の1次元配列のリスト
    record = df5.values.tolist() # DataFrameのインデックスを含まない全レコードの2次元配列のリスト
    return render_template('hello.html',header=header, record=record, auditor=auditor)

# @app.route("/detail/<name>", methods=['GET'])
# def detail(name):
#     return render_template('detail.html',name=name)