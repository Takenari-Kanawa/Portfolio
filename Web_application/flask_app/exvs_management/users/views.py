from flask import render_template, url_for, redirect, session, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from exvs_management import db
from flask import Blueprint
from exvs_management.users.forms import RegistrationForm, LoginForm, UpdateUserForm
from exvs_management.models import User


# ブループリント
users = Blueprint('users', __name__)

@users.route("/login", methods=["GET", "POST"])
def login():
    # インスタンス化
    form = LoginForm()
    # 入力値に問題がない場合
    if form.validate_on_submit():
        # Userモデルのemail列でformに入力された値と等しいデータを取得
        user = User.query.filter_by(email=form.email.data).first()

        # 該当するユーザーが存在する場合
        if user is not None:
            # Userモデルのインスタンスuserのメソッドcheck_passwordでパスワードが正しいかを確認する
            if user.check_password(form.password.data):
                # ログイン
                login_user(user)
                # クエリー文字列(URLの末尾)nextの値を取得して変数nextに格納
                # ログインせずにログインが必要なページを訪れた場合は、クエリー文字列nextにログイン後に遷移するページそして、そのページのURLが設定される
                next = request.args.get("next")

                if next == None or not next[0] == '/':
                    # (最初に)ログインしたらブログ管理ページへ移動
                    # (ログインが必要なページにアクセスしようとしていないケース)
                    next = url_for("main.index")

                return redirect(next)
            
            else:
                flash("パスワードが一致しません")

        # 該当するユーザが存在しない場合
        else:
            flash("入力されたユーザーは存在しません")

    # 最初は何も入力されてないのでloginページ(login.html)へ移動する(入力ミスの場合も同様)
    return render_template("users/login.html", form=form)

@users.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))

@users.route('/register', methods=["GET", "POST"])
def register():
    # Formをインスタンス化(新規Formの作成)
    form = RegistrationForm()

    # Formが送信されて、内容が問題ないかを確認
    if form.validate_on_submit():
        # 管理者は最初にinit_user.pyで追加する
        user = User(email=form.email.data, username=form.username.data, password=form.password.data, administrator="0")
        db.session.add(user)
        db.session.commit()
        flash("ユーザーが登録されました")
        return redirect(url_for("users.login"))
    # 記入済みのFormに問題があるか、未記入の場合、ユーザー登録ページを表示する
    return render_template('users/register.html', form=form)

# ユーザー管理ページ
@users.route('/user_maintenance')
@login_required
def user_maintenance():
    # 現在ログインしているユーザーが管理者ユーザーでない場合は処理を注視して403エラーを出力
    if not current_user.is_administrator():
        abort(403)
    
    # ページの取得
    page = request.args.get("page", 1, type=int)
    users = User.query.order_by(User.id).paginate(page=page, per_page=10)
    return render_template("users/user_maintenance.html", users=users)


@users.route("/<int:user_id>/account", methods=["GET", "POST"])
# ログイン状態でないとview関数が実行出来ないようにする
# ログイン状態でないユーザーがURL"/user_maintenance"にアクセスすると、login_managerに設定されたURLに遷移する
@login_required
def account(user_id):
    # user_id(主キー)を元にデータベースを検索(見つからなかったら404エラーを出力)
    user = User.query.get_or_404(user_id)

    # 現在ログインしているユーザーが更新対象のユーザーでも管理者ユーザーでもない時、処理を中止して403エラーを発生させる
    if user.id != current_user.id and not current_user.is_administrator():
        abort(403)

    form = UpdateUserForm(user_id)

    # formにデータが入力された場合(i.e. account.htmlで更新があったとき)にチェックを行う
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data

        # パスワードは変更された時のみ更新
        if form.password.data:
            # Userクラスのインスタンス上のセッターを通じて、プロパティpasswordに値を設定
            user.password = form.password.data
        
        # 変更を実施
        db.session.commit()
        
        # 変更が行われた事をアナウンス
        flash("ユーザーアカウントが更新されました")
        return redirect(url_for("main.index"))
    
    # 特に最初にURLが呼び出された時はGETメソッドが呼び出される
    # account.htmlで更新があったときは再度このview関数が呼ばれ、その時はpostメソッドが呼び出される
    elif request.method == "GET":
        form.username.data = user.username
        form.email.data = user.email
    return render_template("users/account.html", form=form)


@users.route("/<int:user_id>/delete", methods=["GET", "POST"])
# ログイン状態でないとview関数が実行出来ないようにする
# ログイン状態でないユーザーがURL"/user_maintenance"にアクセスすると、login_managerに設定されたURLに遷移する
@login_required
def delete_user(user_id):

    user = User.query.get_or_404(user_id)
    # 更新(削除)対象のユーザーが管理者ユーザーの場合は、削除できないようにする
    if user.is_administrator():
        flash("管理者は削除できません")
        return redirect(url_for("users.account", user_id=user_id))
    # userの削除
    db.session.delete(user)
    # 変更の実行
    db.session.commit()
    # 削除が行われた事をアナウンス
    flash("ユーザーアカウントが削除されました")
    return redirect(url_for('main.index'))