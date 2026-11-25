(() => {
'use strict';

/* ---------------- helpers ---------------- */
const $  = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[c]));
const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
const tierOf = s => (s >= 80 ? 'strong' : s >= 50 ? 'mid' : 'low');
const TIER_LABEL = { strong: 'Strong match', mid: 'Moderate match', low: 'Low match' };
const fmt = n => (Math.round(n * 10) / 10).toFixed(1);
const splitSkills = s => String(s || '').split(',').map(x => x.trim()).filter(Boolean);
const initials = n => String(n || '?').trim().split(/\s+/).slice(0, 2).map(w => w[0]).join('').toUpperCase() || '?';
const fmtSize = b => b < 1024 ? b + ' B' : b < 1048576 ? Math.round(b / 1024) + ' KB' : (b / 1048576).toFixed(1) + ' MB';
const ico = (n, c = '') => `<svg class="ico ${c}" aria-hidden="true"><use href="#i-${n}"/></svg>`;

/* ---------------- icon sprite ---------------- */
const ICONS = {
  doc: '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M16 13H8"/><path d="M16 17H8"/><path d="M10 9H8"/>',
  briefcase: '<rect width="20" height="14" x="2" y="7" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>',
  x: '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
  check: '<path d="M20 6 9 17l-5-5"/>',
  sparkles: '<path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3z"/>',
  chart: '<path d="M3 3v18h18"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/>',
  chat: '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
  send: '<path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/>',
  'arrow-left': '<path d="m12 19-7-7 7-7"/><path d="M19 12H5"/>',
  'arrow-right': '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
  menu: '<path d="M4 6h16"/><path d="M4 12h16"/><path d="M4 18h16"/>',
  trash: '<path d="M3 6h18"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>',
  search: '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>'
};
document.body.insertAdjacentHTML('afterbegin',
  '<svg xmlns="http://www.w3.org/2000/svg" style="display:none" aria-hidden="true">' +
  Object.entries(ICONS).map(([k, v]) => `<symbol id="i-${k}" viewBox="0 0 24 24">${v}</symbol>`).join('') +
  '</svg>');

/* ---------------- data ---------------- */
async function loadCandidates() {
  const r = await fetch('/candidates');
  if (!r.ok) throw new Error('candidates request failed');
  const d = await r.json();
  return (d.candidates || []).map(([id, name, email, phone, skills, score]) => ({
    id, name: name || 'Unnamed candidate', email: email || '', phone: phone || '',
    skills: splitSkills(skills), score: Number(score) || 0
  }));
}
const emptyState = (title, text, withBtn = true) =>
  `<div class="panel empty"><h3>${esc(title)}</h3><p>${esc(text)}</p>` +
  (withBtn ? '<a class="btn btn-primary" href="/#screening">Analyze Candidates</a>' : '') + '</div>';

function countTo(el, to, dec = 0, suffix = '') {
  const t = Number(to) || 0;
  if (reduceMotion || t === 0) { el.textContent = t.toFixed(dec) + suffix; return; }
  const dur = 900, start = performance.now();
  const step = now => {
    const p = Math.min((now - start) / dur, 1), e = 1 - Math.pow(1 - p, 3);
    el.textContent = (t * e).toFixed(dec) + suffix;
    if (p < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

/* ---------------- navigation ---------------- */
const nav = $('.nav'), toggle = $('.nav-toggle');
const setActive = key => $$('.nav-links a').forEach(a => a.classList.toggle('active', a.dataset.nav === key));
toggle.addEventListener('click', () => toggle.setAttribute('aria-expanded', nav.classList.toggle('open')));
$$('.nav-links a').forEach(a => a.addEventListener('click', () => {
  nav.classList.remove('open'); toggle.setAttribute('aria-expanded', 'false');
}));

/* =====================================================
   HOME
   ===================================================== */
function initHome() {
  const VIEWS = ['dashboard', 'screening', 'assistant'];
  function route() {
    const h = location.hash.slice(1);
    const v = VIEWS.includes(h) ? h : 'dashboard';
    VIEWS.forEach(n => { $('#view-' + n).hidden = n !== v; });
    setActive(v);
    window.scrollTo({ top: 0 });
  }
  addEventListener('hashchange', route);
  route();

  setupScreening();
  setupChat();
  loadDashboard();
}

/* ---------- dashboard ---------- */
async function loadDashboard() {
  const dot = $('#status .dot'), txt = $('#status-text');
  let list;
  try {
    list = await loadCandidates();
    dot.className = 'dot ok'; txt.textContent = 'AI screening server online';
  } catch {
    dot.className = 'dot bad'; txt.textContent = 'Server unreachable';
    $('#dist').innerHTML = '<p class="muted" style="margin-top:20px">Could not load candidate data.</p>';
    $('#top-list').innerHTML = '<p class="muted">Could not load candidate data.</p>';
    return;
  }
  const n = list.length;
  const sorted = [...list].sort((a, b) => b.score - a.score);
  countTo($('#s-total'), n);
  if (n) {
    countTo($('#s-avg'), list.reduce((a, c) => a + c.score, 0) / n, 1, '%');
    countTo($('#s-strong'), list.filter(c => c.score >= 80).length);
    countTo($('#s-top'), sorted[0].score, 1, '%');
    $('#f-top').textContent = sorted[0].name;
  } else {
    $('#s-avg').textContent = '—'; $('#s-top').textContent = '—';
    countTo($('#s-strong'), 0);
  }

  const counts = { strong: 0, mid: 0, low: 0 };
  list.forEach(c => counts[tierOf(c.score)]++);
  $('#dist').innerHTML = n
    ? `<div class="seg" role="img" aria-label="Distribution of match levels">
         ${['strong','mid','low'].filter(k => counts[k]).map(k => `<i class="s-${k}" style="width:${counts[k] / n * 100}%"></i>`).join('')}
       </div>
       <div class="legend">
         <div><b>${counts.strong}</b><span style="--c:var(--ok)">Strong</span></div>
         <div><b>${counts.mid}</b><span style="--c:var(--warn)">Moderate</span></div>
         <div><b>${counts.low}</b><span style="--c:var(--bad)">Low</span></div>
       </div>`
    : '<p class="muted" style="margin-top:20px">No candidates screened yet.</p>';

  $('#top-list').innerHTML = n
    ? sorted.slice(0, 3).map((c, i) => `
        <a class="mini tone-${tierOf(c.score)}" href="/candidate/${c.id}">
          <span class="mini-rank">0${i + 1}</span>
          <span><span class="mini-name">${esc(c.name)}</span><div class="bar"><i style="width:${c.score}%"></i></div></span>
          <span class="mini-score">${fmt(c.score)}%</span>
        </a>`).join('') +
      '<a class="card-link" href="/leaderboard">Full leaderboard ' + ico('arrow-right') + '</a>'
    : '<p class="muted">Upload resumes to see rankings here.</p>';
}

/* ---------- screening ---------- */
function setupScreening() {
  const form = $('#screen-form'), btn = $('#analyze'), summary = $('#summary');
  const rIn = $('#resume-input'), jIn = $('#job-input');
  const rList = $('#resume-list'), jList = $('#job-list');
  const rMsg = $('#resume-msg'), jMsg = $('#job-msg');
  let resumes = [], job = null;

  const isPdf = f => (f.type ? f.type === 'application/pdf' : /\.pdf$/i.test(f.name));
  const sync = (input, files) => {
    try { const dt = new DataTransfer(); files.forEach(f => dt.items.add(f)); input.files = dt.files; } catch {}
  };
  const timers = {};
  const say = (el, text) => {
    el.textContent = text; clearTimeout(timers[el.id]);
    if (text) timers[el.id] = setTimeout(() => { el.textContent = ''; }, 5000);
  };

  function fileLi(f, remove) {
    const li = document.createElement('li');
    li.className = 'file';
    li.innerHTML = `<span class="file-ico" aria-hidden="true">PDF</span>
      <div class="file-meta"><span class="file-name" title="${esc(f.name)}">${esc(f.name)}</span><span class="file-size">${fmtSize(f.size)} · ready</span></div>
      <span class="file-ok" aria-hidden="true">${ico('check')}</span>
      <button type="button" class="icon-btn" aria-label="Remove ${esc(f.name)}">${ico('x')}</button>`;
    $('button', li).addEventListener('click', remove);
    return li;
  }
  function paint() {
    rList.replaceChildren(...resumes.map((f, i) => fileLi(f, () => { resumes.splice(i, 1); sync(rIn, resumes); paint(); })));
    jList.replaceChildren(...(job ? [fileLi(job, () => { job = null; sync(jIn, []); paint(); })] : []));
    const ready = resumes.length > 0 && !!job;
    btn.disabled = !ready;
    summary.textContent = ready
      ? `${resumes.length} resume${resumes.length > 1 ? 's' : ''} and 1 job description ready to analyze.`
      : !resumes.length && !job ? 'Add at least one resume and a job description to begin.'
      : !resumes.length ? 'Add at least one resume to continue.' : 'Add a job description to continue.';
  }
  function addResumes(list) {
    const incoming = [...list]; let bad = 0;
    incoming.forEach(f => {
      if (!isPdf(f)) { bad++; return; }
      if (!resumes.some(r => r.name === f.name && r.size === f.size)) resumes.push(f);
    });
    say(rMsg, bad ? `${bad} file${bad > 1 ? 's were' : ' was'} skipped — only PDF files are supported.` : '');
    sync(rIn, resumes); paint();
  }
  function setJob(list) {
    const f = [...list][0];
    if (!f) return;
    if (!isPdf(f)) { say(jMsg, 'The job description must be a PDF file.'); sync(jIn, job ? [job] : []); return; }
    job = f; say(jMsg, ''); sync(jIn, [job]); paint();
  }
  function wireDrop(el, handle) {
    ['dragenter', 'dragover'].forEach(t => el.addEventListener(t, e => { e.preventDefault(); el.classList.add('is-over'); }));
    ['dragleave', 'drop'].forEach(t => el.addEventListener(t, e => { e.preventDefault(); el.classList.remove('is-over'); }));
    el.addEventListener('drop', e => handle(e.dataTransfer.files));
  }
  wireDrop($('#drop-resumes'), addResumes);
  wireDrop($('#drop-job'), setJob);
  ['dragover', 'drop'].forEach(t => addEventListener(t, e => e.preventDefault()));
  rIn.addEventListener('change', () => addResumes(rIn.files));
  jIn.addEventListener('change', () => setJob(jIn.files));

  /* ---- processing modal ---- */
  const ov = $('#overlay'), modal = $('#modal'), bar = $('#ov-progress'), pct = $('#ov-pct');
  const err = $('#ov-error'), act = $('#ov-actions'), title = $('#ov-title'), sub = $('#ov-sub');
  const steps = $$('.steps li', ov);
  const setStep = n => steps.forEach((li, i) => { li.classList.toggle('done', i + 1 < n); li.classList.toggle('active', i + 1 === n); });
  const setBar = p => { bar.firstElementChild.style.width = p + '%'; };

  function openModal() {
    ov.hidden = false; err.hidden = true; act.hidden = true;
    bar.classList.remove('indet'); setBar(0); pct.textContent = '0%';
    title.textContent = 'Screening in progress';
    sub.textContent = 'Your files are being uploaded.';
    setStep(1); btn.classList.add('is-loading');
  }
  function closeModal() { ov.hidden = true; btn.classList.remove('is-loading'); btn.focus(); }
  function fail(msg) {
    setStep(0); bar.classList.remove('indet'); setBar(0);
    title.textContent = 'Something went wrong';
    sub.textContent = 'Nothing was lost — you can adjust your files and try again.';
    err.textContent = msg; err.hidden = false; act.hidden = false;
    $('#ov-close').focus();
  }
  $('#ov-close').addEventListener('click', closeModal);

  form.addEventListener('submit', e => {
    e.preventDefault();
    if (!resumes.length || !job) return;
    const fd = new FormData();
    resumes.forEach(f => fd.append('resumes', f));
    fd.append('job', job);
    openModal();

    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/upload');
    xhr.upload.onprogress = ev => {
      if (!ev.lengthComputable) return;
      const p = Math.round(ev.loaded / ev.total * 100);
      setBar(p); pct.textContent = p + '%';
    };
    xhr.upload.onload = () => {
      setBar(100); pct.textContent = '100%'; setStep(2); bar.classList.add('indet');
      sub.textContent = 'Upload complete. The AI is reading each resume and scoring it against the job description — larger batches take longer.';
    };
    xhr.onload = () => {
      if (xhr.responseURL && xhr.responseURL.includes('/leaderboard')) {
        bar.classList.remove('indet'); setBar(100); setStep(4);
        title.textContent = 'Screening complete';
        sub.textContent = 'Opening the leaderboard…';
        setTimeout(() => { location.href = '/leaderboard'; }, reduceMotion ? 0 : 900);
        return;
      }
      let msg = 'The server could not process these files.';
      if (xhr.status >= 500) msg = `Server error (${xhr.status}). Check the server terminal for details.`;
      try { const d = JSON.parse(xhr.responseText); if (d.error) msg = d.error; } catch {}
      fail(msg);
    };
    xhr.onerror = () => fail('Could not reach the server. Make sure it is running and try again.');
    xhr.send(fd);
  });
}

/* ---------- chat ---------- */
function setupChat() {
  const log = $('#chat-log'), box = $('#chat-message'), send = $('#chat-send'), chips = $('#chips');
  let busy = false;

  const fmtAnswer = t => esc(t).replace(/^\s*[*\-]\s+/gm, '• ').replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  function addMsg(role, text, cls = '') {
    const d = document.createElement('div');
    d.className = `msg ${role} ${cls}`;
    d.innerHTML = `<div class="avatar">${role === 'user' ? 'You' : 'AI'}</div><div class="bubble"></div>`;
    const b = $('.bubble', d);
    if (role === 'ai' && !cls) b.innerHTML = fmtAnswer(text); else b.textContent = text;
    log.appendChild(d); log.scrollTop = log.scrollHeight;
    return d;
  }
  const typing = () => {
    const d = document.createElement('div');
    d.className = 'msg ai';
    d.innerHTML = '<div class="avatar">AI</div><div class="bubble"><span class="typing" aria-label="Assistant is typing"><span></span><span></span><span></span></span></div>';
    log.appendChild(d); log.scrollTop = log.scrollHeight;
    return d;
  };
  const autosize = () => { box.style.height = 'auto'; box.style.height = Math.min(box.scrollHeight, 140) + 'px'; };

  async function ask(text) {
    text = text.trim();
    if (!text || busy) return;
    busy = true; send.disabled = true; chips.hidden = true;
    addMsg('user', text); box.value = ''; autosize();
    const t = typing();
    try {
      const r = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });
      const d = await r.json();
      t.remove();
      if (d.error || d.answer == null) {
        const m = d.error === 'Upload a resume first'
          ? 'No resume is loaded yet. Screen a resume first — the assistant answers from the most recently uploaded one.'
          : (d.error || 'The assistant returned an unexpected response.');
        addMsg('ai', m, 'err');
      } else {
        addMsg('ai', typeof d.answer === 'string' ? d.answer : JSON.stringify(d.answer));
      }
    } catch {
      t.remove();
      addMsg('ai', 'Unable to contact the assistant. Make sure the server is running.', 'err');
    } finally {
      busy = false; send.disabled = false; box.focus();
    }
  }

  addMsg('ai', 'Hi! Ask me anything about the most recently screened resume — skills, experience, projects or education.');
  $('#chat-form').addEventListener('submit', e => { e.preventDefault(); ask(box.value); });
  box.addEventListener('input', autosize);
  box.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); ask(box.value); }
  });
  $$('.chip-btn', chips).forEach(b => b.addEventListener('click', () => ask(b.textContent)));
}

/* =====================================================
   LEADERBOARD
   ===================================================== */
async function initBoard() {
  setActive('board');
  const board = $('#board'), toolbar = $('#toolbar'), foot = $('#foot'), count = $('#count');
  let all;
  try {
    all = (await loadCandidates()).sort((a, b) => b.score - a.score || a.id - b.id).map((c, i) => ({ ...c, rank: i + 1 }));
  } catch {
    board.innerHTML = emptyState('Could not load candidates', 'Check that the server is running and refresh the page.', false);
    return;
  }
  if (!all.length) {
    board.innerHTML = emptyState('No candidates yet', 'Screen some resumes and the ranking will appear here.');
    return;
  }
  toolbar.hidden = false; foot.hidden = false;

  const state = { q: '', tier: 'all', sort: 'score-desc' };
  const sorters = {
    'score-desc': (a, b) => b.score - a.score || a.id - b.id,
    'score-asc': (a, b) => a.score - b.score || a.id - b.id,
    name: (a, b) => a.name.localeCompare(b.name)
  };

  const rowHTML = (c, i) => {
    const t = tierOf(c.score), top = c.skills.slice(0, 6), rest = c.skills.length - top.length;
    return `<article class="panel cand tone-${t} reveal" style="--i:${Math.min(i, 8)}">
      <div class="cand-row">
        <div class="rank ${c.rank <= 3 ? 'top' : ''}">${String(c.rank).padStart(2, '0')}</div>
        <div class="who">
          <div class="avatar-c" aria-hidden="true">${esc(initials(c.name))}</div>
          <div class="who-t"><a class="name" href="/candidate/${c.id}">${esc(c.name)}</a><span class="sub">${esc(c.email || 'No email found')}</span></div>
        </div>
        <div class="score"><span class="score-n">${fmt(c.score)}%</span><div class="bar"><i style="width:${c.score}%"></i></div></div>
        <div class="status"><span class="badge">${TIER_LABEL[t]}</span></div>
        <div class="cand-actions">
          <button type="button" class="btn btn-secondary btn-sm" data-toggle aria-expanded="false">Details</button>
          <a class="btn btn-primary btn-sm" href="/candidate/${c.id}">View report</a>
        </div>
      </div>
      <div class="chips-row">${top.map(s => `<span class="chip">${esc(s)}</span>`).join('')}${rest > 0 ? `<span class="chip more">+${rest} more</span>` : ''}</div>
      <div class="collapse"><div><div class="more-inner">
        <div><h4>Contact</h4><span class="muted">${esc(c.email || '—')} · ${esc(c.phone || '—')}</span></div>
        <div><h4>All extracted skills (${c.skills.length})</h4><div class="chips-row" style="padding:0;margin:0">${c.skills.map(s => `<span class="chip">${esc(s)}</span>`).join('') || '<span class="muted">None found</span>'}</div></div>
      </div></div></div>
    </article>`;
  };

  function render() {
    const q = state.q.trim().toLowerCase();
    const rows = all
      .filter(c => (state.tier === 'all' || tierOf(c.score) === state.tier) &&
        (!q || c.name.toLowerCase().includes(q) || c.skills.some(s => s.toLowerCase().includes(q))))
      .sort(sorters[state.sort]);
    count.textContent = `${rows.length} of ${all.length} candidate${all.length > 1 ? 's' : ''}`;
    board.innerHTML = rows.length ? rows.map(rowHTML).join('') : emptyState('No matches', 'Try a different search or filter.', false);
  }
  render();

  $('#q').addEventListener('input', e => { state.q = e.target.value; render(); });
  $('#sort').addEventListener('change', e => { state.sort = e.target.value; render(); });
  $$('#tiers button').forEach(b => b.addEventListener('click', () => {
    state.tier = b.dataset.tier;
    $$('#tiers button').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
    render();
  }));
  board.addEventListener('click', e => {
    const b = e.target.closest('[data-toggle]');
    if (!b) return;
    const open = b.closest('.cand').classList.toggle('open');
    b.setAttribute('aria-expanded', String(open));
    b.textContent = open ? 'Hide' : 'Details';
  });
  $('#clear').addEventListener('click', () => {
    if (confirm('Delete all candidates?')) location.href = '/clear-database';
  });
}

/* =====================================================
   CANDIDATE REPORT
   ===================================================== */
async function initCandidate() {
  setActive('board');
  const root = $('#report');
  const id = location.pathname.split('/').filter(Boolean).pop();
  let c;
  try {
    const r = await fetch('/api/candidate/' + encodeURIComponent(id));
    if (r.status === 404) { root.innerHTML = emptyState('Candidate not found', 'This candidate may have been removed.', false); return; }
    if (!r.ok) throw new Error();
    c = await r.json();
  } catch {
    root.innerHTML = emptyState('Could not load report', 'Check that the server is running and try again.', false);
    return;
  }
  const t = tierOf(c.score);
  document.title = `${c.name} · AI Resume Screener`;
  const chips = (arr, cls, icon) => arr.length
    ? arr.map(s => `<span class="chip ${cls}">${ico(icon)}${esc(s)}</span>`).join('')
    : '<span class="muted">None</span>';

  root.innerHTML = `
    <section class="panel report-head tone-${t} reveal">
      <div class="avatar-xl" aria-hidden="true">${esc(initials(c.name))}</div>
      <div class="rh-main">
        <span class="badge">${TIER_LABEL[t]}</span>
        <h1 class="rh-name">${esc(c.name)}</h1>
        <dl class="kv">
          <div><dt>Email</dt><dd>${esc(c.email || '—')}</dd></div>
          <div><dt>Phone</dt><dd>${esc(c.phone || '—')}</dd></div>
          <div><dt>Screening status</dt><dd>${esc(c.recommendation)}</dd></div>
        </dl>
      </div>
      <div class="ring" role="img" aria-label="Match score ${fmt(c.score)} percent">
        <svg viewBox="0 0 128 128"><circle class="bg-c" cx="64" cy="64" r="52"/><circle class="fg" cx="64" cy="64" r="52"/></svg>
        <div class="ring-n">${fmt(c.score)}%</div>
      </div>
    </section>

    <div class="report-grid">
      <section class="panel card tone-${t} reveal" style="--i:1">
        <h3>Recommendation</h3>
        <p class="big-rec">${esc(c.recommendation)}</p>
        <p class="note">Based on the AI match score: Strong Match ≥ 80%, Consider 50–79%, Reject below 50%.</p>
      </section>
      <section class="panel card reveal" style="--i:2">
        <h3>Skills overview</h3>
        <p class="big-rec" style="color:var(--text)">${c.matched_skills.length}<span class="muted" style="font-size:15px;font-weight:500"> of ${c.reference_skills.length} reference skills matched</span></p>
        <p class="note">${c.skills.length} skills extracted from the resume.</p>
      </section>
      <section class="panel card reveal" style="--i:3">
        <h3>Matched skills</h3>
        <div class="tags">${chips(c.matched_skills, 'ok', 'check')}</div>
        <p class="note">Compared against reference profile: ${esc(c.reference_skills.join(', '))}</p>
      </section>
      <section class="panel card reveal" style="--i:4">
        <h3>Missing skills</h3>
        <div class="tags">${chips(c.missing_skills, 'bad', 'x')}</div>
        <p class="note">Compared against the same reference profile.</p>
      </section>
      <section class="panel card full reveal" style="--i:5">
        <h3>All extracted skills</h3>
        <div class="tags">${c.skills.map(s => `<span class="chip">${esc(s)}</span>`).join('') || '<span class="muted">None found</span>'}</div>
      </section>
    </div>`;

  requestAnimationFrame(() => requestAnimationFrame(() => {
    const fg = $('.ring .fg');
    if (fg) fg.style.strokeDashoffset = 326.73 * (1 - Math.max(0, Math.min(c.score, 100)) / 100);
  }));
}

/* ---------------- boot ---------------- */
const page = document.body.dataset.page;
if (page === 'home') initHome();
else if (page === 'board') initBoard();
else if (page === 'candidate') initCandidate();
})();