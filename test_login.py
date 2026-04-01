import urllib.request, urllib.parse; req = urllib.request.Request('http://127.0.0.1:5000/login', data=urllib.parse.urlencode({'username':'admin', 'password':'password123'}).encode()); 

try: urllib.request.urlopen(req)
except Exception as e: print(e.read().decode())
