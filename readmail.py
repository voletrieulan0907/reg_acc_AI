import requests
import json
import time
import re
from twocaptcha import TwoCaptcha

API_KEY_DEFAULT = "35aa7bbf75db184cb0219c9d497d74ac"
PAGE_URL = "https://smailpro.com/temporary-email"
SITEKEY = "0x4AAAAAAABIS_gEec2IwOhI"

headers_smail = {
    'accept': '*/*',
    'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
    'content-type': 'application/json',
    'origin': 'https://smailpro.com',
    'referer': 'https://smailpro.com/temporary-email',
    'sec-ch-ua': '"Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36',
}

headers_sonjj = {
    'accept': '*/*',
    'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
    'origin': 'https://smailpro.com',
    'priority': 'u=1, i',
    'referer': 'https://smailpro.com/',
    'sec-ch-ua': '"Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36',
}


def create_email(captcha_key=API_KEY_DEFAULT):
    """
    Tạo Email tạm thời mới trên Smailpro và trả về dict (address, timestamp, key)
    """
    solver = TwoCaptcha(captcha_key)
    res = solver.turnstile(sitekey=SITEKEY, url=PAGE_URL)
    captcha_token = res.get('code')

    req_headers = headers_smail.copy()
    req_headers['x-captcha'] = captcha_token

    params = {
        'username': 'random',
        'type': 'alias',
        'domain': 'tokyo.edu.pl',
        'server': '1',
    }

    r = requests.get('https://smailpro.com/app/create', params=params, headers=req_headers, timeout=25)
    data = r.json()
    
    return {
        'address': data.get('address'),
        'timestamp': data.get('timestamp'),
        'key': data.get('key')
    }


def get_message_detail(mid, payload_jwt):
    """
    Lấy chi tiết nội dung (HTML/body) chứa mã OTP của một email qua mid
    """
    # Các endpoint GET trên sonjj API
    get_endpoints = [
        ("https://api.sonjj.com/v1/temp_email/id", {"mid": mid, "payload": payload_jwt}),
        ("https://api.sonjj.com/v1/temp_email/message", {"mid": mid, "payload": payload_jwt}),
        ("https://api.sonjj.com/v1/temp_email/read", {"mid": mid, "payload": payload_jwt}),
        ("https://api.sonjj.com/v1/temp_email/inbox", {"mid": mid, "payload": payload_jwt}),
        ("https://api.sonjj.com/v1/temp_email/detail", {"mid": mid, "payload": payload_jwt}),
        ("https://api.sonjj.com/v1/temp_email/body", {"mid": mid, "payload": payload_jwt}),
    ]
    for url, params in get_endpoints:
        try:
            r = requests.get(url, params=params, headers=headers_sonjj, timeout=4)
            if r.status_code == 200 and r.text:
                data = r.json()
                if isinstance(data, dict) and any(k in data for k in ('body', 'html', 'content', 'text', 'message', 'data')):
                    print(f"✅ Thành công lấy body mail từ GET {url}")
                    return data
        except Exception:
            pass

    # Các endpoint POST trên smailpro API
    post_endpoints = [
        ("https://smailpro.com/app/message", {"mid": mid, "payload": payload_jwt}),
        ("https://smailpro.com/app/read", {"mid": mid, "payload": payload_jwt}),
    ]
    for url, body_data in post_endpoints:
        try:
            r = requests.post(url, json=body_data, headers=headers_smail, timeout=4)
            if r.status_code == 200 and r.text:
                data = r.json()
                if isinstance(data, dict) and any(k in data for k in ('body', 'html', 'content', 'text', 'message', 'data')):
                    print(f"✅ Thành công lấy body mail từ POST {url}")
                    return data
        except Exception:
            pass

    return {}


def read_inbox_by_key(address, timestamp, key):
    """
    Đọc toàn bộ hòm thư của 1 email dựa trên address, timestamp và key.
    """
    body_inbox = [{
        "address": address,
        "timestamp": int(timestamp),
        "key": key
    }]
    
    r1 = requests.post('https://smailpro.com/app/inbox', json=body_inbox, headers=headers_smail, timeout=10)
    data1 = r1.json()
    
    if not isinstance(data1, list) or len(data1) == 0:
        return []
        
    payload_jwt = data1[0].get('payload')
    if not payload_jwt:
        return []

    r2 = requests.get('https://api.sonjj.com/v1/temp_email/inbox', params={'payload': payload_jwt}, headers=headers_sonjj, timeout=10)
    data2 = r2.json()
    messages = data2.get('messages', [])

    full_messages = []
    for msg in messages:
        mid = msg.get('mid')
        if mid:
            detail = get_message_detail(mid, payload_jwt)
            if isinstance(detail, dict) and detail:
                msg_combined = msg.copy()
                msg_combined.update(detail)
                full_messages.append(msg_combined)
            else:
                full_messages.append(msg)
        else:
            full_messages.append(msg)

    return full_messages


def get_all_strings_from_obj(obj):
    """
    Hàm hỗ trợ đệ quy lấy toàn bộ chuỗi text trong đối tượng dict/list (bỏ qua các trường metadata ID)
    """
    strings = []
    if isinstance(obj, str):
        strings.append(obj)
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if k.lower() in ('mid', 'id', '_id', 'messageid', 'date', 'textdate', 'timestamp', 'created_at'):
                continue
            strings.extend(get_all_strings_from_obj(v))
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            strings.extend(get_all_strings_from_obj(item))
    return strings


def extract_otp_from_message(msg):
    """
    Trích xuất chính xác mã OTP 4 số từ message email.
    """
    # 1. Thu thập toàn bộ văn bản từ message (kể cả body, html, snippet, subject...)
    raw_strings = get_all_strings_from_obj(msg)
    full_text = " ".join(raw_strings)

    # 2. Làm sạch HTML, mã entity và các định dạng nhiễu (UUID, Ngày tháng)
    clean_text = re.sub(r'<[^>]+>', ' ', full_text)
    clean_text = re.sub(r'&[a-zA-Z0-9#]+;', ' ', clean_text)
    clean_text = re.sub(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}', ' ', clean_text)
    clean_text = re.sub(r'\d{4}-\d{2}-\d{2}[T\s]?\d{2}:\d{2}:\d{2}?', ' ', clean_text)
    clean_text = re.sub(r'\\n|\\r|\\t|\\"', ' ', clean_text)

    # 3. Quét tất cả các vị trí xuất hiện từ khóa xác nhận
    keywords = ['mã', 'code', 'verify', 'verification', 'xác minh', 'xác thực', 'roboneo', 'meitu']
    clean_lower = clean_text.lower()
    
    for kw in keywords:
        pos = clean_lower.find(kw)
        while pos != -1:
            snippet = clean_text[pos:pos+250]
            codes = re.findall(r'\b\d{4}\b', snippet)
            valid_codes = [c for c in codes if c not in [str(y) for y in range(2020, 2031)]]
            if valid_codes:
                return valid_codes[0], clean_text
            pos = clean_lower.find(kw, pos + len(kw))

    # 4. Dự phòng: Bốc tất cả chuỗi 4 chữ số độc lập trong toàn bộ email, loại bỏ năm 2020-2030
    all_codes = re.findall(r'\b\d{4}\b', clean_text)
    valid_codes = [c for c in all_codes if c not in [str(y) for y in range(2020, 2031)]]
    if valid_codes:
        return valid_codes[0], clean_text

    return None, clean_text


def wait_for_otp(address, timestamp, key, timeout=60):
    """
    Lặp theo dõi hòm thư và trả về mã OTP 4 số từ email gửi tới
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            messages = read_inbox_by_key(address, timestamp, key)
            for msg in messages:
                print(f"\n🔍 [DEBUG MSG KEYS DÀNH CHO {address}]: {list(msg.keys())}")
                print(f"🔍 [DEBUG RAW MSG]: {json.dumps(msg, ensure_ascii=False)}")
                
                otp_code, clean_text = extract_otp_from_message(msg)
                sender = msg.get('textFrom', '') or msg.get('from', '')
                subj = msg.get('textSubject', '') or msg.get('subject', '')
                
                print(f"\n📩 [ĐÃ NHẬN THƯ MỚI DÀNH CHO {address}]")
                print(f"   • Người gửi : {sender}")
                print(f"   • Tiêu đề   : {subj}")
                print(f"   • Nội dung  : {clean_text[:150]}...")
                print(f"   ➔ Mã OTP trích xuất: {otp_code}\n")

                if otp_code:
                    return otp_code
        except Exception as e:
            print(f"Lỗi đọc mail {address}: {e}")
        time.sleep(3)
    return None


# if __name__ == "__main__":
#     email_data = create_email()
#     print("Email khởi tạo:", email_data)
