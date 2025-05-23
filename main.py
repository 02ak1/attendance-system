from read_information import make_df_workreport, make_timetable
from read_schedule import make_timetable_schedule
from check import check_schedule, check_work_constraints_isct, check_employee_information

import json
import pandas as pd
from datetime import datetime
import os
import streamlit as st

def checker(df_report, df_timetable):
    
    # JSONファイルの読み込み
    with open("location_workreport.json", encoding="utf-8") as f:
        config = json.load(f)
    # データフレームの作成
    report = make_df_workreport(df_report, config)
    personal_info_df, budget_info_df, work_info_df, date_info_df, signature_df = report.export_df()
    name_input = personal_info_df["NAME"][0]
    timetables_work = make_timetable(df_timetable, date_info_df)
    
    # スケジュールの読み込み
    # このファイル（main.py）からの相対パスでExcelファイルを指定
    BASE_DIR = "" #os.path.dirname(__file__)
    excel_schedule = os.path.join(BASE_DIR, "schedule.xlsx")
    df_schedule_weekly    = pd.read_excel(excel_schedule, sheet_name="毎週の予定", header=0)
    df_schedule_weekly=df_schedule_weekly[["名前", "曜日", "開始時間", "終了時間", "予定", "開始日", "終了日"]]
    df_schedule_weekly = df_schedule_weekly.dropna(how="all").reset_index(drop=True)
    df_schedule_non_weekly = pd.read_excel(excel_schedule, sheet_name="不定期の予定", header=0)
    
    timetables_schedule=make_timetable_schedule(name_input, df_schedule_weekly, df_schedule_non_weekly)
    
    errors = []
    
    # スケジュールのチェック
    errors += check_schedule(timetables_work, timetables_schedule)
    # 勤務条件のチェック
    errors += check_work_constraints_isct(timetables_work)
    # 社員情報のチェック
    errors += check_employee_information(personal_info_df, budget_info_df, work_info_df)
    
    return errors
    
if __name__ == "__main__":
    excel_path = "/Users/ozakiyuuta/Documents/東工大/T-qard/apps/4月業務時間表_尾崎優太.xlsx"
    errors = checker(excel_path)
    
    if errors:
        print("エラーが見つかりました:")
        for error in errors:
            print(error)
    else:
        print("エラーは見つかりませんでした。")