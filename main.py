iimport requests
import json
import folium
from folium import plugins
from datetime import datetime

# APIから地震データを取得
url = "https://api.p2pquake.net/v2/history?codes=551&limit=100"
data = []

for i in range(20):
    offset = i * 100
    response = requests.get(url + "&offset=" + str(offset))
    data += response.json()

# マップに表示する色を決定する関数
def color(magnitude, depth):
    if magnitude < 4:
        return 'green'
    elif magnitude < 5:
        return 'blue'
    elif magnitude < 6:
        return 'orange'
    else:
        return 'red'

# 地震データのリストを作成
features = []
times = []

for d in data:
    time_str = d['earthquake']['time']
    # 時間フォーマットをISO 8601形式に変換
    try:
        time = datetime.strptime(time_str, "%Y/%m/%d %H:%M:%S.%f").strftime('%Y-%m-%dT%H:%M:%SZ')
    except ValueError:
        time = datetime.strptime(time_str, "%Y/%m/%d %H:%M:%S").strftime('%Y-%m-%dT%H:%M:%SZ')
    times.append(time)
    latitude = d['earthquake']['hypocenter']['latitude']
    longitude = d['earthquake']['hypocenter']['longitude']
    magnitude = d['earthquake']['hypocenter']['magnitude']
    depth = d['earthquake']['hypocenter']['depth']
    
    feature = {
        'type': 'Feature',
        'geometry': {
            'type': 'Point',
            'coordinates': [longitude, latitude]
        },
        'properties': {
            'time': time,
            'style': {
                'color': 'black',
                'fillColor': color(magnitude, depth),
                'weight': 2,
                'fillOpacity': 0.7,
                'radius': magnitude * 2
            },
            'icon': 'circle',
            'popup': time_str
        }
    }
    features.append(feature)

# GeoJsonのデータを作成
geojson = {
    'type': 'FeatureCollection',
    'features': features
}

# 地図を作成
m = folium.Map(location=[35.68, 139.76], zoom_start=5)

# タイムスタンプ付きのGeoJsonを追加
plugins.TimestampedGeoJson(
    geojson,
    transition_time=1,
    auto_play=True,
    loop=False,
    add_last_point=False,
    time_slider_drag_update=True,
    period='PT10M',  # 1分ごとに更新
    duration='P1D'
).add_to(m)

# 地図を保存
m.save('earthquake_animation.html')


# 図を表示
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

plt.figure(figsize=(10, 6))
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=120))
plt.plot(times, [d['earthquake']['hypocenter']['magnitude'] for d in data], 'ro')
plt.gcf().autofmt_xdate()
plt.xlabel('Date and Time')
plt.ylabel('Magnitude')
plt.title('Earthquake Magnitude over Time')
plt.savefig('earthquake_magnitude.png')

