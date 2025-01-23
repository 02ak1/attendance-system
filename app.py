import streamlit as st
import pandas as pd
from check_isct import check_schedule


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
        with pd.ExcelFile(work_file) as work_data, pd.ExcelFile(schedule_file) as schedule_data:
            work_df= work_data.parse(work_data.sheet_names[0],header=None)
            schedule_df = schedule_data.parse(schedule_data.sheet_names[0])
            check_schedule(work_df, schedule_df)
        col = st.columns(2)
        col[0].write("業務報告ファイル")
        col[1].write("スケジュールファイル")
        col[0].write(work_df)
        col[1].write(schedule_df)
    else:
        st.warning("両方のファイルをアップロードしてください")    
        #st.write(work_df)
        
    # # アップロードされたエクセルファイルを読み込む
    # _data = pd.ExcelFile(work_file)
    
    # # シート名を選択
    # sheet_name = st.selectbox("解析するシートを選択してください", excel_data.sheet_names)
    
    # # 選択したシートをデータフレームとして読み込む
    # df = _data.parse(sheet_name,header=None)
    
    # データを表示
    #st.subheader("データプレビュー")
    #st.write(df)
    
    