// index 꽃 더미 아래 숨은 고양이: 꽃에 덮여 있을 땐 눌리지 않고, 꽃을 쓸어내 드러나면 누를 수 있음.
// 누르면 폴짝 뛰고 소설 원고실(claude.ai, 나만 열림)로 이동.
(() => {
  const URL = 'https://claude.ai/artifact/QPa6ztGnWjPL7LTmuGvTPv';
  const css = document.createElement('style');
  css.textContent = `
    a.cat-peek{position:fixed;left:max(4%,env(safe-area-inset-left,0px));bottom:calc(2% + env(safe-area-inset-bottom,0px));z-index:15;width:92px;height:140px;transform-origin:50% 100%;-webkit-tap-highlight-color:transparent;outline:none}
    a.cat-peek img{display:block;width:100%;height:100%;object-fit:contain;pointer-events:none;-webkit-user-drag:none;user-select:none}
    a.cat-peek:focus-visible{outline:1px dotted #ad9170;outline-offset:4px}
    a.cat-peek.jump{animation:cat-jump .62s cubic-bezier(.3,.7,.4,1)}
    @keyframes cat-jump{0%{transform:translateY(0) scaleY(1)}18%{transform:translateY(4px) scaleY(.9)}55%{transform:translateY(-46px) scaleY(1.04)}100%{transform:translateY(0) scaleY(1)}}
    @media (max-width:740px){a.cat-peek{width:70px;height:106px}}
    @media (prefers-reduced-motion:reduce){a.cat-peek.jump{animation:none}}`;
  document.head.appendChild(css);
  const a = document.createElement('a');
  a.className = 'cat-peek'; a.href = URL; a.setAttribute('aria-label', '소설 원고실 열기');
  a.innerHTML = '<img src="cat_peek.webp" alt="" width="171" height="260">';
  document.body.appendChild(a);

  // 누르는 순간(꽃이 날아가기 전)에 고양이가 꽃에 얼마나 덮여 있었는지 기억
  const covered = () => (window.petalsCover ? window.petalsCover(a.getBoundingClientRect()) : 0) >= 3;
  let hiddenAtDown = true;
  a.addEventListener('pointerdown', () => { hiddenAtDown = covered(); }, true);
  a.addEventListener('click', e => {
    if (e.detail && hiddenAtDown) { e.preventDefault(); return; }   // 아직 꽃 속에 묻혀 있으면 모르는 척
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.button) return;     // 새 탭으로 열 때는 바로
    e.preventDefault();
    a.classList.remove('jump'); void a.offsetWidth; a.classList.add('jump');
    setTimeout(() => { location.href = URL; }, matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 620);
  });
})();
