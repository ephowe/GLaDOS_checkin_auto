import requests, json, os


def safe_json(response):
    try:
        return response.json()
    except ValueError:
        return None


if __name__ == '__main__':
    # pushplus秘钥 申请地址 http://www.pushplus.plus
    sckey = os.environ.get("PUSHPLUS_TOKEN", "")
    # 推送内容
    sendContent = ''
    # glados账号cookie 直接使用数组 如果使用环境变量需要字符串分割一下
    cookies = [c.strip() for c in os.environ.get("GLADOS_COOKIE", "").split("&") if c.strip()]
    if not cookies:
        print('未获取到COOKIE变量')
        exit(0)

    url = "https://glados.rocks/api/user/checkin"
    url2 = "https://glados.rocks/api/user/status"
    referer = 'https://glados.rocks/console/checkin'
    origin = "https://glados.rocks"
    useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
    payload = {
        'token': 'glados.one'
    }

    for cookie in cookies:
        try:
            checkin = requests.post(
                url,
                headers={'cookie': cookie, 'referer': referer, 'origin': origin, 'user-agent': useragent, 'content-type': 'application/json;charset=UTF-8'},
                data=json.dumps(payload),
                timeout=30
            )
            state = requests.get(
                url2,
                headers={'cookie': cookie, 'referer': referer, 'origin': origin, 'user-agent': useragent},
                timeout=30
            )
        except requests.RequestException as exc:
            print(f"请求异常: {exc}")
            continue

        state_json = safe_json(state)
        if not state_json or 'data' not in state_json:
            print(f"状态接口返回异常，响应内容：{state.text[:500]}")
            continue

        data = state_json.get('data', {})
        left_days = str(data.get('leftDays', '0')).split('.')[0]
        email = data.get('email', 'unknown')

        checkin_json = safe_json(checkin)
        if isinstance(checkin_json, dict) and 'message' in checkin_json:
            mess = checkin_json['message']
            print(email + '----结果--' + mess + '----剩余(' + left_days + ')天')
            sendContent += email + '----' + mess + '----剩余(' + left_days + ')天\n'
        elif 'message' in checkin.text:
            mess = checkin_json.get('message', '签到失败') if isinstance(checkin_json, dict) else '签到失败'
            print(email + '----结果--' + mess + '----剩余(' + left_days + ')天')
            sendContent += email + '----' + mess + '----剩余(' + left_days + ')天\n'
        else:
            if sckey:
                requests.get('http://www.pushplus.plus/send?token=' + sckey + '&content=' + email + 'cookie已失效', timeout=30)
            print('cookie已失效')

    if sckey and sendContent:
        requests.get('http://www.pushplus.plus/send?token=' + sckey + '&title=签到结果' + '&content=' + sendContent, timeout=30)
