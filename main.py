import requests
import json
import uuid
import hashlib
import time
from twocaptcha import TwoCaptcha

PAGE_URL = "https://www.roboneo.com/"

def register_meitu_step_request_captcha(email, password):
    """
    Khởi tạo Session & gửi yêu cầu lấy captcha_app_id từ Meitu API.
    Trả về (session, base_params, captcha_app_id, register_token)
    """
    sid = hashlib.md5(f"sid-{uuid.uuid4().hex}-{time.time()}".encode()).hexdigest()
    unlogin_token = hashlib.md5(f"utoken-{uuid.uuid4().hex}-{time.time()}".encode()).hexdigest()
    mt_g = hashlib.md5(f"mtg-{uuid.uuid4().hex}-{time.time()}".encode()).hexdigest()

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36",
        "Origin": "https://www.roboneo.com",
        "Referer": "https://www.roboneo.com/",
        "Content-Type": "application/x-www-form-urlencoded",
        "Unlogin-Token": unlogin_token,
        "Access-Token": "",
    })

    base_params = {
        'client_id': '1189857647',
        'client_language': 'vi',
        'mt_g': mt_g,
        'overseas': '1',
        'client_type': '2',
        'web_version': '4.9.0',
        'zip_version': '4.76000',
        'is_web': '1',
        'sid': sid,
        'client_accept_cookies': '1',
        'country_code': 'VN',
    }

    # Step 0: Lấy register_token qua /oauth/access_token
    data_oauth = base_params.copy()
    data_oauth.update({
        'email': email,
        'password': password,
        'is_register': '1',
        'grant_type': 'email'
    })
    
    try:
        r_oauth = session.post('https://account.meitu.com/oauth/access_token', data=data_oauth, timeout=15)
        resp_oauth = r_oauth.json()
        register_token = resp_oauth.get('response', {}).get('register_token')
        if r_oauth.headers.get('Unlogin-Token'):
            session.headers.update({"Unlogin-Token": r_oauth.headers.get('Unlogin-Token')})
    except Exception:
        register_token = None

    if not register_token:
        register_token = uuid.uuid4().hex

    # Step 1: Gửi yêu cầu captcha
    data_step1 = base_params.copy()
    data_step1.update({'type': 'register', 'email': email})
    
    r1 = session.post('https://api.account.meitu.com/common/send_email_verify_code', data=data_step1, timeout=15)
    resp1 = r1.json()
    
    captcha_info = resp1.get('response', {}).get('captcha_data', {})
    app_id = captcha_info.get('captcha_app_id', '198067043')

    return session, base_params, app_id, register_token


def solve_tencent_captcha(app_id, captcha_key):
    """
    Giải Tencent Captcha thông qua 2Captcha API.
    Trả về (ticket, randstr)
    """
    solver = TwoCaptcha(captcha_key)
    result = solver.tencent(app_id=app_id, url=PAGE_URL)
    code_raw = result.get('code', '')
    if isinstance(code_raw, str) and code_raw.startswith('{'):
        captcha_obj = json.loads(code_raw)
    else:
        captcha_obj = {'ticket': code_raw, 'randstr': result.get('randstr', '')}

    return captcha_obj.get('ticket', ''), captcha_obj.get('randstr', '')


def register_meitu_step_send_otp(session, base_params, email, ticket, randstr):
    """
    Kích hoạt gửi mã OTP về email bằng tc_ticket & tc_randstr.
    """
    data_step3 = base_params.copy()
    data_step3.update({
        'type': 'register',
        'email': email,
        'tc_ticket': ticket,
        'tc_randstr': randstr
    })
    r3 = session.post('https://api.account.meitu.com/common/send_email_verify_code', data=data_step3, timeout=15)
    return r3.json()


def register_meitu_step_create_account(session, base_params, email, password, otp_code, register_token):
    """
    Gửi yêu cầu đăng ký tạo tài khoản (/account/create).
    """
    data_create = base_params.copy()
    data_create.update({
        'email': email,
        'password': password,
        'verify_code': otp_code,
        'register_token': register_token,
    })
    r_create = session.post('https://api.account.meitu.com/account/create', data=data_create, timeout=15)
    return r_create.json()