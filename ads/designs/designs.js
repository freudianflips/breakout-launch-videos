// Breakout static ad designs. The renderer (ads/engine/render.mjs) sets window.AD and window.BRAND
// before this runs; this file draws the ad, fits the type and sets window.READY.
//
//   AD    = { template, size: [w, h], fields: {...} }
//   BRAND = brand/brand.json
//
// Text fields take the brand's key-word markup: *pipeline.* (or a lone * to the end) sets the words
// in italic violet, a newline breaks the line. Each template adapts to square, wide (1.91:1) and tall (4:5).
(() => {
  const AD = window.AD || { template: 'verdict', size: [1200, 1200], fields: { headline: 'Pageview to *pipeline.' } };
  const B = window.BRAND || { colors: {}, gradients: {} };
  const [W, H] = AD.size;
  const f = AD.fields || {};
  const root = document.getElementById('root');
  const shape = W / H > 1.4 ? 'wide' : H / W > 1.15 ? 'tall' : 'square';
  document.body.className = shape;

  const C = B.colors || {}, G = B.gradients || {};
  const css = document.documentElement.style;
  const set = (k, v) => v && css.setProperty(k, v);
  set('--u', `${Math.min(W, H) / 100}px`);
  set('--ground', C.ground); set('--ink', C.ink); set('--ink-2', C.ink_secondary);
  set('--accent', C.accent); set('--accent-on-dark', C.accent_on_dark); set('--dark-ink', C.dark_ink);
  set('--dark-mesh', G.dark_mesh); set('--card-lavender', G.card_lavender);
  set('--blush', '#ffd6f5');

  const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  // *a b* -> <em>a b</em>; a lone * runs to the end of its line; \n -> <br>
  const mk = (s) => esc(s).split('\n').map((line) => {
    line = line.replace(/\*([^*]+)\*/g, '<em class="key">$1</em>');
    const i = line.indexOf('*');
    return i < 0 ? line : `${line.slice(0, i)}<em class="key">${line.slice(i + 1)}</em>`;
  }).join('<br>');
  const logo = (dark) => f.logo === false ? '<span></span>' : `<img class="logo" src="../../brand/${dark ? 'logo-on-dark.svg' : 'logo.svg'}">`;
  const foot = (dark) => `<div class="foot">${logo(dark)}${f.label ? `<span class="label">${esc(f.label)}</span>` : ''}${f.cta ? `<span class="chip">${esc(f.cta)}</span>` : ''}</div>`;
  const kicker = () => f.kicker ? `<div class="kicker">${mk(f.kicker)}</div>` : '';
  const sub = () => f.sub ? `<p class="sub">${mk(f.sub)}</p>` : '';
  const headline = (cls = '') => `<div class="stage"><h1 class="display ${cls}" data-fit>${mk(f.headline)}</h1></div>`;

  const T = {
    // A short verdict in the display face. theme: light (default) or dark.
    verdict() {
      const dark = f.theme === 'dark';
      return `<div class="ad verdict ${dark ? 'dark' : 'light'}"><div class="bloom"></div>${kicker()}${headline()}${sub()}${foot(dark)}</div>`;
    },
    // Swiss grid type slam: lines in Manrope 800, each filling the width; a line wrapped in * goes violet.
    slam() {
      const lines = (f.lines || [f.headline]).map((l) => {
        const key = /^\*.*\*?$/.test(l);
        const strike = /^~.*~$/.test(l);
        return `<div class="line${key ? ' key' : ''}${strike ? ' strike' : ''}" data-slam>${esc(l.replace(/[*~]/g, ''))}</div>`;
      }).join('');
      return `<div class="ad slam light"><div class="grid"></div><div class="top mono"><span>${esc(f.index || '01')}</span><span>${esc(f.kicker || 'getbreakout.ai')}</span></div><div class="lines">${lines}</div>${sub()}${foot(false)}</div>`;
    },
    // The website agent answering a visitor, with a headline.
    chat() {
      const turns = (f.turns || []).map((t) => t.who === 'agent'
        ? `<div class="agent-row"><img src="../../assets/screens/agent-avatar.png"><div class="bubble agent">${esc(t.text)}</div></div>`
        : `<div class="bubble me">${esc(t.text)}</div>`).join('');
      return `<div class="ad chat lav"><div class="copy">${kicker()}${headline()}${sub()}${shape === 'wide' ? foot(false) : ''}</div>
        <div class="widget"><div class="head"><img src="../../assets/screens/agent-avatar.png">Breakout</div><div class="book">Book a Meeting</div>
        <div class="body">${turns}</div><div class="input">Type your message...<span class="send"></span></div><div class="powered">Powered by <b>breakout</b></div></div>
        ${shape === 'wide' ? '' : foot(false)}</div>`;
    },
    // Today versus with Breakout. Keep each side to 2 to 4 words.
    split() {
      return `<div class="ad split"><div class="pane today"><div class="k">${esc(f.left_label || 'Your site today')}</div><h1 class="display" data-fit-pane>${mk(f.left)}</h1><div class="spacer"></div></div>
        <div class="pane with"><div class="k">${esc(f.right_label || 'With Breakout')}</div><h1 class="display" data-fit-pane>${mk(f.right)}</h1>${logo(true)}</div>${f.source ? `<div class="src">${esc(f.source)}</div>` : ''}</div>`;
    },
    // A real product screen (assets/screens/), cropped to crop: [x, y, w, h] in image pixels.
    screen() {
      return `<div class="ad screen lav"><div class="copy">${kicker()}${headline()}${sub()}${shape === 'wide' ? foot(false) : ''}</div>
        <div class="shot"><img id="shot" src="../../${esc(f.image)}"></div>${shape === 'wide' ? '' : foot(false)}</div>`;
    },
    // A generic button-only chat widget (no vendor's UI or logo) beside Breakout's open question.
    buttons() {
      const bs = (f.buttons || ['Pricing', 'Book a demo', 'Careers', 'Something else']).map((b) => `<div class="b">${esc(b)}</div>`).join('');
      return `<div class="ad buttons light"><div class="bloom"></div><div class="copy">${kicker()}${headline()}${shape === 'wide' ? foot(false) : ''}</div>
        <div class="bw"><div class="gen"><div class="hi"><span class="dot"></span>${esc(f.greeting || 'Hi there! Choose an option:')}</div>${bs}<div class="miss">${esc(f.miss || 'No text box.')}</div></div>
        <div class="ask"><div class="q">${esc(f.question || 'Can it work with our CRM?')}</div><div class="display">${mk(f.answer || 'Go ahead.\n*Ask me stuff.*')}</div><div class="input">Type your message...</div></div></div>
        ${shape === 'wide' ? '' : foot(false)}</div>`;
    },
    // Conceptual: Breakout's resume, stamped.
    resume() {
      const secs = (f.sections || []).map((x) => `<div><h4>${esc(x.title)}</h4>${x.items ? `<ul>${x.items.map((i) => `<li>${esc(i)}</li>`).join('')}</ul>` : `<p>${esc(x.text)}</p>`}</div>`).join('');
      return `<div class="ad resume objbg lav"><div class="paper"><div class="nm">${esc(f.name || 'Breakout')}</div><div class="role">${esc(f.role)}</div>${secs}<div class="stamp">${esc(f.stamp)}</div></div>${foot(false)}</div>`;
    },
    // Conceptual: a multiple-choice question, one answer ringed.
    quiz() {
      const opts = (f.options || []).map((o, i) => `<div class="opt${i === f.answer ? ' right' : ''}"><span class="bub">${'abcdef'[i]}</span>${esc(o)}${i === f.answer ? '<svg class="ring" viewBox="0 0 100 40" preserveAspectRatio="none"><ellipse cx="50" cy="20" rx="48" ry="17" transform="rotate(-1.5 50 20)"/></svg>' : ''}</div>`).join('');
      return `<div class="ad quiz objbg lav"><div class="paper"><div class="qn">${esc(f.index || 'Question')}</div><div class="q">${mk(f.question)}</div>${opts}</div>${foot(false)}</div>`;
    },
    // Conceptual: a lost poster with tear-off tabs.
    poster() {
      const tabs = Array.from({ length: f.tab_count || 7 }, () => `<span>${esc(f.tab || 'getbreakout.ai')}</span>`).join('');
      const cursor = '<svg viewBox="0 0 24 32"><path d="M2 2 L2 26 L8 20 L12 30 L16 28 L12 18 L20 18 Z" fill="#4c00ff" stroke="#140b3c" stroke-width="1.2" stroke-linejoin="round"/></svg>';
      return `<div class="ad poster objbg violet"><div class="paper"><div class="big">${esc(f.big || 'MISSING')}</div><div class="pic">${cursor}</div><div class="who">${mk(f.who)}</div><div class="desc">${mk(f.desc)}</div><div class="tabs">${tabs}</div></div>${foot(true)}</div>`;
    },
    // Conceptual: a letter.
    letter() {
      const body = (f.body || []).map((p) => `<p>${mk(p)}</p>`).join('');
      return `<div class="ad letter objbg lav"><div class="paper"><p class="salut">${esc(f.salutation)}</p>${body}<p class="sign">${mk(f.signoff)}</p></div>${foot(false)}</div>`;
    },
    // Conceptual: a till receipt.
    receipt() {
      const rows = (f.items || []).map(([a, b]) => `<div class="row"><span>${esc(a)}</span><span class="dots"></span><span>${esc(b)}</span></div>`).join('');
      return `<div class="ad receipt objbg violet"><div class="paper"><div class="c hd">${esc(f.title)}</div><div class="c">${esc(f.subtitle || '')}</div><div class="rule"></div>${rows}<div class="rule"></div><div class="row tot"><span>${esc(f.total_label || 'TOTAL')}</span><span class="dots"></span><span>${esc(f.total)}</span></div><div class="bars"></div><div class="c ft">${esc(f.footer || '')}</div></div>${foot(true)}</div>`;
    },
    // Conceptual: sticky notes; ~text~ is done, the last note with key: true is the answer.
    sticky() {
      const notes = (f.notes || []).map((n) => {
        const done = /^~.*~$/.test(n);
        return `<div class="n${done ? ' done' : ''}">${esc(n.replace(/~/g, ''))}</div>`;
      }).join('') + (f.answer ? `<div class="n key">${mk(f.answer)}</div>` : '');
      return `<div class="ad sticky objbg lav"><div class="wall">${notes}</div>${foot(false)}</div>`;
    },
    // Conceptual: a search box and its suggestions (no search engine's brand). The suggestion with * is highlighted.
    search() {
      const sug = (f.suggestions || []).map((x) => {
        const key = x.startsWith('*');
        return `<div class="s${key ? ' key' : ''}">${esc(f.query)} <b>${esc(x.replace(/^\*/, ''))}</b></div>`;
      }).join('');
      return `<div class="ad search objbg lav"><div class="box"><div class="q"><span class="glass"></span>${esc(f.query)}<span class="caret"></span></div>${sug}</div>${foot(false)}</div>`;
    },
    // Conceptual: a project plan. rows: [label, start, length] in twelfths of the chart; key: the Breakout row.
    gantt() {
      const rows = (f.rows || []).map(([l, a, w]) => `<div class="row"><div class="l">${esc(l)}</div><div class="track"><div class="bar" style="left:${a / 12 * 100}%;width:${w / 12 * 100}%"></div></div></div>`).join('');
      const key = f.key ? `<div class="row key"><div class="l">${esc(f.key)}</div><div class="track"><div class="bar" style="left:0;width:1.2%"></div><div class="flag" style="left:3%">${esc(f.key_flag || '')}</div></div></div>` : '';
      return `<div class="ad gantt objbg lav"><div class="chart"><div class="title"><span>${esc(f.title || 'Implementation plan')}</span></div>${rows}${key}</div>${foot(false)}</div>`;
    },
    // Conceptual: a text thread (generic bubbles). messages: [{from: them|me|bo, who?, text}]
    thread() {
      const ms = (f.messages || []).map((m) => `${m.who ? `<div class="who${m.from === 'me' ? ' r' : ''}">${esc(m.who)}</div>` : ''}<div class="m ${m.from}">${esc(m.text)}</div>`).join('');
      return `<div class="ad thread objbg lav"><div class="phone"><div class="hdr">${esc(f.title || 'marketing')}</div>${ms}</div>${foot(false)}</div>`;
    },
    // Conceptual: a fortune cookie slip.
    fortune() {
      return `<div class="ad fortune objbg violet"><div class="slip"><p>${mk(f.fortune)}</p></div>${f.caption ? `<div class="cap">${mk(f.caption)}</div>` : ''}${foot(true)}</div>`;
    },
    // Conceptual: fine print, with highlighted lines; [[text]] marks a highlight.
    fine() {
      const t = esc(f.text || '').replace(/\[\[(.+?)\]\]/g, '<mark>$1</mark>');
      return `<div class="ad fine objbg lav"><div class="doc"><h3>${esc(f.title || 'Terms')}</h3><div class="t">${t}</div>${f.ours ? `<div class="ours">${mk(f.ours)}</div>` : ''}</div>${foot(false)}</div>`;
    },
    // Conceptual: a dating profile card (generic, no app's UI).
    dating() {
      const sec = (lab, xs, no) => `<div class="lab">${esc(lab)}</div><div class="chips">${(xs || []).map((x) => `<span class="chip2${no ? ' no' : ''}">${esc(x)}</span>`).join('')}</div>`;
      return `<div class="ad dating objbg lav"><div class="card"><div class="ph"><div class="nm">${esc(f.name || 'Breakout')}<small>${esc(f.tagline || '')}</small></div></div>
        <div class="bd">${sec(f.looking_label || 'Looking for', f.looking)}${sec(f.green_label || 'Green flags', f.green)}${sec(f.no_label || 'Dealbreakers', f.no, true)}</div></div>${foot(false)}</div>`;
    },
    // A real review, quoted word for word, with its source. [[text]] highlights.
    review() {
      const body = esc(f.body || '').replace(/\[\[(.+?)\]\]/g, '<mark>$1</mark>');
      return `<div class="ad review objbg lav"><div class="card"><div class="stars">\u2605\u2605\u2605\u2605\u2605</div><div class="ttl">${mk(f.title)}</div><div class="body">${body}</div><div class="by">${esc(f.source)}</div></div>${foot(false)}</div>`;
    },
    // An offer as a gift tag on a string. No product photography or third-party logos: the gift is named in type.
    gift() {
      const lines = (f.lines || []).map(([k, v]) => `<div class="ln"><b>${esc(k)}</b><span>${mk(v)}</span></div>`).join('');
      return `<div class="ad gift objbg violet"><div class="string"></div><div class="tag"><span class="hole"></span>${lines}<div class="prize">${mk(f.prize)}</div></div>${foot(true)}${f.terms ? `<div class="terms">${esc(f.terms)}</div>` : ''}</div>`;
    },
    // Pattern break: a lead form with every field struck through.
    form() {
      const fields = f.fields || ['First name', 'Last name', 'Work email', 'Company', 'Job title', 'Phone', 'How did you hear about us?'];
      const items = fields.map((x, i) => `<div class="fld${i === fields.length - 1 ? ' full' : ''}"><label>${esc(x)}</label><div class="box"></div></div>`).join('');
      return `<div class="ad form light"><div class="bloom"></div><div class="copy">${kicker()}${headline()}${sub()}${shape === 'wide' ? foot(false) : ''}</div>
        <div class="card">${items}<div class="submit">${esc(f.submit || 'Submit')}</div></div>${shape === 'wide' ? '' : foot(false)}</div>`;
    },
    // Pattern break: one small notification in a lot of empty space (a sample: label it).
    notice() {
      return `<div class="ad notice dark"><div class="corner">${f.logo === false ? '' : '<img src="../../brand/logo-on-dark.svg">'}</div>
        <div class="note-card">${f.generic ? '<img style="background:#cfcfd6">' : '<img src="../../brand/mark.svg">'}<div class="app">${esc(f.app || 'Breakout')}</div><div class="when">${esc(f.when || 'now')}</div><div class="msg">${mk(f.message)}</div></div>
        ${f.caption ? `<div class="caption">${mk(f.caption)}</div>` : ''}${f.label ? `<div class="caption" style="bottom:calc(var(--u)*3);font-size:calc(var(--u)*1.7)">${esc(f.label)}</div>` : ''}</div>`;
    },
    // Pattern break: a near-empty violet field and one small line.
    quiet() {
      return `<div class="ad quiet"><div class="line">${mk(f.line || f.headline)}</div>${f.logo === false ? '' : '<div class="corner"><img src="../../brand/logo-on-dark.svg"></div>'}</div>`;
    },
  };

  // Shrink a box's font until it fits its parent, from big to small.
  function fit(el, box, hi, lo) {
    let size = hi;
    el.style.fontSize = `${size}px`;
    while (size > lo && (el.scrollHeight > box.clientHeight + 1 || el.scrollWidth > box.clientWidth + 1)) {
      size *= 0.96;
      el.style.fontSize = `${size}px`;
    }
    return size;
  }

  async function draw() {
    if (!T[AD.template]) throw new Error(`no design "${AD.template}"; pick one of ${Object.keys(T).join(', ')}`);
    root.innerHTML = T[AD.template]();
    await document.fonts.ready;
    const u = Math.min(W, H) / 100;
    const cap = (f.max_size || (shape === 'wide' ? 13 : 15)) * u;
    document.querySelectorAll('[data-fit]').forEach((el) => fit(el, el.parentElement, cap, 3 * u));
    document.querySelectorAll('[data-fit-pane]').forEach((el) => {
      const pane = el.parentElement;
      el.style.maxHeight = `${pane.clientHeight * 0.62}px`;
      const box = { clientWidth: pane.clientWidth - 12 * u, get clientHeight() { return pane.clientHeight * 0.62; } };
      fit(el, box, 12 * u, 3 * u);
    });
    // Slam lines fill the width, then the stack shrinks together if it is too tall.
    const slams = [...document.querySelectorAll('[data-slam]')];
    if (slams.length) {
      const box = slams[0].parentElement;
      slams.forEach((el) => { el.style.fontSize = '100px'; el.style.fontSize = `${Math.min(100 * box.clientWidth / el.scrollWidth, 30 * u)}px`; });
      const total = slams.reduce((s, el) => s + el.offsetHeight, 0);
      if (total > box.clientHeight) slams.forEach((el) => { el.style.fontSize = `${parseFloat(el.style.fontSize) * box.clientHeight / total}px`; });
    }
    const img = document.getElementById('shot');
    if (img) {
      if (!img.complete) await new Promise((ok, bad) => { img.onload = ok; img.onerror = () => bad(new Error(`cannot load ${f.image}`)); });
      const shot = img.parentElement;
      const [cx, cy, cw, ch] = f.crop || [0, 0, img.naturalWidth, img.naturalHeight];
      const s = Math.min(shot.clientWidth / cw, shot.clientHeight / ch);   // contain: the whole crop shows
      img.style.width = `${img.naturalWidth}px`;
      img.style.transform = `translate(${-(cx + cw / 2) * s + shot.clientWidth / 2}px, ${-(cy + ch / 2) * s + shot.clientHeight / 2}px) scale(${s})`;
    }
  }

  draw().then(() => { window.READY = true; }).catch((e) => {
    document.getElementById('err').textContent = String(e.stack || e);
    window.READY = true;
    window.FAILED = String(e);
  });
})();
