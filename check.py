import pandas as pd
import streamlit as st
from standardizer_isct import standardize_schedule, standardize_work
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
                'date': str,
                'work_start': str,
                'work_end': str,
                'schedule_start': str,
                'schedule_end': str
            }
    """
    has_error = False
    error_list = []
    for work_log in work_log_list:
        for schedule_log in schedule_log_list:
            if work_log['date'] == schedule_log['date']:
                for work_time in work_log['times']:
                    for schedule_time in schedule_log['times']:
                        if work_time['start'] <= schedule_time['end'] and work_time['end'] >= schedule_time['start']:
                            has_error = True
                            error_list.append({
                                'date': work_log['date'],
                                'work_start': work_time['start'],
                                'work_end': work_time['end'],
                                'schedule_start': schedule_time['start'],
                                'schedule_end': schedule_time['end']
                            })
                            
    return has_error, error_list
