import pandas as pd
import streamlit as st
from standardizer_isct import standardize_schedule, standardize_work

from datetime import datetime, date, time, timedelta
import jpholiday
import collections
import json

# def check_time(work_file,schedule_file):
#     has_error = False
#     work_standardized_df = standardize_work(work_file)
#     schedule_standardized_df = standardize_schedule(schedule_file)
#     for i in range(len(work_standardized_df)):
#         if work_standardized_df["is_holiday"][i] == True:
#                 st.warning(f'{work_standardized_df["Name"][i]}さん、{work_standardized_df["Date"][i]}は祝日のため勤務できません')
#                 has_error = True
#                 continue       
#         for j in range(len(schedule_standardized_df)):
#             if work_standardized_df['Name'][i] == schedule_standardized_df['Name'][j]:
#                 if work_standardized_df['Date'][i] == schedule_standardized_df['Date'][j]:
#                     if work_standardized_df['Start_Time'][i] <= schedule_standardized_df['End_Time'][j] and work_standardized_df['End_Time'][i] >= schedule_standardized_df['Start_Time'][j]:
#                         has_error = True
#                         manth_day = pd.to_datetime(work_standardized_df["Date"][i]).strftime("%m-%d")
#                         st.warning(f'{manth_day}({work_standardized_df["Name"][i]})の{schedule_standardized_df["Start_Time"][j]}から{schedule_standardized_df["End_Time"][j]}は{schedule_standardized_df["Name"][j]}さんが{schedule_standardized_df["Description"][j]}に参加中であるため勤務できません。')
                        
#     if has_error == False:
#         st.write("報告された勤務時間は問題ありません")


def check_schedule(work_log_list, schedule_log_list):
    """
    勤務時間とスケジュールの重複をチェックする関数。

    Parameters:
        column_work_log (list): 勤務時間が記録された列。各要素は以下の形式の辞書：
            {
                'date': datetime.date,  # 日付（例: '2025-04-01'）
                'times': list of dict  # 各辞書に datetime.time型の'start', 'end' を含む（例: '09:00'）
            }
        column_schedule_log (list): 各自のスケジュール（講義など）が記録された列。
            {
                'date': datetime.date,  # 日付（例: '2025-04-01'）
                'times': list of dict  # 各辞書に datetime.time型の'start', 'end' とstring型の'event'を含む（例: '09:00'）
            }
    Returns:
        bool: 重複があった場合はTrue、なかった場合はFalse。
        dict: 重複があった場合の詳細な情報を含む辞書。
            各辞書の例：
            {
                'date': datetime.date,
                'work_start': datetime.time,
                'work_end': datetime.time,
                'schedule_start': datetime.time,
                'schedule_end': datetime.time
            }
    """
    has_error = False
    errors = []
    for work_log in work_log_list:
        for schedule_log in schedule_log_list:
            if work_log['date'] == schedule_log['date']:
                for work_time in work_log['times']:
                    for schedule_time in schedule_log['times']:
                        if work_time['start'] <= schedule_time['end'] and work_time['end'] >= schedule_time['start']:
                            has_error = True
                            errors.append(f"勤務時間とスケジュールが重複しています: {work_log['date']}の{work_time['start']}-{work_time['end']}は{schedule_time['event']}の{schedule_time['start']}-{schedule_time['end']}と重複しています。")
    return has_error , errors




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
    has_error = False
    errors = []

    # 週単位の集計用
    weekly_minutes = collections.defaultdict(int)  # key: (year, week), value: minutes

    for entry in work_log_list:
        work_date = entry['date']
        times = entry['times']

        # --- 勤務可能時間帯 & 土日祝チェック ---
        if work_date.weekday() >= 5 or jpholiday.is_holiday(work_date):
            errors.append(f"{work_date} は土日または祝日です。勤務不可。")
            has_error = True

        total_minutes = 0
        times_sorted = sorted(times, key=lambda x: x['start'])

        # --- 勤務時間帯チェック & 総勤務時間計算 ---
        for period in times:
            s, e = period['start'], period['end']
            if not (time(8, 0) <= s <= time(20, 0)) or not (time(8, 0) <= e <= time(20, 0)):
                errors.append(f"{work_date} の勤務が勤務可能時間（8:00-20:00）外です。")
                has_error = True
            minutes = (datetime.combine(date.min, e) - datetime.combine(date.min, s)).seconds // 60
            total_minutes += minutes

        # --- 休憩チェック ---
        for i in range(len(times_sorted) - 1):
            end_current = times_sorted[i]['end']
            start_next = times_sorted[i + 1]['start']
            rest_minutes = (datetime.combine(date.min, start_next) - datetime.combine(date.min, end_current)).seconds // 60
            if rest_minutes >= 45:
                break  # OK
            else:
                if total_minutes >= 360:  # 6時間以上働く場合
                    errors.append(f"{work_date} の勤務が6時間以上連続ですが、45分以上の休憩がありません。")
                has_error = True

        if total_minutes > 465:
            errors.append(f"{work_date} の勤務時間が上限の7時間45分（465分）を超えています。")
            has_error = True
        # --- 週単位の記録 ---
        year, week_num, _ = work_date.isocalendar()
        weekly_minutes[(year, week_num)] += total_minutes

    # --- 週単位のチェック ---
    for (year, week), total in weekly_minutes.items():
        if total > 1200:
            errors.append(f"{year}年の第{week}週の勤務時間が20時間（1200分）を超えています。合計: {total}分")

    return has_error, errors

def check_employee_information(personal_info_df, budget_info_df, work_info_df):
    # JSONファイルを読み込む
    with open("employee_information.json", "r", encoding="utf-8") as f:
        employee_information = json.load(f)
    
    has_error = False
    errors = []
    
    student_id = str(personal_info_df["STUDENT_ID"].values[0])
    # 学生IDに対応する情報をemployee_information.jsonから取得
    employee_info = next((entry for entry in employee_information if entry["personal_info"]["STUDENT_ID"] == student_id), None)
    if employee_info is None:
        errors.append(f"STUDENT_ID {student_id} が employee_information.json に見つかりません。")
        has_error = True
        return has_error, errors
    
    # 比較対象の辞書データ
    fields_to_check = [
        # personal_info
        ("personal_info", "NAME", personal_info_df["NAME"].values[0]),
        ("personal_info", "AFFILIATION", personal_info_df["AFFILIATION"].values[0]),
        ("personal_info", "CONTACT", personal_info_df["CONTACT"].values[0]),
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
        expected_value = str(employee_info[section].get(key, "")).strip()
        df_value = str(value).strip()
        if expected_value != df_value:
            errors.append(f"{section} の {key} が一致しません。期待値: {expected_value}, 入力されている値: {df_value}")
            has_error = True
    
    return has_error, errors


def test_check_schedule():
    from datetime import date, time

    work_log_list = [
        {
            'date': date(2025, 4, 1),
            'times': [
                {'start': time(8, 0), 'end': time(12, 0)},
                {'start': time(13, 0), 'end': time(18, 0)}
            ]
        }
    ]

    schedule_log_list = [
        {
            'date': date(2025, 4, 1),
            'times': [
                {'start': time(9, 0), 'end': time(10, 30), 'event': '講義'}
            ]
        }
    ]

    has_error, errors = check_schedule(work_log_list, schedule_log_list)
    print("=== test_check_schedule ===")
    if has_error:
        for e in errors:
            print("⚠️", e)
    else:
        print("✅ スケジュールの重複なし")


def test_check_work_constraints_isct():
    from datetime import date, time

    work_log_list = [
        {
            'date': date(2025, 4, 1),
            'times': [
                {'start': time(8, 0), 'end': time(12, 0)},
                {'start': time(13, 0), 'end': time(18, 0)}
            ]
        },
        {
            'date': date(2025, 4, 6),  # 日曜日（祝日も含むチェック）
            'times': [
                {'start': time(9, 0), 'end': time(12, 0)}
            ]
        }
    ]

    has_error, errors = check_work_constraints_isct(work_log_list)
    print("=== test_check_work_constraints_isct ===")
    if has_error:
        for e in errors:
            print("⚠️", e)
    else:
        print("✅ 勤務条件違反なし")
        
def test_check_employee_information():
    # --- DataFrameを仮作成（JSONに合わせて作成） ---
    personal_info_df = pd.DataFrame([{
        "STUDENT_ID": "25D00150",
        "NAME": "蒲健太郎",
        "AFFILIATION": "理学院物理学系",
        "CONTACT": "2387"
    }])

    budget_info_df = pd.DataFrame([{
        "BUDGET_CODE_1": "11JYJY1000000000JY01ZZJY240221nn",
        "AFFILIATION_CONFIRM_1": "理学院物理学系",
        "NAME_CONFIRM_1": "大関真之"
    }])

    work_info_df = pd.DataFrame([{
        "WORK_TYPE_1": "RA",
        "HOURLY_WAGE_1": 3000,
        "EMPLOYEE_ID_1": "21061771"
    }])

    # --- テスト実行 ---
    has_error, errors = check_employee_information(personal_info_df, budget_info_df, work_info_df)

    # --- 結果表示 ---
    if has_error:
        print("❌ エラーが見つかりました：")
        for err in errors:
            print(" -", err)
    else:
        print("✅ 全て一致しています。テスト合格！")

# テスト関数呼び出し（スクリプト末尾に入れる）
if __name__ == "__main__":
    test_check_schedule()
    test_check_work_constraints_isct()
    test_check_employee_information()
