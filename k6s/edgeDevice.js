import http from 'k6/http';
import { sleep, check } from 'k6';
import { Counter } from 'k6/metrics';

export const requests = new Counter('http_reqs');

export const options = {
  stages: [
    { target: 2, duration: '30s' },
    { target: 2, duration: '1m' },
    { target: 5, duration: '10s' },
    { target: 2, duration: '10s' },
    { target: 2, duration: '1m' },
    { target: 3, duration: '10s' },
    { target: 3, duration: '20s' },
    { target: 1, duration: '10' },
    { target: 1, duration: '1m' },
    { target: 0, duration: '1m' },
  ]
};

export default function () {
  const url = 'http://localhost:8080/function/director';
  const payload = JSON.stringify({
    data: "1451624436,asd,0.003483333,,3.33E-05,0.0207,0.061916667,0.442633333,0.12415,0.006983333,0.013083333,0.000416667,0.00015,0,0.03135,0.001016667,0.004066667,0.001516667,0.003483333,36.14,clear-night,0.62,10,Clear,29.26,1016.91,9.18,cloudCover,282,0,24.4,0",
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  http.post(url, payload, params);

  sleep(3);
}