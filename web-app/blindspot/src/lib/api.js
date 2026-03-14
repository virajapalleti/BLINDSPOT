const PI_URL = 'http://YOUR_PI_IP:5000'; // update this when Pi is ready

export async function checkConnection() {
  try {
    const res = await fetch(PI_URL + '/status', {
      signal: AbortSignal.timeout(3000)
    });
    return res.ok;
  } catch {
    return false;
  }
}

export async function applyPattern(objectName, pattern) {
  const res = await fetch(PI_URL + '/apply', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ object: objectName, pattern }),
    signal: AbortSignal.timeout(3000)
  });
  return res.ok;
}

export async function pushRange(value) {
  const res = await fetch(PI_URL + '/range', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ range: value }),
    signal: AbortSignal.timeout(3000)
  });
  return res.ok;
}