from pydantic import BaseModel
from datetime import datetime
import json
import logging

def removeNaNs(sd):
  for i,x in enumerate(sd):
    if not isfloat(sd[i]):
      sd[i] = '-1'
  return sd

def isfloat(num):
  try:
    float(num)
    return True
  except ValueError:
    return False

def formatAll(sd):
  for i,x in enumerate(sd):
    if i>0 and i<10:
      x=float(sd[i])
      sd[i] = format(x,'.8f')
  return sd

class Sensor(BaseModel):
    time: str
    use: float
    gen: float
    dw: float         # dishwasher
    fu: float         # furance
    fu2: float
    ho: float         # home office
    fridge: float
    wc: float         # wine cellar

def handle(dict):
    """ Processing function
    Args:
      dict (str): {"data":"1451624436,asd,0.003483333,,3.33E-05,0.0207,0.061916667,0.442633333,0.12415,0.006983333,0.013083333,0.000416667,0.00015,0,0.03135,0.001016667,0.004066667,0.001516667,0.003483333,36.14,clear-night,0.62,10,Clear,29.26,1016.91,9.18,cloudCover,282,0,24.4,0"}
    Curl for testing:
      curl 127.0.0.1:8080/function/processing --data-binary '{"data":"1451624436,asd,0.003483333,,3.33E-05,0.0207,0.061916667,0.442633333,0.12415,0.006983333,0.013083333,0.000416667,0.00015,0,0.03135,0.001016667,0.004066667,0.001516667,0.003483333,36.14,clear-night,0.62,10,Clear,29.26,1016.91,9.18,cloudCover,282,0,24.4,0"}'
    Response:
      {'time': '2016-01-01 05:00:36', 'use': -1.0, 'gen': 0.00348333, 'dw': 3.33e-05, 'fu': 0.0207, 'fu2': 0.06191667, 'ho': 0.44263333, 'fridge': 0.12415, 'wc': 0.00698333}
    """
    json_req = json.loads(dict)
    if 'data' in json_req:
        sd = json_req['data']
    else:
        sd = ",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,"
    # only for testing locally
    # f = open("HomeC_short.csv", "r")
    # sd: str = f.readline().split(",")
    sd: str = sd.split(",")
    sd = removeNaNs(sd)
    sd = formatAll(sd)
    sensor = Sensor (
      time=datetime.utcfromtimestamp(int(sd[0])).strftime('%Y-%m-%d %H:%M:%S'),
      use= sd[1],
      gen= sd[2],
      dw= sd[4],
      fu= sd[5],
      fu2= sd[6],
      ho= sd[7],
      fridge= sd[8],
      wc= sd[9]
    )

    return json.dumps(sensor.dict())

# handle({"data": "1451624416,,0.003483333,,3.33E-05,0.0207,0.061916667,0.442633333,0.12415,0.006983333,0.013083333,0.000416667,0.00015,0,0.03135,0.001016667,0.004066667,0.001516667,0.003483333,36.14,clear-night,0.62,10,Clear,29.26,1016.91,9.18,cloudCover,282,0,24.4,0"})
