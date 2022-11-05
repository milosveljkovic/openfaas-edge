import requests
import logging

logging.basicConfig(level=logging.DEBUG)


def handle(req):
  """handle a request to the function
  Args:
      req (str): request body
  """
  logging.debug("Director called with:", req)
  processing_res = requests.post("http://gateway.openfaas:8080/function/processing", req)
  logging.debug("Response from processing:", processing_res)
  logging.debug("Content from processing:", processing_res.content)
  storing_res = requests.post("http://gateway.openfaas:8080/function/storing", processing_res.content)
  logging.debug("Response from storing:", storing_res)

  return storing_res.status_code