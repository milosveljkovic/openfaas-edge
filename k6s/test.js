import http from 'k6/http';

export const options = {
  discardResponseBodies: true,
  scenarios: {
    edgeDevice1: {
      executor: 'constant-vus',
      exec: 'contacts',
      vus: 50,
      duration: '30s',
    },
    edgeDevice2: {
      executor: 'per-vu-iterations',
      exec: 'news',
      vus: 50,
      iterations: 100,
      startTime: '30s',
      maxDuration: '1m',
    },
  },
};

export function edgeDevice1() {
  http.get('http://localhost:8080/function/processing', {
    tags: { my_custom_tag: 'contacts' },
  });
}

export function edgeDevice2() {
  http.get('http://localhost:8080/function/processing1', {
    tags: { my_custom_tag: 'contacts' },
  });
}

export function edgeDevice3() {
  http.get('http://localhost:8080/function/processing2', {
    tags: { my_custom_tag: 'contacts' },
  });
}