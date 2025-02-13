import streamlit as st
import pandas as pd
from check_test import check_schedule


# タイトルの設定
st.title("勤怠管理アプリ")

# ファイルアップロード機能
work_file = st.file_uploader("科学大の業務報告ファイルをアップロードしてください", type=["xlsx"])
schedule_file = st.file_uploader("記入済みのスケジュールファイルをアップロードしてください", type=["xlsx"])

file_path = "schedule.xlsx"
# ファイルを読み込んでバイナリデータを取得
with open(file_path, "rb") as file:
    file_data = file.read()
# ダウンロードボタンを表示
st.download_button(
    label="スケジュールファイルのダウンロードはこちらから",
    data=file_data,
    file_name="schedule.xlsx",
    mime="application/vnd.ms-excel"
)
if st.button("確認する"):
    if work_file and schedule_file:
        check_schedule(work_file, schedule_file)
        work_data = pd.ExcelFile(work_file) 
        work_df= work_data.parse(work_data.sheet_names[0],header=None)
        st.write("業務報告ファイル")
        st.write(work_df)
        
        schedule_data = pd.read_excel(schedule_file, sheet_name=None, header=None)

        # シートごとにデータを表示
        for sheet_name, df in schedule_data.items():
            st.write("スケジュールファイル")
            st.write(f"📄 シート: {sheet_name}")
            st.write(df)

    else:
        st.warning("両方のファイルをアップロードしてください")


    
    