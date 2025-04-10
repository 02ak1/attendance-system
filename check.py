import pandas as pd
import streamlit as st
from standardizer_isct import standardize_schedule, standardize_work

from datetime import datetime, date, time, timedelta
import jpholiday
import collections

def check_time(work_file,schedule_file):
    has_error = False
    work_standardized_df = standardize_work(work_file)
    schedule_standardized_df = standardize_schedule(schedule_file)
    for i in range(len(work_standardized_df)):
        if work_standardized_df["is_holiday"][i] == True:
                st.warning(f'{work_standardized_df["Name"][i]}さん、{work_standardized_df["Date"][i]}は祝日のため勤務できません')
                has_error = True
                continue       
        for j in range(len(schedule_standardized_df)):
            if work_standardized_df['Name'][i] == schedule_standardized_df['Name'][j]:
                if work_standardized_df['Date'][i] == schedule_standardized_df['Date'][j]:
                    if work_standardized_df['Start_Time'][i] <= schedule_standardized_df['End_Time'][j] and work_standardized_df['End_Time'][i] >= schedule_standardized_df['Start_Time'][j]:
                        has_error = True
                        manth_day = pd.to_datetime(work_standardized_df["Date"][i]).strftime("%m-%d")
                        st.warning(f'{manth_day}({work_standardized_df["Name"][i]})の{schedule_standardized_df["Start_Time"][j]}から{schedule_standardized_df["End_Time"][j]}は{schedule_standardized_df["Name"][j]}さんが{schedule_standardized_df["Description"][j]}に参加中であるため勤務できません。')
                        
    if has_error == False:
        st.write("報告された勤務時間は問題ありません")


def check_schedule(work_log_list, schedule_log_list):
    """
    勤務時間とスケジュールの重複をチェックする関数。

    Parameters:
        column_work_log (list): 勤務時間が記録された列。各要素は以下の形式の辞書：
            {
                'date': datetime.date,  # 日付（例: '2025-04-01'）
                'times': list of dict  # 各辞書に datetime.time型の'start', 'end' の時刻を含む（例: '09:00'）
            }
        column_schedule_log (list): 各自のスケジュール（講義など）が記録された列。
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
    error_dict = []
    for work_log in work_log_list:
        for schedule_log in schedule_log_list:
            if work_log['date'] == schedule_log['date']:
                for work_time in work_log['times']:
                    for schedule_time in schedule_log['times']:
                        if work_time['start'] <= schedule_time['end'] and work_time['end'] >= schedule_time['start']:
                            has_error = True
                            error_dict.append({
                                'date': work_log['date'],
                                'work_start': work_time['start'],
                                'work_end': work_time['end'],
                                'schedule_start': schedule_time['start'],
                                'schedule_end': schedule_time['end']
                            })
                            
    return has_error, error_dict




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
                {'start': time(9, 0), 'end': time(10, 30)}
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

# テスト関数呼び出し（スクリプト末尾に入れる）
if __name__ == "__main__":
    test_check_schedule()
    test_check_work_constraints_isct()
