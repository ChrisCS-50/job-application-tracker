from app import app, db
with app.test_client() as c:
  r=c.post('/login', data={'username':'admin', 'password':'password123'})
  print('Login Status:', r.status_code)
  if r.status_code == 500: print(r.text)
  r2=c.get('/')
  print('Dashboard Status:', r2.status_code)
  if r2.status_code == 500: print(r2.text)
