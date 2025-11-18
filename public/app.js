const API_BASE = '';

function show(id){
  document.querySelectorAll('#login-panel, #dashboard, #tokens, #send, #broadcast, #logs').forEach(el=>el.classList.add('hidden'));
  document.getElementById('responsePre').innerText = 'No response yet';
  if (id === 'dashboard') loadStats();
  if (id === 'tokens') loadTokens();
  if (id === 'logs') loadLogs();
  document.getElementById(id).classList.remove('hidden');
}

function setAuthUI(email){
  document.getElementById('login-panel').classList.add('hidden');
  document.getElementById('user-info').classList.remove('hidden');
  document.getElementById('admin-email').innerText = email;
  document.getElementById('logoutBtn').onclick = () => { localStorage.removeItem('admin_token'); location.reload(); };
}

async function login(){
  const email = document.getElementById('loginEmail').value;
  const password = document.getElementById('loginPassword').value;
  const res = await fetch(API_BASE + '/api/admin/login', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({email,password}) });
  const j = await res.json();
  if (j.success && j.token) {
    localStorage.setItem('admin_token', j.token);
    setAuthUI(email);
    show('dashboard');
  } else {
    alert('Login failed: ' + (j.error || JSON.stringify(j)));
  }
}

document.getElementById('loginBtn').addEventListener('click', login);

// attach auth header helper
function authHeaders(){
  const t = localStorage.getItem('admin_token');
  if (t) return { 'Authorization': 'Bearer ' + t, 'Content-Type': 'application/json' };
  return { 'Content-Type': 'application/json' };
}

async function loadStats(){
  const tkns = await fetch('/tokens', { headers: authHeaders() }).then(r=>r.json()).catch(()=>({success:false}));
  document.getElementById('statTokens').innerText = (tkns.tokens && tkns.tokens.length) ? tkns.tokens.length : 0;
  document.getElementById('statBroadcast').innerText = '-';
  document.getElementById('statActivity').innerText = '-';
}

async function loadTokens(){
  const res = await fetch('/tokens', { headers: authHeaders() });
  const j = await res.json();
  document.getElementById('responsePre').innerText = JSON.stringify(j, null, 2);
  const tbody = document.getElementById('tokensTable');
  tbody.innerHTML = '';
  if (j.tokens) j.tokens.forEach(t=>{
    const tr = document.createElement('tr');
    tr.className = 'border-b border-gray-700';
    tr.innerHTML = `<td class="py-2">${t.userId}</td><td class="py-2 text-xs">${t.token}</td><td class="py-2">${t.platform||'-'}</td><td class="py-2">${t.created_at}</td><td class="py-2"><button class="px-2 py-1 bg-red-600 rounded" onclick="deleteToken('${t.token}')">Delete</button></td>`;
    tbody.appendChild(tr);
  });
}

async function deleteToken(token){
  if (!confirm('Delete token?')) return;
  const res = await fetch('/unregister', { method:'POST', headers: authHeaders(), body: JSON.stringify({ token }) });
  const j = await res.json();
  document.getElementById('responsePre').innerText = JSON.stringify(j,null,2);
  loadTokens();
}

async function quickSend(){
  const userId = document.getElementById('quickUser').value;
  const token = document.getElementById('quickToken').value;
  const title = document.getElementById('quickTitle').value;
  const body = document.getElementById('quickBody').value;
  const res = await fetch('/send', { method:'POST', headers: authHeaders(), body: JSON.stringify({ userId, token, title, body }) });
  const j = await res.json();
  document.getElementById('responsePre').innerText = JSON.stringify(j,null,2);
}

async function sendNotification(){
  const userId = document.getElementById('sendUser').value;
  const token = document.getElementById('sendToken').value;
  const title = document.getElementById('sendTitle').value;
  const body = document.getElementById('sendBody').value;
  const res = await fetch('/send', { method:'POST', headers: authHeaders(), body: JSON.stringify({ userId, token, title, body }) });
  const j = await res.json();
  document.getElementById('responsePre').innerText = JSON.stringify(j,null,2);
}

async function broadcast(){
  const title = document.getElementById('bTitle').value;
  const body = document.getElementById('bBody').value;
  const res = await fetch('/broadcast', { method:'POST', headers: authHeaders(), body: JSON.stringify({ title, body }) });
  const j = await res.json();
  document.getElementById('responsePre').innerText = JSON.stringify(j,null,2);
}

async function loadLogs(){
  const res = await fetch('/logs', { headers: authHeaders() });
  const j = await res.json();
  document.getElementById('logsPre').innerText = JSON.stringify(j,null,2);
}

// on load check token
(function(){
  const t = localStorage.getItem('admin_token');
  if (t) {
    try {
      const p = JSON.parse(atob(t.split('.')[1]));
      setAuthUI(p.sub || p.email || 'admin');
      show('dashboard');
    } catch(e) {
      localStorage.removeItem('admin_token');
      document.getElementById('login-panel').classList.remove('hidden');
    }
  } else {
    document.getElementById('login-panel').classList.remove('hidden');
  }
})();
