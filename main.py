# import
import os
from dotenv import load_dotenv
import urllib.parse
import requests
import json
import pandas as pd

def main():
    # 定数定義
    MAX_RESULT_PER_REQUEST = 100 # 1回のリクエストで取得する件数（URL仕様上，上限100）

    # クエリを1回発行し，ヒット件数を取得する．
    response = get(1,1)
    response_body = response.json()
    hit_count = int(response_body['ResultInfo']['Total'])

    # ヒット件数と1回のリクエストで取得する件数より，必要なループ回数を取得する．
    loop_num = -((-1)*hit_count // MAX_RESULT_PER_REQUEST)

    # 結果を格納するDataFrameを作成
    df = pd.DataFrame(data=[[]])

    for i in range(loop_num):
        response = get(1 + (i *MAX_RESULT_PER_REQUEST), MAX_RESULT_PER_REQUEST)
        response_body = response.json()

        # 取得した各店舗情報をループ
        for sp in response_body['Feature']:
            # 店舗ID
            shop_id = sp['Id']
            # 店舗名
            shop_name = sp['Name']

            # 最寄り駅を取得してループ
            station_list = sp['Property']['Station']
            if len(station_list) > 0:
                for st in station_list:
                    # 稀にIdが空（SubIdはある）Stationがヒットする（鉄道駅ではなく港など？）のでその場合は無視．
                    if 'Id' in st:
                        # ['店舗ID', '店舗名称', '駅ID', '駅名']の形式でデータフレームに追加
                        data = [{'店舗ID': shop_id, '店舗名':shop_name, '駅ID':st['Id'], '駅名':st['Name']}]
                        tmp_df = pd.DataFrame(data)
                        df = pd.concat([df, tmp_df])
    
    # 重複データを削除する
    df = df.drop_duplicates()
    print(df)

    # 駅IDのID別出現回数
    st_cnt = df['駅名'].value_counts()
    print(st_cnt)
 
    


# Yahooローカルサーチに対してGETリクエストを発行し，そのレスポンスを返す変数．
# 引数:
#  start：何件目から取得するか
#  max_result_per_request：最大何件取得するか
def get(start, max_result_per_request):
    # envファイル読み込み
    load_dotenv()
    CLIENT_ID = os.environ['CLIENT_ID']

    # アクセスするAPIの定義
    API_URL_BASE = 'https://map.yahooapis.jp/search/local/V1/localSearch?appid=' + CLIENT_ID + '&output=json&query=ココカラファイン'

    # 引数からURLを組み立て
    url = API_URL_BASE + '&start=' + str(start) + '&results=' + str(max_result_per_request)

    # GETリクエスト発行
    response = requests.get(url)
    print(url)

    return response

main()
