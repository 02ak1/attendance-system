import json
import pandas as pd
from datetime import datetime



# Excelファイルとシートの情報を取得
excel_path = "/Users/ozakiyuuta/Documents/東工大/T-qard/apps/schedule.xlsx"

# Excelからデータを読み込み
df_schedule_weekly    = pd.read_excel(excel_path, sheet_name="毎週の予定", header=0)
df_schedule_weekly=df_schedule_weekly[["名前", "曜日", "開始時間", "終了時間", "予定", "開始日", "終了日"]]
df_schedule_weekly = df_schedule_weekly.dropna(how="all").reset_index(drop=True)

df_schedule_non_weekly = pd.read_excel(excel_path, sheet_name="不定期の予定", header=0)



def make_timetable_schedule(name_input, df_schedule_weekly, df_schedule_non_weekly):
    """
    指定された名前のスケジュールを取得する関数
    parameters:
        name_input(str): 取得したい名前
        df_schedule_weekly(DataFrame): 毎週の予定のDataFrame
        df_schedule_non_weekly(DataFrame): 不定期の予定のDataFrame
    returns:
        timetables(list): 指定された名前のスケジュールのリスト 以下は例
            [
                {
                'date': Timestamp('2025-02-03 00:00:00'), 'times': [{'start': datetime.time(10, 0), 'end': datetime.time(10, 30), 'event': 'テスト'}]
                },
                {
                    'date': Timestamp('2024-04-01 00:00:00'), 'times': [{'start': datetime.time(9, 0), 'end': datetime.time(11, 0), 'event': '力学'}]
                    }
            ]
    """
    timetables = []
    
    #　不定期の予定を取得
    for i in range(len(df_schedule_non_weekly)):
        name = df_schedule_non_weekly['名前'][i]
        name = name.replace('　', '').replace(' ', '')
        if name != name_input:
            continue
        date = df_schedule_non_weekly['日付'][i]
        start_time = df_schedule_non_weekly['開始時間'][i]
        end_time = df_schedule_non_weekly['終了時間'][i]
        event = df_schedule_non_weekly['予定'][i]
        
        time_entry = {
        "start": start_time,
        "end": end_time,
        "event": event
        }

        # すでにその日付があるかチェック
        found = False
        for entry in timetables:
            if entry["date"] == date:
                entry["times"].append(time_entry)
                found = True
                break

        # なければ新しく追加
        if not found:
            timetable = {
                "date": date,
                "times": [time_entry]
            }
            timetables.append(timetable)
    
    # 毎週の予定を取得
    weekday_dict = {"月": 0, "火": 1, "水": 2, "木": 3, "金": 4, "土": 5, "日": 6}
    for i in range(len(df_schedule_weekly)):
        name = df_schedule_weekly['名前'][i]
        name = name.replace('　', '').replace(' ', '')
        if name != name_input:
            continue
        start_date = df_schedule_weekly['開始日'][i]
        end_date = df_schedule_weekly['終了日'][i]
        weekday_target = weekday_dict[df_schedule_weekly['曜日'][i]]
        
        if start_date > end_date:
            raise ValueError(f"開始日 ({start_date}) が終了日 ({end_date}) より後になっています。スケジュールを確認してください。")
        current_date = start_date
        while current_date <= end_date:
            # 曜日が一致する日だけ追加
            if current_date.weekday() == weekday_target:
                date = current_date
                start_time = df_schedule_weekly['開始時間'][i]
                end_time = df_schedule_weekly['終了時間'][i]
                event = df_schedule_weekly['予定'][i]
                
                time_entry = {
                    "start": start_time,
                    "end": end_time,
                    "event": event
                }

                # すでにその日付があるかチェック
                found = False
                for entry in timetables:
                    if entry["date"] == date:
                        entry["times"].append(time_entry)
                        found = True
                        break

                # なければ新しく追加
                if not found:
                    timetable = {
                        "date": date,
                        "times": [time_entry]
                    }
                    timetables.append(timetable)
            current_date += pd.Timedelta(days=1)
            
    return timetables

if __name__ == "__main__":
    name_input = "尾崎優太"
    timetables = make_timetable_schedule(name_input, df_schedule_weekly, df_schedule_non_weekly)
    print(timetables)