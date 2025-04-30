import os
import pandas as pd
from datetime import datetime, date, time, timedelta
import jpholiday
import collections
import json
import math

def is_valid_time(t):
    return t is not None and not (isinstance(t, float) and math.isnan(t))

def get_sunday(date_obj):
    return date_obj - timedelta(days=date_obj.weekday() + 1) if date_obj.weekday() != 6 else date_obj

def check_schedule(work_log_list, schedule_log_list):
    """
    勤務時間とスケジュールの重複をチェックする関数。

    Parameters:
        column_work_log (list): 勤務時間が記録された列。各要素は以下の形式の辞書：
            {
                'date': datetime.datetime,  # 日付（例: '2025-04-01'）
                'times': list of dict  # 各辞書に datetime.time型の'start', 'end' を含む
            }
        column_schedule_log (list): 各自のスケジュール（講義など）が記録された列。
            {
                'date': datetime.datetime,  # 日付（例: '2025-04-01'）
                'times': list of dict  # 各辞書に datetime.time型の'start', 'end' とstring型の'event'を含む
            }
    Returns:
        list: 重複があった場合の詳細な情報を含むリスト。
    """
    errors = []
    for work_log in work_log_list:
        for schedule_log in schedule_log_list:
            if work_log['date'] == schedule_log['date']:
                for work_time in work_log['times']:
                    if not is_valid_time(work_time['start']) or not is_valid_time(work_time['end']):
                        continue
                    for schedule_time in schedule_log['times']:
                        if work_time['start'] <= schedule_time['end'] and work_time['end'] >= schedule_time['start']:
                            errors.append(f"勤務時間とスケジュールが重複しています: {work_log['date'].date()}の{work_time['start']}-{work_time['end']}は{schedule_time['event']}{schedule_time['start']}-{schedule_time['end']}と重複しています。")
    return errors




def check_work_constraints_isct(work_log_list):
    """
    勤務時間が科学大の就業規則に従っているかをチェックする関数。
    就業規則の概要:
    ---- 1日ごとの勤務時間の制約 ----
    1日の上限は7時間45分
    6時間以上の連続勤務になる場合は、途中で45分以上の休憩を挟む
    ---- 週ごとの勤務時間の制約 ----
    週に20時間を超過する勤務は禁止
    ---- 勤務可能時間についての制約 ----
    勤務可能なのは8:00-20:00の範囲
    土日祝日の勤務は禁止
    講義の時間に被るのは禁止(別の関数でチェック)
    
    Parameters:
        work_log_list (list): 勤務時間が記録されたリスト。各要素は以下の形式の辞書：
            {
                'date': datetime.date,  # 日付（例: '2025-04-01'）
                'times': list of dict  # 各辞書に datetime.time型の'start', 'end' の時刻を含む（例: '09:00'）
            }
    Returns:
        bool: エラーがあった場合はTrue、なかった場合はFalse。
        list: エラーがあった場合の詳細な情報を含むリスト。
            リストの各要素はエラーメッセージの文字列。
            例: "2025-04-01 の勤務時間が上限の7時間45分（465分）を超えています。"
    """
    errors = []

    # 週単位の集計用
    weekly_minutes = collections.defaultdict(int)  # key: (year, week), value: minutes

    for entry in work_log_list:
        work_date = entry['date']
        times = entry['times']

        # --- 勤務可能時間帯 & 土日祝チェック ---
        for period in times:
            s, e = period['start'], period['end']
            if not is_valid_time(s) or not is_valid_time(e):
                        continue
            if work_date.weekday() >= 5 or jpholiday.is_holiday(work_date):
                errors.append(f"{work_date.date()} は土日または祝日です。勤務不可。")

        total_minutes = 0
        valid_times = [t for t in times if is_valid_time(t['start']) and is_valid_time(t['end'])]
        times_sorted = sorted(valid_times, key=lambda x: x['start'])

        # --- 勤務時間帯チェック & 総勤務時間計算 ---
        for period in times:
            s, e = period['start'], period['end']
            if not is_valid_time(s) or not is_valid_time(e):
                        continue
            if not (time(8, 0) <= s <= time(20, 0)) or not (time(8, 0) <= e <= time(20, 0)):
                errors.append(f"{work_date.date()} の勤務が勤務可能時間（8:00-20:00）外です。")
            minutes = (datetime.combine(date.min, e) - datetime.combine(date.min, s)).seconds // 60
            total_minutes += minutes

        # --- 休憩チェック ---
        for i in range(len(times_sorted) - 1):
            end_current = times_sorted[i]['end']
            start_next = times_sorted[i + 1]['start']
            if not is_valid_time(end_current) or not is_valid_time(start_next):
                continue
            rest_minutes = (datetime.combine(date.min, start_next) - datetime.combine(date.min, end_current)).seconds // 60
            if rest_minutes >= 45:
                break  # OK
            else:
                if total_minutes >= 360:  # 6時間以上働く場合
                    errors.append(f"{work_date.date()} の勤務が6時間以上連続ですが、45分以上の休憩がありません。")

        if total_minutes > 465:
            errors.append(f"{work_date.date()} の勤務時間が上限の7時間45分（465分）を超えています。")
        # --- 週単位の記録 ---
        # その週の日曜日を取得
        week_start_sunday = get_sunday(work_date)
        # 合計勤務時間加算
        weekly_minutes[week_start_sunday] += total_minutes

    # --- 週単位のチェック ---
    for week_start, total in weekly_minutes.items():
        if total > 1200:
            week_end = week_start + timedelta(days=6)
            errors.append(f"{week_start.date()}から{week_end.date()}の勤務時間が20時間（1200分）を超えています。合計: {total}分")
    return errors

def check_employee_information(personal_info_df, budget_info_df, work_info_df):
    """
    学生の個人情報、予算情報、勤務情報が employee_information.json と一致しているかをチェックする関数。
    Parameters:
        personal_info_df (pd.DataFrame): 個人情報のDataFrame
        budget_info_df (pd.DataFrame): 予算情報のDataFrame
        work_info_df (pd.DataFrame): 勤務情報のDataFrame
    Returns:
        bool: 一致していない場合はTrue、すべて一致している場合はFalse
        list: エラーがあった場合の詳細な情報を含むリスト
    """
    # JSONファイルを読み込む
    base_dir = os.path.dirname(os.path.dirname(__file__))
    EMPLOYEE_INFO_PATH = os.path.join(base_dir, "data", "employee_information.json")
    with open(EMPLOYEE_INFO_PATH, "r", encoding="utf-8") as f:
        employee_information = json.load(f)
    
    errors = []
    
    student_id = str(personal_info_df["STUDENT_ID"].values[0])
    # 学生IDに対応する情報をemployee_information.jsonから取得
    employee_info = next((entry for entry in employee_information if entry["personal_info"]["STUDENT_ID"] == student_id), None)
    if employee_info is None:
        errors.append(f"STUDENT_ID {student_id} が employee_information.json に見つかりません。")
        return errors
    
    # 比較対象の辞書データ
    fields_to_check = [
        # personal_info
        ("personal_info", "NAME", personal_info_df["NAME"].values[0]),
        ("personal_info", "AFFILIATION", personal_info_df["AFFILIATION"].values[0]),
        #("personal_info", "CONTACT", personal_info_df["CONTACT"].values[0]), #連絡先はなくてもいい
        # budget_info
        ("budget_info_1", "BUDGET_CODE_1", budget_info_df["BUDGET_CODE_1"].values[0]),
        ("budget_info_1", "AFFILIATION_CONFIRM_1", budget_info_df["AFFILIATION_CONFIRM_1"].values[0]),
        ("budget_info_1", "NAME_CONFIRM_1", budget_info_df["NAME_CONFIRM_1"].values[0]),
        # work_info
        ("work_info_1", "WORK_TYPE_1", work_info_df["WORK_TYPE_1"].values[0]),
        ("work_info_1", "HOURLY_WAGE_1", work_info_df["HOURLY_WAGE_1"].values[0]),
        ("work_info_1", "EMPLOYEE_ID_1", work_info_df["EMPLOYEE_ID_1"].values[0]),
    ]
    
    for section, key, value in fields_to_check:
        expected_value = str(employee_info[section].get(key, "")).replace(" ", "")
        df_value = str(value).replace(" ", "")
        if expected_value != df_value:
            errors.append(f"{section} の {key} が一致しません。期待値: {expected_value}, 入力されている値: {df_value}")
    
    return errors