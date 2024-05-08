from exvs_management import db
from exvs_management.models import User

# (全消去による)初期化
db.drop_all()

# データベースの作成(sqliteから変更したので、data.sqliteとは別物に記録していくことに注意)
db.create_all()

# 管理者ユーザーの作成
user1 = User(email="takenarikanawa32@gmail.com", username="Admin User", password="moneyring1368", administrator="1")
db.session.add(user1)
db.session.commit()