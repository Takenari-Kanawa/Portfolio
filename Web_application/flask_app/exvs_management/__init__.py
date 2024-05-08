import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# インスタンスの作成
app = Flask(__name__)

# アプリの環境変数SECRET_KEYに対して秘密鍵を作成する(Formを利用する際に必要, セキュリティ, 値は何でもOK)
app.config["SECRET_KEY"] = "mysecretkey"

# データベース周りの環境設定
basedir = os.path.abspath(os.path.dirname(__file__))
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')

# herokuは(今まで使っていた)sqliteではなくpostgreSQLをサポートしている
# 設定を変更する

# heroku上ではPostgreSQLへの接続用の環境変数はDATABASE_URLに格納される
uri = os.environ.get('DATABASE_URL')

# heroku上でアプリを実行するとURLに値が設定される
if uri:
    # uriがpostgres://で始まっているかを確認
    # heroku上では、環境変数データベースURLの値はpostgres://で始まる
    if uri.startswith('postgres://'):
        # postgres://をpostgresql://へ変更する
        # 1は先頭から最初の一つ目を置き換えるという意味
        uri = uri.replace('postgres://', 'postgresql://', 1)
        # このアプリではsqlalchemyを用いてデータベースにアクセスするので、環境変数はSQLALCHEMY_DATABASE_URIを使用する
        # しかし、heroku上で設定される環境変数は、変数名がDATABASE_URLになっているので、これを環境変数SQLALCHEMY_DATABASE_URIに設定する
        app.config['SQLALCHEMY_DATABASE_URI'] = uri

# ローカルでアプリを実行するとURIには値が設定されない
else:
    # ifで行った設定を直接行う
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# データベースの作成と、flask_migrateの設定
db = SQLAlchemy(app)
Migrate(app, db)

# ログインマネジャーの設定
# インスタンス化
login_manager = LoginManager()
# アプリとログインの機能を紐づける
login_manager.init_app(app)
# ログインをしていないユーザーがログインが必要なページにアクセスしようとすると転送されるURLを指定する
# usersはBlueprint(インスタンス)
login_manager.login_view = "users.login"

# ログインしていないユーザーがログインが必要なページに移動しようとして、ログインページへ飛ばされた際のアナウンスをカスタマイズ
# *args:複数の引数をタプルとして受け取る
# *kwargs:複数のキーワード引数を辞書として受け取る
def localize_callback(*args, **kwargs):
    return "このページにアクセスするには、ログインが必要です。"
login_manager.localize_callback = localize_callback


# 実装したBlueprintをFlaskのアプリケーションへ登録する(これにより、Blueprintは有効になる)
# 各ファイルで定義したBlueprint(インスタンス)
from exvs_management.main.views import main
from exvs_management.users.views import users
from exvs_management.error_pages.handlers import error_pages


# Blueprintの登録
app.register_blueprint(main)
app.register_blueprint(users)
app.register_blueprint(error_pages)
