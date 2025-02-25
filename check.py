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
        else:
            st.write('祝日ではありません')        
        for j in range(len(schedule_standardized_df)):
            if work_standardized_df['Name'][i] == schedule_standardized_df['Name'][j]:
                if work_standardized_df['Date'][i] == schedule_standardized_df['Date'][j]:
                    if work_standardized_df['Start_Time'][i] <= schedule_standardized_df['End_Time'][j] and work_standardized_df['End_Time'][i] >= schedule_standardized_df['Start_Time'][j]:
                        has_error = True
                        manth_day = pd.to_datetime(work_standardized_df["Date"][i]).strftime("%m-%d")
                        st.warning(f'{manth_day}({work_standardized_df["Name"][i]})の{schedule_standardized_df["Start_Time"][j]}から{schedule_standardized_df["End_Time"][j]}は{schedule_standardized_df["Name"][j]}さんが{schedule_standardized_df["Description"][j]}に参加中であるため勤務できません。')
                        
    if has_error == False:
        st.write("報告された勤務時間は問題ありません")