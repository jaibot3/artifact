/* 사이트 전체 클릭 효과음 (WebAudio, 외부 파일 없음). 끄려면 window.CLICK_SFX=false */
(function(){
  var ctx;
  function play(up){
    if(window.CLICK_SFX===false) return;
    try{
      ctx = ctx || new (window.AudioContext||window.webkitAudioContext)();
      if(ctx.state==='suspended') ctx.resume();
      var t=ctx.currentTime, o=ctx.createOscillator(), g=ctx.createGain();
      o.type='sine';
      var a=up===true?500:880,b=up===true?1000:420;
      if(up===false){a=900;b=380;}
      o.frequency.setValueAtTime(a,t);
      o.frequency.exponentialRampToValueAtTime(b,t+(up===undefined?.06:.12));
      g.gain.setValueAtTime(.0001,t);
      g.gain.exponentialRampToValueAtTime(.12,t+.005);
      g.gain.exponentialRampToValueAtTime(.0001,t+(up===undefined?.09:.16));
      o.connect(g); g.connect(ctx.destination);
      o.start(t); o.stop(t+.2);
    }catch(e){}
  }
  window.playSfx=play;
  document.addEventListener('pointerdown',function(e){
    if(e.target.closest&&e.target.closest('.toggle'))return; /* more/less는 전용 소리 */
    play();
  },{passive:true,capture:true});
})();
