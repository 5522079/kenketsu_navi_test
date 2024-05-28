import pandas as pd
from matplotlib import pyplot as plt
import japanize_matplotlib

# CSVファイルを読み込む
file_path = "../data/BloodDonation.csv"
df = pd.read_csv(file_path)

# year列とmonth列を結合してdate列を作成
df['date'] = pd.to_datetime((df['year'].astype(str)) + '-' + (df['month'].astype(str)))

# dateごとのblood_donorsの総和を求めグループ化
grouped_date_total = df.groupby(['date'])['blood_donors'].sum().to_frame()

# 予測期間のデータフレームを作成
latest_date = df['date'].max() # 最新の日付を取得
start_date = latest_date + pd.DateOffset(months=1) # 予測期間の開始日と終了日を取得
end_date = latest_date + pd.DateOffset(months=3)
future_dates = pd.date_range(start_date, end_date, freq='MS') # 予測期間のインデックスを作成
model_forecast_result = pd.DataFrame(index=future_dates, columns=['blood_donors'])

# 学習データを作成
train = grouped_date_total

# 学習
from statsmodels.tsa.statespace.sarimax import SARIMAX
sarima_model = SARIMAX(train, order=(1, 0, 1), seasonal_order=(1, 1, 1, 10))
sarima_fit = sarima_model.fit()

# 予測
model_forecast_result['blood_donors'] = sarima_fit.forecast(steps=len(model_forecast_result.index))

# グラフデータの準備
# 棒グラフのデータを用意する
bar_data = grouped_date_total[-21:-9]
bar_data.index += pd.DateOffset(years=1)

# 折れ線グラフのデータを用意する
latest_data = grouped_date_total[-9:] # 最新のデータ
model_data = model_forecast_result # 予測データ
plot_data = pd.concat([latest_data, model_data])

# グラフ化
# グラフのスタイルとサイズ
plt.style.use('fast')
plt.rcParams['figure.figsize'] = [12, 9]

# 折れ線グラフのデータをセット
plt.plot(plot_data.index, plot_data['blood_donors'], color="#FF7628", marker='d', markersize=6)
plt.plot(plot_data[-3:].index, plot_data[-3:]['blood_donors'], color="#01B7D6", marker='o', markersize=8)

# 棒グラフのデータをセット
plt.bar(bar_data.index, bar_data['blood_donors'], width=12, color="#FFBBBB", alpha=1)

# グラフの詳細設定
plt.title("全国の総献血者数の推移と予測")
plt.legend(["献血者数", "予測献血者数", "昨年の献血者数"])
plt.ylabel("献\n血\n者\n数", rotation=0)
plt.xticks(plot_data.index, [(date.strftime('%Y-%m')) for date in plot_data.index], rotation=0)
plt.yticks([_ + 20000 for _ in range(360000, 460000, 10000)], range(360000, 460000, 10000))
plt.ylim(380000, 460000)
plt.grid(axis='y')

# グラフを保存
plt.savefig('../static/images/data/model_graph.png')
plt.close()
