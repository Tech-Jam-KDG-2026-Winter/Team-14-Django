import datetime
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from django.conf import settings

SCOPES = ['https://www.googleapis.com/auth/fitness.activity.read']

def get_google_fit_steps(user, target_date=None):
    """
    特定のユーザーのGoogle Fitから歩数を取得する。
    """
    # 1. ユーザープロファイルから辞書形式の資格情報を取得
    credentials_data = getattr(user.profile, 'google_fit_credentials', None)
    
    if not credentials_data:
        raise ValueError("Google Fit連携が設定されていません。")

    # 修正ポイント: 'token' か 'access_token' のどちらかにある値を取得する
    access_token = credentials_data.get('token') or credentials_data.get('access_token')
    refresh_token = credentials_data.get('refresh_token')

    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_FIT_CLIENT_ID,
        client_secret=settings.GOOGLE_FIT_CLIENT_SECRET,
        scopes=SCOPES
    )

    # 2. トークンの有効期限切れをチェックして更新
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            
            # 修正：保存側と名前を確実に合わせるため、'token' キーで保存を統一する
            updated_credentials = {
                'token': creds.token,
                'refresh_token': creds.refresh_token or refresh_token,
            }
            user.profile.google_fit_credentials = updated_credentials
            user.profile.save()

    # 3. フィットネスデータの取得 (以下変更なし)
    service = build('fitness', 'v1', credentials=creds)
    
    if target_date is None:
        target_date = datetime.date.today()
        
    start_time = datetime.datetime.combine(target_date, datetime.time.min)
    end_time = datetime.datetime.combine(target_date, datetime.time.max)
    
    start_time_ms = int(start_time.timestamp() * 1000)
    end_time_ms = int(end_time.timestamp() * 1000)
    
    body = {
        "aggregateBy": [{"dataTypeName": "com.google.step_count.delta"}],
        "bucketByTime": { "durationMillis": 86400000 },
        "startTimeMillis": start_time_ms,
        "endTimeMillis": end_time_ms
    }
    
    dataset = service.users().dataset().aggregate(userId='me', body=body).execute()
    
    total_steps = 0
    for bucket in dataset.get('bucket', []):
        for dataset_item in bucket.get('dataset', []):
            for point in dataset_item.get('point', []):
                val = point['value'][0]
                total_steps += val.get('intVal', 0) + int(val.get('fpVal', 0))
                
    return total_steps