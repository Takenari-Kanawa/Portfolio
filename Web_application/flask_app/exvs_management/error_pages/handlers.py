from flask import render_template, Blueprint



error_pages = Blueprint("error_pages", __name__)

# 権限がないページにアクセスした時(403エラー)に実行
# errorhandlerは(このままだと)一つのブループリントの範囲内だけで有効な関数
# これをアプリケーション全体で有効な関数にするには、app_errorhandlerとする必要がある
@error_pages.app_errorhandler(403)
def error_403(error):
    return render_template('error_pages/403.html'), 403

# 存在しないページにアクセスした時(404エラー)に実行
@error_pages.app_errorhandler(404)
def error_404(error):
    return render_template('error_pages/404.html'), 404