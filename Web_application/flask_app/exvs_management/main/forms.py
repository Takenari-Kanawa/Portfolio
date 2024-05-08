from datetime import datetime
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import SelectField, SubmitField, IntegerField, IntegerField, StringField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email
from datetime import datetime

class NonZeroInteger(object):
    def __init__(self, message=None):
        if not message:
            message = '0以上の整数を入力してください。'
        self.message = message

    def __call__(self, form, field):
        if field.data is not None and (field.data < 0 or not isinstance(field.data, int)):
            raise ValidationError(self.message)
        
# FlaskFormの機能を継承
class RecordForm(FlaskForm):
    # validatorsで入力チェック(DataRequired:必須入力, Email:メール形式, EqualTo:入力値が同じか)
    year = SelectField('年', coerce=int, validators=[DataRequired()])
    month = SelectField('月', coerce=int, validators=[DataRequired()])
    day = SelectField('日', coerce=int, validators=[DataRequired()])
    matches = IntegerField('対戦数', validators=[DataRequired()])
    wins = IntegerField('勝利数', validators=[DataRequired()])
    ten_wins = IntegerField('10連勝数', validators=[NonZeroInteger()])
    submits = SubmitField('登録')   

    def __init__(self, *args, **kwargs):
        super(RecordForm, self).__init__(*args, **kwargs)
        now = datetime.now()
        jyear = now.year
        self.year.choices = [(i, str(i)+"年") for i in range(jyear-5, jyear+5)]  # 適切な範囲に変更
        self.month.choices = [(i, str(i)+"月") for i in range(1, 13)]
        self.day.choices = [(i, str(i)+"日") for i in range(1, 32)]
        
    def validate(self):
        if not super().validate():
            return False
        try:
            year = int(self.year.data)
            month = int(self.month.data)
            day = int(self.day.data)
            _ = datetime(year, month, day)
        except ValueError:
            self.year.errors.append('日付が無効です。')
            return False
        return True
    
class UpdateRecordForm(FlaskForm):
    year = SelectField('年', coerce=int, validators=[DataRequired()])
    month = SelectField('月', coerce=int, validators=[DataRequired()])
    day = SelectField('日', coerce=int, validators=[DataRequired()])
    matches = IntegerField('対戦数', validators=[DataRequired()])
    wins = IntegerField('勝利数', validators=[DataRequired()])
    ten_wins = IntegerField('10連勝数', validators=[NonZeroInteger()])
    submit = SubmitField("更新")

    def __init__(self, record_id, *args, **kwargs):
        # superで継承元のクラス(FlaskForm)の処理は残しつつ、新たな初期処理を追記する
        super(UpdateRecordForm, self).__init__(*args, **kwargs)
        self.id = record_id
        self.user_id = current_user.id
        now = datetime.now()
        jyear = now.year
        self.year.choices = [(i, str(i)+"年") for i in range(jyear-5, jyear+5)]  # 適切な範囲に変更
        self.month.choices = [(i, str(i)+"月") for i in range(1, 13)]
        self.day.choices = [(i, str(i)+"日") for i in range(1, 32)]

# 問い合わせフォーム
class InquiryForm(FlaskForm):
    name = StringField('お名前（必須）', validators=[DataRequired()])
    email = StringField('メールアドレス（必須）', validators=[DataRequired(), Email(message='正しいメールアドレスを入力して下さい')])
    title = StringField('題名')
    text = TextAreaField('メッセージ本文（必須）', validators=[DataRequired()])
    submit = SubmitField('送信')