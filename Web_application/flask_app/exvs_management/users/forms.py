from flask_wtf import FlaskForm
from wtforms import ValidationError, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from exvs_management.models import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(message="正しいメールアドレスを入力して下さい")])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("ログイン")


# FlaskFormの機能を継承
class RegistrationForm(FlaskForm):
    # フィールドの定義と名前
    # validatorsで入力チェック(DataRequired:必須入力, Email:メール形式, EqualTo:入力値が同じか)
    # validatorsの各要素のmessageはエラーメッセージ
    email = StringField('メールアドレス', validators=[DataRequired(), Email(message="正しいメールアドレスを入力して下さい")])
    username = StringField('ユーザー名', validators=[DataRequired()])
    password = PasswordField('パスワード', validators=[DataRequired(), EqualTo("pass_confirm", message="パスワードが一致していません")])
    pass_confirm = PasswordField('パスワード(確認)', validators=[DataRequired()])
    submit = SubmitField('登録')

    # validate_(フィルド名)で定義される関数は、form.validate_on_submit()が実行されるときに同時に実行される
    def validate_username(self, field):
        # filter_byで検索をかける
        if User.query.filter_by(username=field.data).first():
            # 条件に一致する最初の一件が存在する時、次を実行
            raise ValidationError("入力されたユーザー名は既に使われています。")
    
    def validate_email(self, field):
        # filter_byで検索をかける
        if User.query.filter_by(email=field.data).first():
            # 条件に一致するデータが1組でもあれば、次を実行
            raise ValidationError("入力されたメールアドレスは既に登録されています。")


# GETメソッドは、ブラウザーがウェブサーバーから情報の転送を依頼する際に使用
# POSTメソッドは、ブラウザーがウェブサーバーへ情報を送信する際に使用
# デフォルトではGETメソッドだけ受信可能になる
class UpdateUserForm(FlaskForm):
    email = StringField("メールアドレス", validators=[DataRequired(), Email(message="正しいメールアドレスを入力して下さい")])
    username = StringField("ユーザー名", validators=[DataRequired()])
    password = PasswordField("パスワード", validators=[EqualTo("pass_confirm", message="パスワードが一致していません。")])
    pass_confirm = PasswordField("パスワード(確認)")
    submit = SubmitField("更新")

    def __init__(self, user_id, *args, **kwargs):
        # superで継承元のクラス(FlaskForm)の処理は残しつつ、新たな初期処理を追記する
        super(UpdateUserForm, self).__init__(*args, **kwargs)
        self.id = user_id
    
    # validate_(フィールド名)で定義される関数は、form.validate_on_submit()が実行されるときに同時に実行される
    def validate_email(self, field):
        # 更新対象のユーザー以外で、同じemailを持つデータがないか？
        if User.query.filter(User.id != self.id).filter_by(email=field.data).first():
            raise ValidationError("入力されたメールアドレスは既に登録されています。")
        
    def validate_username(self, field):
        if User.query.filter(User.id != self.id).filter_by(username=field.data).first():
            raise ValidationError("入力されたユーザー名は既に使われています。")