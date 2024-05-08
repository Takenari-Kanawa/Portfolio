from datetime import datetime
from sqlalchemy import func
from exvs_management.models import Record


def win_rate(matches, wins):
    rate = (round(wins/matches, 4))*100

    return rate


def calculation(matches, wins, ten_wins):
    # 負けるか10連勝する度に100円がかかる
    moneys = (matches - wins + ten_wins) * 100

    return moneys


def calculation_support(user_id):
    # 現在の年と月を取得
    now = datetime.now()
    jyear = now.year
    jmonth = now.month

    # データベースから、user_id=current_user.idかつyear=jyearかつmonth=jmonthに対応するすべてのデータを抽出
    records_query = Record.query.filter_by(user_id=user_id, year=jyear, month=jmonth)

    # 抽出したデータ内で、matchesとwinsの合計をmonth_matchesとmonth_winsに格納
    result = records_query.with_entities(func.sum(Record.matches), func.sum(Record.wins), func.sum(Record.ten_wins)).first()
    month_matches = result[0] if result[0] is not None else 0
    month_wins = result[1] if result[1] is not None else 0
    month_ten_wins = result[2] if result[2] is not None else 0
    
    return month_matches, month_wins, month_ten_wins

def money_calculation(user_id):
    # 現在の年と月を取得
    now = datetime.now()
    jyear = now.year
    jmonth = now.month

    # データベースから、user_id=current_user.idかつyear=jyearかつmonth=jmonthに対応するすべてのデータを抽出
    records_query = Record.query.filter_by(user_id=user_id, year=jyear, month=jmonth)

    # 抽出したデータ内で、matchesとwinsの合計をmonth_matchesとmonth_winsに格納
    result = records_query.with_entities(func.sum(Record.moneys)).first()
    month_money = result[0] if result[0] is not None else 0
    month_money = int(month_money)
    
    return month_money