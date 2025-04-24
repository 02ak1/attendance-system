import json
import pandas as pd
from datetime import datetime

# JSONファイルの読み込み
with open("location_workreport.json", encoding="utf-8") as f:
    config = json.load(f)

# Excelファイルとシートの情報を取得
excel_path = config["sheet_info"]["EXCEL_PATH"]
REPORT     = config["sheet_info"]["REPORT"]
TIMETABLE  = config["sheet_info"]["TIMETABLE"]

# Excelからデータを読み込み（すべて文字列として読み込むのが安全）
df_report    = pd.read_excel(excel_path, sheet_name=REPORT,    index_col=0)
df_timetable = pd.read_excel(excel_path, sheet_name=TIMETABLE, index_col=0)

# 機能：指定位置からデータを取り出して1行だけのDataFrameにする関数
class make_df_workreport:
    def __init__(self, df_report):
        self.df_report = df_report

    def make_df(self, block_config):
        df_report = self.df_report
        data = {}
        for key, (row, col) in block_config.items():
            value = df_report.iat[row, col]  # 指定位置の値を取得
            data[key] = value
        return pd.DataFrame([data])  # 1行のDataFrameとして返す

    def export_df(self):
        personal_info_df     = make_df_workreport.make_df(config["personal_info"])
        budget_info_df       = make_df_workreport.make_df(config["budget_info_1"])
        work_info_df         = make_df_workreport.make_df(config["work_info_1"])
        date_info_df         = make_df_workreport.make_df(config["date"])
        date_info_df["DAYS"] = (date_info_df["DATE_END"] - date_info_df["DATE_START"]).dt.days + 1
        signature_df         = make_df_workreport.make_df(config["signature"])
        
        return personal_info_df, budget_info_df, work_info_df, date_info_df, signature_df

# print(df_timetable.iloc[5+int, 2])

def make_timetable(df_timetable, date_info_df):
    df_timetable = df_timetable
    date_info_df = date_info_df
    
    # JSONから設定値を取得
    tt_begin_row = config["timetable_info"]["START"][0]
    tt_begin_col = config["timetable_info"]["START"][1]
    budget_col = config["timetable_info"]["BUDGET_COL"]
    start_col = config["timetable_info"]["START_COL"]
    end_col = config["timetable_info"]["END_COL"]
    check1_col = config["timetable_info"]["CHECK1_COL"]
    check2_col = config["timetable_info"]["CHECK2_COL"]
    
    timetables = []
    for int in range(date_info_df["DAYS"][0]):
        timetable = {}
        timetable["date"] = df_timetable.iloc[tt_begin_row+int, tt_begin_col]
        timetable["times"] = []
        timetable["checks"] = []

        for i in range(4):
            time = {}
            time["budget"] = df_timetable.iloc[tt_begin_row+int, budget_col+4*i], 
            time["start"]  = df_timetable.iloc[tt_begin_row+int, start_col+4*i],
            time["end"]    = df_timetable.iloc[tt_begin_row+int, end_col+4*i],
            timetable["times"].append(time)

        check = {}
        check["check1"] = df_timetable.iloc[tt_begin_row+int, check1_col]
        check["check2"] = df_timetable.iloc[tt_begin_row+int, check2_col]
        timetable["checks"].append(check)
        
        timetables.append(timetable)
        
    return timetables
