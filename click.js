/* 사이트 전체 클릭 효과음 (WebAudio, 외부 파일 없음). 끄려면 window.CLICK_SFX=false */
(function(){
  var ctx;
  function play(){
    if(window.CLICK_SFX===false) return;
    try{
      ctx = ctx || new (window.AudioContext||window.webkitAudioContext)();
      if(ctx.state==='suspended') ctx.resume();
      var t=ctx.currentTime, o=ctx.createOscillator(), g=ctx.createGain();
      o.type='sine';
      o.frequency.setValueAtTime(880,t);
      o.frequency.exponentialRampToValueAtTime(420,t+.06);
      g.gain.setValueAtTime(.0001,t);
      g.gain.exponentialRampToValueAtTime(.12,t+.005);
      g.gain.exponentialRampToValueAtTime(.0001,t+.09);
      o.connect(g); g.connect(ctx.destination);
      o.start(t); o.stop(t+.1);
    }catch(e){}
  }
  document.addEventListener('pointerdown',play,{passive:true,capture:true});
})();
