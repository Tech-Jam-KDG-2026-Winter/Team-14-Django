import os
import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# 許可をもらう範囲
SCOPES = ['https://www.googleapis.com/auth/fitness.activity.read']

def main():
    # 認証用ファイルの名前
    client_secrets_file = 'credentials.json' 
    
    # 認証の準備
    flow = InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, 
        scopes=SCOPES,
        redirect_uri='http://localhost:8080/'
    )
    
    # 認証実行（ブラウザが開きます）
    creds = flow.run_local_server(host='localhost', port=8080, prompt='consent')
    service = build('fitness', 'v1', credentials=creds)

    # 「今日の開始(00:00)」と「現在の時刻」を取得
    now = datetime.datetime.now()
    today_start = datetime.datetime(now.year, now.month, now.day)
    
    # Google Fitに送るための時間データ（ミリ秒）
    start_time_ms = int(today_start.timestamp() * 1000)
    end_time_ms = int(now.timestamp() * 1000)

    # 歩数を集計するためのリクエスト内容
    body = {
        "aggregateBy": [{
            "dataTypeName": "com.google.step_count.delta" 
            # ↑ dataSourceId を消して、データタイプだけにしました。
            # これでGoogleが最適なデータソースを自動で選んでくれます。
        }],
        "bucketByTime": { "durationMillis": 86400000 }, # 24時間単位
        "startTimeMillis": start_time_ms,
        "endTimeMillis": end_time_ms
    }

    # Googleにデータを「ちょうだい！」とリクエスト
    dataset = service.users().dataset().aggregate(userId='me', body=body).execute()

    # 結果を表示
    print("\n" + "="*30)
    found = False
    for bucket in dataset.get('bucket', []):
        for dataset_item in bucket.get('dataset', []):
            for point in dataset_item.get('point', []):
                steps = point['value'][0]['intVal']
                print(f"👟 今日の歩数: {steps} 歩")
                found = True
    
    if not found:
        print("👟 今日の歩数はまだ 0 歩か、データが見つかりませんでした。")
        print("（スマホのGoogle Fitアプリで同期されているか確認してください）")
    print("="*30 + "\n")

if __name__ == '__main__':
    main()