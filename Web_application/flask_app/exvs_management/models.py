from datetime import datetime
from pytz import timezone
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from exvs_management import db , login_manager

# ユーザー認証に関わる関数を指定する
# これにより、current_userで現在のログインユーザーの情報を引き出すとこが出来る
@login_manager.user_loader
def load_user(user_id):
    # user_idを元にデータベースを検索し、user_idに対応するユーザー情報を取得する
    return User.query.get(user_id)

# データベースdb上に定義されて浮いた状態のクラス
# UserMixinクラスに定義されている属性やメソッドを利用できるので、flask_loginで利用する属性やメソッドを定義する必要がない(ex. base.htmlで現在のユーザーを表す属性current_userを使える)
# ユーザー情報をまとめたテーブル
class User(db.Model, UserMixin):
    __tablename__ = "users"

    # 列の定義
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    # セキュリティー向上のため、パスワードはハッシュ化して保持する
    password_hash = db.Column(db.String(128))
    administrator = db.Column(db.String(1))
    
    # 初期化の処理
    def __init__(self, email, username, password, administrator):
        # インスタンスの属性はself.~で表す
        self.email = email
        self.username = username
        # プロパティpasswordに設定する
        # 変数password_hashではなく、プロパティpasswordに(セッターを用いて)値を設定することで、ハッシュ化前のパスワードにはアクセス出来ないようにする(プロパティpasswordにはゲッターを用いる必要があるが、ゲッターを用いるとAttributeErrorが起きるから)
        self.password = password
        self.administrator = administrator

    # print()などで画面出力する際にreturnで定義した内容を表示する    
    def __repr__(self):
        return f"UserName:{self.username}"
    
    def check_password(self, password):
        # ハッシュ化されたパスワードと入力されたパスワードを比較
        return check_password_hash(self.password_hash, password)
    
    # パスワードは簡単に変更されたり参照されては困る
    # propertyを用いて、ゲッターとセッターを設定する
    # propertyは、クラスのインスタンスに保持するデータで値の参照や変更方法を制限することが可能
    # プロパティでは、ゲッターを通じてのみ値を参照することができず、セッターを通じてしか値を変更出来ない(i.e. 思わぬところからの参照変更を防ぐ)
    # ゲッター
    # @property
    # def プロパティ名(self):
    #     return self.変数
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    # セッター
    # @プロパティ名.setter
    # def プロパティ名(self, 設定値):
    #     self.変数 = 設定値
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    # propertyの利用方法
    # 値の参照：インスタンス名.プロパティ名
    # 値の設定：インスタンス名.プロパティ名 = 設定値
    
    # 管理者か否かを判定する
    def is_administrator(self):
        if self.administrator == "1":
            return 1
        else:
            return 0
        
    # プレイ日数を数える
    #def play_count(self, user_id):
        #return BlogPost.query.filter_by(user_id=user_id).count()


# 戦績管理テーブル
class Record(db.Model):
    __tablename__ = "records"

    # 列の定義
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer)
    year = db.Column(db.Integer)
    month = db.Column(db.Integer)
    day = db.Column(db.Integer)
    matches = db.Column(db.Integer)
    wins = db.Column(db.Integer)
    ten_wins = db.Column(db.Integer)
    rate = db.Column(db.Integer)
    moneys = db.Column(db.Integer)
    
    # 初期化の処理
    def __init__(self, user_id, year, month, day, matches, wins, ten_wins, rate, moneys):
        self.user_id = user_id
        self.year = year
        self.month = month
        self.day = day
        self.matches = matches
        self.wins = wins
        self.ten_wins = ten_wins
        self.rate = rate
        self.moneys = moneys


#  お問い合わせ情報を管理するモデル
class Inquiry(db.Model):
    __tablename__ = "inquiry"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(64))
    title = db.Column(db.String(140))
    text = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.now(timezone("Asia/Tokyo")))
    
    def __init__(self, name, email, title, text):
        self.name = name
        self.email = email
        self.title = title
        self.text = text

    def __repr__(self):
        return f"InquiryID: {self.id}, Name: {self.name}, Text: {self.text} \n"