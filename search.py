import pandas as pd

df0 = pd.read_excel("r07kinmu.xlsx", sheet_name=0, index_col=0)
df3 = pd.read_excel("r07kinmu.xlsx", sheet_name=3, index_col=0)
# print(df0.head(10))
# print(df3.head(10))

# 探したい値
target_value = "蒲 健太郎"

# 条件に一致する要素の位置を取得
result = (df0 == target_value)

# Trueになっている場所（存在する場所）をインデックスと列ラベルで取得
positions = list(zip(*result.values.nonzero()))

# 行・列ラベルを表示
for row_idx, col_idx in positions:
    print(f"{row_idx}, {col_idx}")

# print(df0.iloc["row_idx", "col_idx"])