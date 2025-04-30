import os
import json
import pandas as pd
def run():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    CONFIG_PATH = os.path.join(base_dir, "data", "location_workreport.json")
    with open(CONFIG_PATH, encoding="utf-8") as f:
        config = json.load(f)

    # Excelファイルとシートの情報を取得
    excel_path = config["sheet_info"]["EXCEL_PATH"]
    REPORT     = config["sheet_info"]["REPORT"]
    TIMETABLE  = config["sheet_info"]["TIMETABLE"]

    # Excelからデータを読み込み（すべて文字列として読み込むのが安全）
    df_report    = pd.read_excel(excel_path, sheet_name=REPORT,    index_col=0)
    df_timetable = pd.read_excel(excel_path, sheet_name=TIMETABLE, index_col=0)
    return df_report, df_timetable, config