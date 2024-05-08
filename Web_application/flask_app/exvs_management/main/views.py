from datetime import datetime
from flask import Blueprint, render_template, request, url_for, redirect, flash, abort
from flask_login import login_user, logout_user, login_required, current_user
from exvs_management import db
from exvs_management.models import Record, Inquiry
from exvs_management.main.forms import RecordForm, UpdateRecordForm, InquiryForm
from exvs_management.main.problem import win_rate, calculation, calculation_support, money_calculation


# Blueprintの実装
# __name__にはこのファイルのディレクトリが格納されている
main = Blueprint('main', __name__)

# ホーム用view関数
@main.route('/')
def index():
    return render_template('index.html')

# 戦績登録用view関数
@main.route('/<int:user_id>/record_register', methods=["GET", "POST"])
@login_required
def record_register(user_id):
    form = RecordForm()
    # 入力データに誤りがないとき
    if form.validate_on_submit():
        record = Record(user_id=user_id, year=form.year.data, month=form.month.data, day=form.day.data, matches=form.matches.data, wins=form.wins.data, ten_wins=form.ten_wins.data, rate = win_rate(matches=form.matches.data, wins=form.wins.data), moneys = calculation(matches=form.matches.data, wins=form.wins.data, ten_wins=form.ten_wins.data))
        db.session.add(record)
        db.session.commit()

        flash("戦績と推定金額が登録されました")
        return redirect(url_for('main.record_maintenance',user_id=user_id, alert=0))
    
    # 未記入か、入力内容に問題がある場合
    return render_template("record_register.html", form=form)

# 戦績管理ページ
@main.route('/<int:user_id>/<int:alert>/record_maintenance')
@login_required
def record_maintenance(user_id, alert=0):
    # ページの取得
    page = request.args.get("page", 1, type=int)
    records = Record.query.filter_by(user_id=user_id).order_by(Record.year.desc(), Record.month.desc(), Record.day.desc()).paginate(page=page, per_page=10)

    # 今月の情報を取得
    month_matches, month_wins, month_ten_wins = calculation_support(user_id)
    month_money = money_calculation(user_id)

    if alert:
        flash(f"今月の累計使用金額: {month_money}円", "success")


    return render_template("record_maintenance.html", records=records, month_matches=month_matches, month_wins=month_wins, month_ten_wins = month_ten_wins,  month_money=month_money)


@main.route("/<int:record_id>/record", methods=["GET", "POST"])
@login_required
def record(record_id):
    # user_id(主キー)を元にデータベースを検索(見つからなかったら404エラーを出力)
    record = Record.query.get_or_404(record_id)

    # 現在ログインしているユーザーが更新対象のユーザーでも管理者ユーザーでもない時、処理を中止して403エラーを発生させる
    if record.user_id != current_user.id and not current_user.is_administrator():
        abort(403)

    form = UpdateRecordForm(record_id)

    # formにデータが入力された場合(i.e. account.htmlで更新があったとき)にチェックを行う
    if form.validate_on_submit():
        record.year = form.year.data
        record.month = form.month.data
        record.day = form.day.data
        record.matches = form.matches.data
        record.wins = form.wins.data
        record.ten_wins = form.ten_wins.data
        record.rate = round(win_rate(matches=form.matches.data, wins=form.wins.data), 4)
        record.moneys = calculation(matches=form.matches.data, wins=form.wins.data, ten_wins=form.ten_wins.data)

        # 変更を実施
        db.session.commit()
        
        # 変更が行われた事をアナウンス
        flash("戦績が更新されました")
        return redirect(url_for("main.record_maintenance", user_id=current_user.id, alert=0))
    
    # 特に最初にURLが呼び出された時はGETメソッドが呼び出される
    # account.htmlで更新があったときは再度このview関数が呼ばれ、その時はpostメソッドが呼び出される
    elif request.method == "GET":
        form.year.data = record.year
        form.month.data = record.month
        form.day.data = record.day
        form.matches.data = record.matches
        form.wins.data = record.wins
        form.ten_wins.data = record.ten_wins
    return render_template("record.html", form=form)


@main.route("/<int:record_id>/delete", methods=["GET", "POST"])
@login_required
def delete_record(record_id):

    record = Record.query.get_or_404(record_id)
    # 現在ログインしているユーザーが更新対象のユーザーでも管理者ユーザーでもない時、処理を中止して403エラーを発生させる
    if record.user_id != current_user.id and not current_user.is_administrator():
        abort(403)

    # 戦績の削除
    db.session.delete(record)
    # 変更の実行
    db.session.commit()
    # 削除が行われた事をアナウンス
    flash("戦績が削除されました")
    return redirect(url_for('main.record_maintenance', user_id=current_user.id, alert=0))


# お問合せ用view関数
@main.route('/inquiry', methods=['GET', 'POST'])
def inquiry():
    form = InquiryForm()

    # 正しい入力がなされた場合
    if form.validate_on_submit():
        # 入力内容をデータベースに保存
        inquiry = Inquiry(name=form.name.data, email=form.email.data, title=form.title.data, text=form.text.data)
        db.session.add(inquiry)
        db.session.commit()
        flash('お問い合せが送信されました')
        return redirect(url_for('main.inquiry'))

    # 未入力か誤入力がある時(特に最初の呼び出し)
    return render_template('inquiry.html', form=form)


# お問合せ一覧用view関数
@main.route('/inquiry_maintenance')
@login_required
def inquiry_maintenance():
    # 現在のページ数を取得
    page = request.args.get('page', 1, type=int)

    # ページネーションをしたデータを取得
    inquiries = Inquiry.query.order_by(Inquiry.id.desc()).paginate(page=page, per_page=10)

    return render_template('inquiry_maintenance.html', inquiries=inquiries)


# お問合せ詳細ページ用view関数
@main.route('/<int:inquiry_id>/display_inquiry')
@login_required
def display_inquiry(inquiry_id):
    # inquiry_idを元にデータを抽出
    inquiry = Inquiry.query.get_or_404(inquiry_id)

    # インスタンス化して利用可能状態にする
    form = InquiryForm()

    # お問合せ内容を記入する
    form.name.data = inquiry.name
    form.email.data = inquiry.email
    form.title.data = inquiry.title
    form.text.data = inquiry.text

    return render_template('inquiry.html', form=form, inquiry_id=inquiry_id)


# お問い合わせ削除用view関数
@main.route('/<int:inquiry_id>/delete_inquiry', methods=['GET', 'POST'])
@login_required
def delete_inquiry(inquiry_id):
    # inquiry_idを元に問い合わせを取得
    inquiries = Inquiry.query.get_or_404(inquiry_id)
    
    # 現在のユーザーが管理者ではない時403エラー
    if not current_user.is_administrator():
        abort(403)
    
    # 問い合わせinquiriesをデータベースから削除
    db.session.delete(inquiries)
    db.session.commit()
    flash('お問い合わせが削除されました')

    return redirect(url_for('main.inquiry_maintenance'))