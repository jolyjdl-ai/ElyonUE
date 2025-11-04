import json,urllib.request,traceback,sys
long = 'Réalise une synthèse complète : ' + ('x' * 700)
body = json.dumps({'input': long, 'mode': 'normal'}).encode('utf-8')
req = urllib.request.Request('http://127.0.0.1:8000/gen/generate', data=body, headers={'Content-Type':'application/json'})
try:
    resp = urllib.request.urlopen(req, timeout=20)
    print(resp.read().decode('utf-8'))
except Exception as e:
    print('ERROR', e)
    traceback.print_exc()
    sys.exit(1)
