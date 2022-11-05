
import psycopg2
import json 
import logging

logging.basicConfig(level=logging.DEBUG)

def connectToDb():
  print("Connecting to db")
  conn=psycopg2.connect("host=faas-edge-db-postgresql.default port=5432 dbname=postgres user=postgres password=BVHz1M9Fd1")
  cur=conn.cursor()
  return cur, conn

def disconnect(cur):
  print("Disconnect from db")
  cur.close()

def handle(req):
  """ Processing function
  Curl for testing:
    curl 127.0.0.1:8080/function/storing --data-binary  '{"time": "2016-01-01 05:00:36", "use": -1.0, "gen": 0.00348333, "dw": 3.33e-05, "fu": 0.0207, "fu2": 0.06191667, "ho": 0.44263333, "fridge": 0.12415, "wc": 0.00698333}'
  Response:
    {"msg":"Successfully stored iot data"}
  """
  json_req = json.loads(req)
  logging.debug("Storing called with:", json_req)
  try:
    cur,conn = connectToDb()
    cur.execute('INSERT INTO public.smart_home(time, use, gen, dw, fu, fu2, ho, fridge, wc) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',(json_req['time'],json_req['use'],json_req['gen'],json_req['dw'],json_req['fu'],json_req['fu2'],json_req['ho'],json_req['fridge'],json_req['wc']))
    conn.commit()
  except:
    print("Something went wrong")
    return {"msg":"Something went wrong"}
# finally:
#     return {"msg":"Finally"}
#     disconnect(cur)
  return {"msg":"Successfully stored iot data"}