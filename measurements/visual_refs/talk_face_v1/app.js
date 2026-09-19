const logEl = document.getElementById('log');
const input = document.getElementById('input');
const form = document.getElementById('composer');
const pendingBox = document.getElementById('pendingBox');
const confirmBtn = document.getElementById('confirmBtn');
const liveDot = document.getElementById('liveDot');
const liveLabel = document.getElementById('liveLabel');
const flagsBadge = document.getElementById('flagsBadge');
const openForgeBtn = document.getElementById('openForgeBtn');
const clearChatBtn = document.getElementById('clearChatBtn');

function addBubble(role, text) {
  const row = document.createElement('div');
  row.className = 'msg ' + role;
  const av = document.createElement('div');
  av.className = 'avatar ' + (role === 'user' ? 'user' : 'ai');
  av.textContent = role === 'user' ? 'You' : 'A';
  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.textContent = text || '';
  row.appendChild(av);
  row.appendChild(bubble);
  logEl.appendChild(row);
  logEl.scrollTop = logEl.scrollHeight;
}

async function api(path, opts) {
  const res = await fetch(path, Object.assign({
    headers: { 'Content-Type': 'application/json', ...((opts && opts.headers) || {}) },
  }, opts || {}));
  const data = await res.json();
  if (!res.ok || data.ok === false) {
    throw new Error((data && (data.error || data.text)) || ('HTTP ' + res.status));
  }
  return data;
}

async function refresh() {
  try {
    const st = await api('/api/status');
    liveDot.classList.remove('off');
    liveLabel.textContent = 'Live';
    const flags = (st.data && st.data.flags) || st.flags || {};
    flagsBadge.textContent =
      'plant_chat ' + (flags.plant_chat || 'BLOCKED') +
      ' · kit_act ' + String(flags.kit_act ?? false);
    const pend = await api('/api/pending');
    const p = (pend.data || {});
    const brief = pend.brief || p.brief || '';
    if (p.path && !p.applied) {
      pendingBox.classList.add('armed');
      pendingBox.textContent =
        (brief ? brief + '\n\n' : '') +
        'Staged: ' + (p.path || '') +
        '\nConfirm write uses plant spine (fail-closed).';
      confirmBtn.disabled = false;
    } else {
      pendingBox.classList.remove('armed');
      pendingBox.textContent = brief || 'No staged write.';
      confirmBtn.disabled = true;
    }
  } catch (e) {
    liveDot.classList.add('off');
    liveLabel.textContent = 'Offline';
    pendingBox.textContent = String(e.message || e);
  }
}

form.addEventListener('submit', async (ev) => {
  ev.preventDefault();
  const msg = (input.value || '').trim();
  if (!msg) return;
  input.value = '';
  input.style.height = 'auto';
  addBubble('user', msg);
  try {
    const r = await api('/api/turn', { method: 'POST', body: JSON.stringify({ message: msg }) });
    addBubble('assistant', r.text || (r.data && r.data.text) || '(empty)');
    await refresh();
  } catch (e) {
    addBubble('assistant', 'Error: ' + (e.message || e));
  }
});

input.addEventListener('keydown', (ev) => {
  if (ev.key === 'Enter' && !ev.shiftKey) {
    ev.preventDefault();
    form.requestSubmit();
  }
});
input.addEventListener('input', () => {
  input.style.height = 'auto';
  input.style.height = Math.min(input.scrollHeight, 120) + 'px';
});

document.getElementById('refreshBtn').addEventListener('click', refresh);

confirmBtn.addEventListener('click', async () => {
  confirmBtn.disabled = true;
  try {
    const r = await api('/api/apply', { method: 'POST', body: JSON.stringify({ confirm: true }) });
    addBubble('assistant', r.text || 'Confirm result received.');
  } catch (e) {
    addBubble('assistant', 'Confirm failed (fail-closed): ' + (e.message || e));
  }
  await refresh();
});

openForgeBtn.addEventListener('click', async () => {
  openForgeBtn.disabled = true;
  try {
    const r = await api('/api/open_forge', { method: 'POST', body: JSON.stringify({}) });
    addBubble('assistant', r.text || 'Forge terminal launching in a new window.');
  } catch (e) {
    addBubble('assistant', 'Could not open Forge: ' + (e.message || e));
  }
  openForgeBtn.disabled = false;
});

clearChatBtn.addEventListener('click', () => {
  logEl.innerHTML = '';
  addBubble('assistant', 'Chat cleared. Menu stays — Open Forge still works.');
});

document.getElementById('copyBtn').addEventListener('click', async () => {
  const text = Array.from(logEl.querySelectorAll('.bubble')).map((b) => b.textContent).join('\n\n');
  try {
    await navigator.clipboard.writeText(text || '');
    addBubble('assistant', 'Conversation copied.');
  } catch (e) {
    addBubble('assistant', 'Copy failed: ' + (e.message || e));
  }
});

document.getElementById('quitHintBtn').addEventListener('click', () => {
  addBubble('assistant', 'Close this browser tab when you are done. The host console can keep running; run the desktop shortcut again to reopen this face.');
});

document.getElementById('tabLive').addEventListener('click', () => {});

addBubble(
  'assistant',
  'Ready. Ask me anything — plans, code, a webpage, or help with this PC.\nUse Open Forge when you want the industrial terminal. Confirm write stays fail-closed on the plant spine.'
);
refresh();
