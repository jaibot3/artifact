/* project-data.js의 설명을 [data-project] 자리에 그림.
   상세 페이지(.process): 소제목·문단·키워드 전부 / portfolio1.html(.more-desc): 문단만 */
(function () {
  var D = window.PROJECTS || {};
  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }
  function text(s) {
    return (s.hl ? '<p class="hl">' + esc(s.hl) + '</p>' : '') +
      (s.p || []).map(function (p) { return '<p>' + esc(p) + '</p>'; }).join('');
  }
  function full(s) {
    return '<div class="step"><h3 class="k">' + esc(s.k) + '</h3><div class="v">' + text(s) + '</div>' +
      (s.ex ? '<ul class="v ex">' + s.ex.map(function (e) { return '<li>' + esc(e) + '</li>'; }).join('') + '</ul>' : '') +
      '</div>';
  }
  function prose(s) {
    return '<div class="md-step"><h4 class="k">' + esc(s.k) + '</h4><div class="v">' + text(s) + '</div></div>';
  }
  document.querySelectorAll('[data-project]').forEach(function (el) {
    var p = D[el.getAttribute('data-project')];
    if (p) el.innerHTML = p.steps.map(el.classList.contains('more-desc') ? prose : full).join('');
  });
})();
