// 하단 띠에 숨은 고양이: 머리만 살짝 내밀고 있다가, 누르면 폴짝 뛰고 소설 원고실(claude.ai, 나만 열림)로 이동.
(() => {
  const foot = document.querySelector('footer.foot');
  if (!foot) return;
  const URL = 'https://claude.ai/artifact/QPa6ztGnWjPL7LTmuGvTPv';
  const css = document.createElement('style');
  css.textContent = `
    footer.foot{position:relative;overflow:hidden}
    .foot a.cat-peek{position:absolute;right:14%;bottom:0;width:86px;height:130px;opacity:1;transform:translateY(34%);transition:transform .45s cubic-bezier(.2,.8,.2,1);-webkit-tap-highlight-color:transparent}
    .foot a.cat-peek:hover,.foot a.cat-peek:focus-visible{opacity:1;transform:translateY(16%)}
    .foot a.cat-peek img{display:block;width:100%;height:100%;object-fit:contain;pointer-events:none;-webkit-user-drag:none}
    .foot a.cat-peek.jump{animation:cat-jump .62s cubic-bezier(.3,.7,.4,1) forwards}
    @keyframes cat-jump{0%{transform:translateY(16%) scaleY(1)}18%{transform:translateY(22%) scaleY(.9)}55%{transform:translateY(-14%) scaleY(1.04)}100%{transform:translateY(16%) scaleY(1)}}
    @media (max-width:740px){.foot a.cat-peek{right:8%;width:66px;height:100px}}
    @media (prefers-reduced-motion:reduce){.foot a.cat-peek{transition:none}.foot a.cat-peek.jump{animation:none}}`;
  document.head.appendChild(css);
  const a = document.createElement('a');
  a.className = 'cat-peek'; a.href = URL; a.setAttribute('aria-label', '소설 원고실 열기');
  a.innerHTML = '<img src="cat_peek.webp" alt="" width="171" height="260" loading="lazy">';
  a.addEventListener('click', e => {
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.button) return;   // 새 탭으로 열 때는 바로
    e.preventDefault();
    a.classList.remove('jump'); void a.offsetWidth; a.classList.add('jump');
    setTimeout(() => { location.href = URL; }, matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 620);
  });
  foot.appendChild(a);
})();
