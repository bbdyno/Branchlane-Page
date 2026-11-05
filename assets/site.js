(function () {
  var top = document.querySelector('.top');
  var rail = document.querySelector('.rail');
  var flow = document.querySelector('.flow');

  function onScroll() {
    if (top) top.classList.toggle('stuck', window.scrollY > 8);
    if (rail && flow) {
      var box = rail.getBoundingClientRect();
      var progress = (window.innerHeight * 0.55 - box.top) / box.height;
      rail.style.setProperty('--p', Math.max(0, Math.min(1, progress)).toFixed(4));
    }
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll);
  onScroll();

  if ('IntersectionObserver' in window) {
    var reveal = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('in');
        reveal.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -8% 0px' });
    document.querySelectorAll('.rv').forEach(function (el) { reveal.observe(el); });

    var light = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting || entry.boundingClientRect.top < 0) entry.target.classList.add('lit');
        else entry.target.classList.remove('lit');
      });
    }, { rootMargin: '-50% 0px -50% 0px' });
    document.querySelectorAll('.node').forEach(function (el) { light.observe(el); });

    var stage = document.querySelector('.stage');
    if (stage) {
      var frames = stage.querySelectorAll('.stage-frame .shot');
      var chapters = document.querySelectorAll('.chapter');
      var tour = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var index = Array.prototype.indexOf.call(chapters, entry.target);
          chapters.forEach(function (c, i) { c.classList.toggle('on', i === index); });
          frames.forEach(function (f, i) { f.classList.toggle('on', i === index); });
          stage.style.setProperty('--glow', getComputedStyle(entry.target).getPropertyValue('--c'));
        });
      }, { rootMargin: '-46% 0px -46% 0px' });
      chapters.forEach(function (c) { tour.observe(c); });
    }
  } else {
    document.querySelectorAll('.rv').forEach(function (el) { el.classList.add('in'); });
  }

  // Rebase playground. Rows run newest first, and a squash folds into the next kept commit below it.
  var todo = document.querySelector('.todo');
  if (!todo) return;
  var result = document.querySelector('.result');
  var count = document.querySelector('.lab-count');
  var rows = Array.prototype.slice.call(todo.querySelectorAll('li'));
  var text = todo.parentElement.parentElement.dataset;

  function format(template, values) {
    return template.replace(/\{(\w+)\}/g, function (_, key) { return values[key]; });
  }

  function render() {
    var kept = [];
    rows.slice().reverse().forEach(function (row) {
      var action = row.dataset.action;
      var message = row.querySelector('.msg').textContent;
      if (action === 'drop') return;
      if (action === 'squash' && kept.length) { kept[kept.length - 1].count += 1; return; }
      kept.push({ message: message, count: 1 });
    });
    result.textContent = '';
    if (!kept.length) {
      var empty = document.createElement('li');
      empty.innerHTML = '<span class="r-msg empty"></span>';
      empty.firstChild.textContent = text.empty;
      result.appendChild(empty);
    }
    kept.reverse().forEach(function (commit) {
      var item = document.createElement('li');
      var message = document.createElement('span');
      message.className = 'r-msg';
      message.textContent = commit.message;
      item.appendChild(message);
      if (commit.count > 1) {
        item.className = 'combo';
        var sub = document.createElement('span');
        sub.className = 'r-sub';
        sub.textContent = format(text.combined, { n: commit.count });
        item.appendChild(sub);
      }
      result.appendChild(item);
    });
    count.textContent = format(text.count, { from: rows.length, to: kept.length });
  }

  function setAction(row, action) {
    if (row.querySelector('[data-a="' + action + '"]').disabled) return;
    row.dataset.action = action;
    row.classList.toggle('drop', action === 'drop');
    row.classList.toggle('squash', action === 'squash');
    row.querySelectorAll('button').forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.dataset.a === action));
    });
    render();
  }

  rows.forEach(function (row) {
    setAction(row, row.dataset.action);
    row.addEventListener('click', function (event) {
      var button = event.target.closest('button');
      if (button) setAction(row, button.dataset.a);
    });
  });
})();
