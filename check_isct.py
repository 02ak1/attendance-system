import pandas as pd
import streamlit as st
def check_schedule(work_df,schedule_df):
    has_error = False
    if pd.isnull(work_df.iloc[1][11]):
        st.write('業務時間表に名前が入力されていません')
        return
    name=work_df.iloc[1][11] #名前の取得
    name = name.replace('　', '').replace(' ', '')
    for i in range(6,len(work_df)):
        day_of_week = work_df.iloc[i][2]
        for j in range(4,17,4):
            if pd.isnull(work_df.iloc[i][j]):
                continue
            start_time = work_df.iloc[i][j]
            end_time = work_df.iloc[i][j+1]
            for k in range(len(schedule_df)):
                schedule_df['Name'][k]=schedule_df['Name'][k].replace('　', '').replace(' ', '')
                if name != schedule_df['Name'][k]:
                    continue
                if day_of_week == schedule_df['Day_of_Week'][k]:
                    if start_time<=schedule_df['End_Time'][k] and end_time>=schedule_df['Start_Time'][k]:
                        has_error = True
                        st.warning(f'{work_df.iloc[i][1].date()}({work_df.iloc[i][2]})の{schedule_df["Start_Time"][k]}から{schedule_df["End_Time"][k]}は{schedule_df["Name"][k]}さんが{schedule_df["Description"][k]}に参加中であるため勤務できません。')
    if has_error == False:
        st.write("報告された勤務時間は問題ありません")

# with pd.ExcelFile('work.xlsx') as work_data, pd.ExcelFile('schedule.xlsx') as schedule_data:
    
#     # ファイル操作
#     work_df= work_data.parse(work_data.sheet_names[0],header=None)
#     schedule_df = schedule_data.parse(schedule_data.sheet_names[0])
#     #print(work_df[:][2])
    
#     # for i in range(6,len(work_df)):
#     #     day_of_week = work_df.iloc[i][2]
#     #     for j in range(4,17,4):
#     #         if pd.isnull(work_df.iloc[i][j]):
#     #             continue
#     #         start_time = work_df.iloc[i][j]
#     #         end_time = work_df.iloc[i][j+1]
#     #         for k in range(len(schedule_df)):
#     #             if day_of_week == schedule_df['Day_of_Week'][k]:
#     #                 if start_time<=schedule_df['End_Time'][k] and end_time>=schedule_df['Start_Time'][k]:
#     #                     print(f'エラー:{work_df.iloc[i][1].date()}({work_df.iloc[i][2]})の{schedule_df["Start_Time"][k]}から{schedule_df["End_Time"][k]}は{schedule_df["Name"][k]}さんが{schedule_df["Description"][k]}中のため勤務できません。')
                        
#     check_schedule(work_df,schedule_df)
