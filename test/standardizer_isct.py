import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import jpholiday

def standardize_schedule(file,standardized_data_df=None):
    schedule_data = pd.ExcelFile(file)
    schedule_weekly_df= schedule_data.parse(schedule_data.sheet_names[0])
    schedule_non_weekly_df= schedule_data.parse(schedule_data.sheet_names[1])
    schedule_weekly_df=schedule_weekly_df[["名前", "曜日", "開始時間", "終了時間", "予定", "開始日", "終了日"]]
    # **完全に空の行を削除**
    schedule_weekly_df = schedule_weekly_df.dropna(how="all").reset_index(drop=True)
    schedule_non_weekly_df['日付'] = schedule_non_weekly_df['日付'].dt.strftime('%Y-%m-%d')
    data_list=[]
    for i in range(len(schedule_non_weekly_df)):
        name= schedule_non_weekly_df['名前'][i]
        name = name.replace('　', '').replace(' ', '')
        data_list.append({'Name':name,'Date':schedule_non_weekly_df['日付'][i],'Start_Time':schedule_non_weekly_df['開始時間'][i],'End_Time':schedule_non_weekly_df['終了時間'][i],'Description':schedule_non_weekly_df['予定'][i]})
    
    weekday_dict = {"月": 0, "火": 1, "水": 2, "木": 3, "金": 4, "土": 5, "日": 6}
    for _, row in schedule_weekly_df.iterrows():
        start_date = pd.to_datetime(row["開始日"])
        end_date = pd.to_datetime(row["終了日"])
        weekday_target = weekday_dict[row["曜日"]]
        
        if start_date > end_date:
            st.warning(f'{_}行目の開始日が終了日より後になっています')
        
        current_date = start_date
        while current_date <= end_date:
            # 曜日が一致する日だけ追加
            if current_date.weekday() == weekday_target:
                name = row['名前']
                name = name.replace('　', '').replace(' ', '')
                data_list.append({
                    "Name": name,
                    "Date": current_date.strftime("%Y-%m-%d"),
                    "Start_Time": row["開始時間"],
                    "End_Time": row["終了時間"],
                    "Description": row["予定"],
                })
            current_date += timedelta(days=1)  # 1日ずつ増やす
    data_df = pd.DataFrame(data_list)
    if standardized_data_df is None:
        schedule_standardized_df = data_df
    else:
        schedule_standardized_df = pd.concat([data_df, schedule_standardized_df],ignore_index=True,axis=0)
    return schedule_standardized_df
def standardize_work(file, work_standardized_df=None):
    work_data = pd.ExcelFile(file)
    work_df= work_data.parse(work_data.sheet_names[0],header=None)
    name=work_df.iloc[1][11] #名前の取得
    name = name.replace('　', '').replace(' ', '')
    data_list = []
    for i in range(6,len(work_df)):
        if work_df.iloc[i][1] == False:
            continue
        date = work_df.iloc[i][1].strftime("%Y-%m-%d")
        for j in range(4,17,4):
            if pd.isnull(work_df.iloc[i][j]):
                print(work_df.iloc[i][j])
                continue
            data_list.append({
                "Name": name,
                "Date": date,
                "Start_Time": work_df.iloc[i][j],
                "End_Time": work_df.iloc[i][j+1],
                "Weekday": work_df.iloc[i][1].strftime("%A"),
                "is_holiday": jpholiday.is_holiday(work_df.iloc[i][1])#祝日かどうか
            })
    data_df = pd.DataFrame(data_list)
    if work_standardized_df is None:
        work_standardized_df = data_df
    else:
        work_standardized_df = pd.concat([data_df, work_standardized_df],ignore_index=True,axis=0)
    return work_standardized_df
# file='schedule_2.xlsx'
# schedule_df = standardize_schedule(file)
# print(schedule_df)

# file='work.xlsx'
# work_df = standardize_work(file)
# print(work_df)