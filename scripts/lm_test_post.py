import json,urllib.request,traceback,sys
url = 'http://10.10.5.207:1234/v1/chat/completions'
payload = {"model":"mistral-7b-instruct-v0.1","messages":[{"role":"user","content":"ping"}],"max_tokens":10}
req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type':'application/json'})
try:
    resp = urllib.request.urlopen(req, timeout=10)
    print('STATUS', resp.status)
    print(resp.read().decode('utf-8'))
except Exception as e:
    print('ERROR', e)
    traceback.print_exc()
    sys.exit(1)
