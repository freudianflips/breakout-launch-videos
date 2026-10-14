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
        return `<div class="line${key ? ' key' : ''}" data-slam>${esc(l.replace(/\*/g, ''))}</div>`;
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
        <div class="pane with"><div class="k">${esc(f.right_label || 'With Breakout')}</div><h1 class="display" data-fit-pane>${mk(f.right)}</h1>${logo(true)}</div></div>`;
    },
    // A real product screen (assets/screens/), cropped to crop: [x, y, w, h] in image pixels.
    screen() {
      return `<div class="ad screen lav"><div class="copy">${kicker()}${headline()}${sub()}${shape === 'wide' ? foot(false) : ''}</div>
        <div class="shot"><img id="shot" src="../../${esc(f.image)}"></div>${shape === 'wide' ? '' : foot(false)}</div>`;
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
