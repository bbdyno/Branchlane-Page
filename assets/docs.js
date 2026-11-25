(function () {
  var root = document.documentElement;
  var words = document.body.dataset;

  // Sections of the single page these docs used to be.
  var moved = window.docsMoved && window.docsMoved[location.hash.slice(1)];
  if (moved) { location.replace(moved); return; }

  document.querySelector('.theme').addEventListener('click', function () {
    var isDark = root.dataset.theme ? root.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches;
    root.dataset.theme = isDark ? 'light' : 'dark';
    try { localStorage.setItem('docs-theme', root.dataset.theme); } catch (e) {}
  });

  // Navigation drawer on narrow screens
  var burger = document.querySelector('.burger');
  function drawer(open) {
    document.body.classList.toggle('open', open);
    burger.setAttribute('aria-expanded', String(open));
    if (open) document.querySelector('.side a').focus();
  }
  burger.addEventListener('click', function () { drawer(!document.body.classList.contains('open')); });
  document.querySelector('.scrim').addEventListener('click', function () { drawer(false); });
  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && document.body.classList.contains('open')) { drawer(false); burger.focus(); }
  });
  var side = document.querySelector('.side');
  var current = side.querySelector('.group [aria-current]');
  if (current && current.offsetTop > side.clientHeight - 80) side.scrollTop = current.offsetTop - side.clientHeight / 2;

  document.addEventListener('click', function (event) {
    var button = event.target.closest('.copy');
    if (!button) return;
    var code = button.closest('.code').querySelector('code');
    function done(text) {
      button.textContent = text;
      setTimeout(function () { button.textContent = words.copy; }, 1600);
    }
    function select() {
      getSelection().selectAllChildren(code);
      done(words.selected);
    }
    if (!navigator.clipboard) return select();
    navigator.clipboard.writeText(code.textContent).then(function () { done(words.copied); }, select);
  });

  // Tabs. A choice, such as the client, is kept for other pages.
  var saved;
  try { saved = localStorage.getItem('docs-tab'); } catch (e) {}
  document.querySelectorAll('.tabs').forEach(function (tabs) {
    var buttons = Array.prototype.slice.call(tabs.querySelectorAll('[role="tab"]'));
    function choose(button, focus) {
      buttons.forEach(function (other) {
        var isOn = other === button;
        other.setAttribute('aria-selected', String(isOn));
        other.tabIndex = isOn ? 0 : -1;
        document.getElementById(other.getAttribute('aria-controls')).hidden = !isOn;
      });
      if (focus) button.focus();
    }
    buttons.forEach(function (button, index) {
      button.addEventListener('click', function () {
        choose(button);
        try { localStorage.setItem('docs-tab', button.dataset.tab); } catch (e) {}
      });
      button.addEventListener('keydown', function (event) {
        var step = event.key === 'ArrowRight' ? 1 : event.key === 'ArrowLeft' ? -1 : 0;
        if (step) choose(buttons[(index + step + buttons.length) % buttons.length], true);
      });
    });
    choose(buttons.filter(function (b) { return b.dataset.tab === saved; })[0] || buttons[0]);
  });

  // The outline follows the text
  var links = Array.prototype.slice.call(document.querySelectorAll('.outline a'));
  var heads = links.map(function (link) { return document.getElementById(decodeURIComponent(link.hash.slice(1))); });
  function follow() {
    var active = 0;
    heads.forEach(function (head, index) { if (head && head.getBoundingClientRect().top < 120) active = index; });
    if (innerHeight + scrollY >= document.body.scrollHeight - 4 && scrollY > 0) active = links.length - 1;
    links.forEach(function (link, index) { link.classList.toggle('on', index === active); });
  }
  if (links.length) {
    addEventListener('scroll', follow, { passive: true });
    follow();
  }

  // Search
  var dialog = document.querySelector('dialog');
  var input = dialog.querySelector('input');
  var list = dialog.querySelector('.hits');
  var index, selected = 0;

  function open() {
    if (dialog.open) return;
    dialog.showModal();
    input.select();
    if (!index) {
      fetch(words.index).then(function (r) { return r.json(); }).then(function (data) { index = data; show(); })
        .catch(function () { message(words.failed); });
    }
  }
  function message(text) {
    list.textContent = '';
    var item = document.createElement('li');
    item.className = 'none';
    item.textContent = text;
    list.appendChild(item);
  }
  function marked(parent, text, terms) {
    var lower = text.toLowerCase(), at = 0;
    while (at < text.length) {
      var best = -1, length = 0;
      terms.forEach(function (term) {
        var found = lower.indexOf(term, at);
        if (found >= 0 && (best < 0 || found < best)) { best = found; length = term.length; }
      });
      if (best < 0) break;
      parent.appendChild(document.createTextNode(text.slice(at, best)));
      var mark = document.createElement('mark');
      mark.textContent = text.slice(best, best + length);
      parent.appendChild(mark);
      at = best + length;
    }
    parent.appendChild(document.createTextNode(text.slice(at)));
  }
  function show() {
    if (!index) return;
    var terms = input.value.toLowerCase().split(/\s+/).filter(Boolean);
    if (!terms.length) { message(words.hint); return; }
    var hits = [];
    index.forEach(function (entry) {
      var title = (entry.p + ' ' + entry.h).toLowerCase(), body = entry.t.toLowerCase(), score = 0;
      var all = terms.every(function (term) {
        if (entry.h.toLowerCase().indexOf(term) >= 0) score += 12;
        else if (title.indexOf(term) >= 0) score += 6;
        else if (body.indexOf(term) >= 0) score += 2;
        else return false;
        return true;
      });
      // The area being read comes first among equals.
      if (entry.u.split('#')[0].indexOf(words.area) === 0) score += 1;
      if (all) hits.push({ entry: entry, score: score });
    });
    hits.sort(function (a, b) { return b.score - a.score; });
    if (!hits.length) { message(words.none); return; }
    list.textContent = '';
    selected = 0;
    hits.slice(0, 12).forEach(function (hit, i) {
      var item = document.createElement('li'), link = document.createElement('a');
      link.href = words.base + hit.entry.u;
      link.setAttribute('aria-selected', String(i === 0));
      var title = document.createElement('b');
      marked(title, hit.entry.h === hit.entry.p ? hit.entry.p : hit.entry.p + ' › ' + hit.entry.h, terms);
      var small = document.createElement('small');
      var at = terms.map(function (term) { return hit.entry.t.toLowerCase().indexOf(term); }).filter(function (n) { return n >= 0; })[0] || 0;
      marked(small, (at > 40 ? '... ' : '') + hit.entry.t.slice(Math.max(0, at - 40), at + 140), terms);
      link.append(title, small);
      item.appendChild(link);
      list.appendChild(item);
    });
  }
  function move(step) {
    var all = list.querySelectorAll('a');
    if (!all.length) return;
    all[selected].setAttribute('aria-selected', 'false');
    selected = (selected + step + all.length) % all.length;
    all[selected].setAttribute('aria-selected', 'true');
    all[selected].scrollIntoView({ block: 'nearest' });
  }
  document.querySelector('.find').addEventListener('click', open);
  input.addEventListener('input', show);
  input.addEventListener('keydown', function (event) {
    if (event.isComposing) return;
    if (event.key === 'ArrowDown') { move(1); event.preventDefault(); }
    if (event.key === 'ArrowUp') { move(-1); event.preventDefault(); }
    if (event.key === 'Enter') {
      var link = list.querySelectorAll('a')[selected];
      if (link) { dialog.close(); location.href = link.href; }
    }
  });
  list.addEventListener('click', function (event) { if (event.target.closest('a')) dialog.close(); });
  dialog.addEventListener('click', function (event) { if (event.target === dialog) dialog.close(); });
  document.addEventListener('keydown', function (event) {
    var isTyping = /^(INPUT|TEXTAREA)$/.test(event.target.tagName);
    if ((event.key === 'k' && (event.metaKey || event.ctrlKey)) || (event.key === '/' && !isTyping)) { event.preventDefault(); open(); }
  });
})();
