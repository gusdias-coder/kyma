
(function () {
 'use strict';
 var stage=document.getElementById('cinema-stage'),controller=document.getElementById('cinema-controller');
 var status=document.getElementById('cinema-status'),notice=document.getElementById('cinema-notice');
 var noticeMessage=document.getElementById('cinema-notice-message'),retry=document.getElementById('cinema-retry');
 if(!stage||!controller)return;
 var buttons=controller.querySelectorAll('button'),videos=stage.querySelectorAll('video');
 var branches={scene:{name:'Cenário',prefix:'scene'},light:{name:'Luz',prefix:'light'},colorway:{name:'Look',prefix:'clothing'},fullLook:{name:'Modelo',prefix:'cast'}};
 var scene='base',playback='loading',direction='forward',locked=false,visible=null;
 var token=0,job=null,failedJob=null,bootCleanup=null,booting=false,bootRemaining=12000,hoverIndex=0;
 var raf=window.requestAnimationFrame.bind(window),caf=window.cancelAnimationFrame.bind(window);
 var mobile=window.matchMedia('(max-width:700px)');
 function announce(message){status.textContent=message;}
 function syncState(){stage.setAttribute('data-scene',scene);stage.setAttribute('data-playback',playback);stage.setAttribute('data-direction',direction);controller.setAttribute('aria-busy',locked||playback==='loading'?'true':'false');}
 function setNotice(message,action){noticeMessage.textContent=message;retry.hidden=!action;notice.hidden=false;}
 function hideNotice(){notice.hidden=true;retry.hidden=true;}
 function ready(v){return v.readyState>=2&&!v.error;}
 function pairReady(branch){var p=branches[branch].prefix;return ready(document.getElementById(p+'-forward'))&&ready(document.getElementById(p+'-reverse'));}
 function focusSafely(button){try{button.focus({preventScroll:true});}catch(e){button.focus();}}
 function semantics(){
  var i,b,key,selected=scene!=='base';
  for(i=0;i<buttons.length;i++){
   b=buttons[i];key=b.getAttribute('data-branch');
   var concealed=selected&&key!==scene;
   b.disabled=locked||playback==='loading'||playback==='error'||concealed||!pairReady(key);
   b.setAttribute('tabindex',b.disabled?'-1':'0');
   if(concealed){b.setAttribute('aria-hidden','true');}else{b.removeAttribute('aria-hidden');}
   b.setAttribute('aria-label',selected&&key===scene?'Voltar':branches[key].name);
   b.setAttribute('aria-pressed',selected&&key===scene?'true':'false');
  }
  syncState();
 }
 function highlight(index){
  if(locked||scene!=='base'||playback!=='ready')return;
  controller.style.setProperty('--cap-left',index===0?'-5px':(index*20)+'%');
  controller.style.setProperty('--cap-width',index===0||index===4?'calc(20% + 5px)':'20%');
  controller.classList.toggle('highlighted',index>0);
 }
 function restingHighlight(){var i;for(i=0;i<buttons.length;i++)if(document.activeElement===buttons[i]){highlight(i+1);return;}highlight(hoverIndex);}
 function labelPosition(button){
  /* Measure the expanded grid cell, without counting its existing translation. */
  var bounds=controller.getBoundingClientRect(),cell=button.getBoundingClientRect();
  var style=window.getComputedStyle(button),matrix=style.transform,tx=0,ty=0,parts;
  if(matrix&&matrix!=='none'){parts=matrix.slice(matrix.indexOf('(')+1,-1).split(',');if(parts.length===6){tx=parseFloat(parts[4])||0;ty=parseFloat(parts[5])||0;}}
  var x=bounds.left+bounds.width/2,y=bounds.top+(mobile.matches?window.innerHeight*.04:35);
  button.style.setProperty('--label-x',(x-(cell.left+cell.width/2-tx))+'px');
  button.style.setProperty('--label-y',(y-(cell.top+cell.height/2-ty))+'px');
 }
 function collapse(button){
  var i;for(i=0;i<buttons.length;i++)buttons[i].classList.toggle('chosen',buttons[i]===button);
  labelPosition(button);controller.classList.remove('returning','selected','highlighted');controller.classList.add('collapsed');
 }
 function expand(){controller.style.setProperty('--cap-left','-5px');controller.style.setProperty('--cap-width','calc(20% + 5px)');controller.classList.add('returning');controller.classList.remove('selected','collapsed','highlighted');}
 function reveal(video){
  var i;for(i=0;i<videos.length;i++){if(videos[i]!==video){videos[i].pause();videos[i].classList.remove('visible');}}
  video.classList.add('visible');visible=video;
 }
 function current(j,a){return job===j&&j.token===token&&(a===undefined||j.attempt===a);}
 function cleanStart(j){var i;for(i=0;i<j.startClean.length;i++)j.startClean[i]();j.startClean=[];}
 function cleanMonitor(j){if(j.raf){caf(j.raf);j.raf=0;}if(j.frame&&j.video.cancelVideoFrameCallback){j.video.cancelVideoFrameCallback(j.frame);j.frame=0;}if(j.ended){j.video.removeEventListener('ended',j.ended);j.ended=null;}}
 function cleanDeadline(j){if(j.timer){clearTimeout(j.timer);j.timer=0;j.remaining=Math.max(0,j.remaining-(Date.now()-j.timerStarted));}}
 function armDeadline(j,a){cleanDeadline(j);if(document.hidden)return;j.timerStarted=Date.now();j.timer=setTimeout(function(){if(current(j,a)&&!document.hidden)fail(j,'O vídeo demorou para carregar. Tente novamente.');},j.remaining);}
 function seekStart(j,a){
  var v=j.video;
  return new Promise(function(resolve,reject){
   if(!current(j,a))return;
   /* A held visible endpoint is never rewound. A retry resumes that frame. */
   if(v===visible&&v.currentTime>.001){j.resumeAt=v.currentTime;resolve();return;}
   j.resumeAt=0;
   if(v.currentTime<=.001&&!v.seeking){resolve();return;}
   var onSeek=function(){if(current(j,a)&&!v.seeking&&v.currentTime<=.001)resolve();};
   v.addEventListener('seeked',onSeek);j.startClean.push(function(){v.removeEventListener('seeked',onSeek);});
   try{v.currentTime=0;}catch(e){reject(e);}
  });
 }
 function decodedFrame(j,a){
  var v=j.video;
  return new Promise(function(resolve){
   var done=false,frameId=0,tick=0,playing=false;
   function validTime(t){return j.resumeAt?Math.abs(t-j.resumeAt)<=.5:t<=.5;}
   function accept(time){if(done||!current(j,a)||document.hidden||!ready(v)||!validTime(time))return false;done=true;resolve();return true;}
   function frame(now,meta){frameId=0;if(!current(j,a)||done)return;if(!accept(meta.mediaTime))frameId=v.requestVideoFrameCallback(frame);}
   function secondTick(){tick=0;if(!current(j,a)||done||document.hidden)return;if(playing&&!v.paused&&ready(v)&&validTime(v.currentTime))accept(v.currentTime);else tick=raf(firstTick);}
   function firstTick(){tick=raf(secondTick);}
   function onPlaying(){playing=true;if(!v.requestVideoFrameCallback&&!tick)tick=raf(firstTick);}
   v.addEventListener('playing',onPlaying);
   if(v.requestVideoFrameCallback)frameId=v.requestVideoFrameCallback(frame);
   j.startClean.push(function(){done=true;v.removeEventListener('playing',onPlaying);if(frameId&&v.cancelVideoFrameCallback)v.cancelVideoFrameCallback(frameId);if(tick)caf(tick);});
  });
 }
 function prepare(j){
  if(!current(j)||document.hidden)return;
  cleanStart(j);var a=++j.attempt,v=j.video;j.phase='first';playback='starting';syncState();armDeadline(j,a);
  seekStart(j,a).then(function(){
   if(!current(j,a)||document.hidden)return;
   /* Register decoding before play; Promise.all propagates either rejection. */
   var framePromise=decodedFrame(j,a),playPromise;
   try{playPromise=v.play();}catch(e){playPromise=Promise.reject(e);}
   return Promise.all([playPromise||Promise.resolve(),framePromise]).then(function(){
    if(!current(j,a)||document.hidden)return;
    cleanDeadline(j);cleanStart(j);reveal(v);j.revealed=true;j.phase='playing';playback='playing';syncState();monitor(j);
   });
  }).catch(function(e){if(current(j,a)&&!document.hidden)fail(j,e&&e.name==='NotAllowedError'?'Reprodução bloqueada. Use Tentar novamente.':'Não foi possível reproduzir. Tente novamente.');});
 }
 function terminal(j){var guard=j.direction==='reverse'&&j.branch==='scene'?.18:.08;return Math.max(0,j.video.duration-guard);}
 function monitor(j){
  if(!current(j))return;
  cleanMonitor(j);var v=j.video,hold=terminal(j);
  function progress(){
   if(!current(j))return;
   if(!document.hidden){
    if(j.direction==='forward'&&v.currentTime>=Math.min(v.duration*.12,.9))stage.classList.add('title-hidden');
    if(!v.requestVideoFrameCallback&&v.currentTime>=hold){complete(j);return;}
    if(v.currentTime>j.lastTime+.001){j.lastTime=v.currentTime;j.stallRemaining=12000;}
    else{j.stallRemaining-=Math.min(100,Date.now()-j.lastTick);if(j.stallRemaining<=0){fail(j,'A reprodução foi interrompida. Tente novamente.');return;}}
   }
   j.lastTick=Date.now();j.raf=raf(progress);
  }
  function frame(now,meta){j.frame=0;if(!current(j))return;if(!document.hidden&&meta.mediaTime>=hold-.001){complete(j);return;}j.frame=v.requestVideoFrameCallback(frame);}
  j.lastTime=v.currentTime;j.lastTick=Date.now();j.stallRemaining=12000;
  if(v.requestVideoFrameCallback)j.frame=v.requestVideoFrameCallback(frame);
  j.ended=function(){if(current(j))complete(j);};v.addEventListener('ended',j.ended);
  j.raf=raf(progress);
 }
 function complete(j){
  if(!current(j)||j.completed)return;j.completed=true;
  j.video.pause();cleanDeadline(j);cleanStart(j);cleanMonitor(j);
  scene=j.direction==='forward'?j.branch:'base';playback='ready';locked=false;failedJob=null;job=null;hideNotice();
  if(scene==='base'){stage.classList.remove('title-hidden');controller.classList.remove('returning','selected','collapsed');}
  else{stage.classList.add('title-hidden');controller.classList.remove('returning');controller.classList.add('collapsed','selected');}
  semantics();announce(scene==='base'?'Editorial inicial restaurado. Escolha uma opção.':branches[scene].name+' selecionado. Use Voltar para restaurar o editorial.');
  if(j.returnFocus)focusSafely(j.button);
 }
 function fail(j,message){
  if(!current(j))return;j.video.pause();cleanDeadline(j);cleanStart(j);cleanMonitor(j);j.attempt++;
  failedJob=j;job=null;locked=false;playback='error';semantics();setNotice(message,true);announce(message);focusSafely(retry);
 }
 function begin(branch,button,retryJob){
  if(locked)return;
  if(!retryJob&&(playback!=='ready'||!pairReady(branch)||(scene!=='base'&&scene!==branch)))return;
  /* This lock is acquired in the event handler, before any promise or timer. */
  locked=true;var heldFocus=retryJob?retryJob.returnFocus:document.activeElement===button;
  direction=retryJob?retryJob.direction:(scene==='base'?'forward':'reverse');
  var prefix=branches[branch].prefix,v=document.getElementById(prefix+'-'+direction);
  if(visible)visible.pause();
  var j={token:++token,attempt:0,phase:'first',branch:branch,button:button,direction:direction,video:v,returnFocus:heldFocus,startClean:[],remaining:12000,timer:0,raf:0,frame:0,revealed:false,completed:false};
  job=j;failedJob=null;playback='starting';hideNotice();semantics();
  if(direction==='forward')collapse(button);else expand();
  announce(direction==='forward'?'Alterando '+branches[branch].name.toLowerCase()+'.':'Voltando ao editorial inicial.');
  if(retryJob&&v.error&&v!==visible)v.load();
  prepare(j);
 }
 function boot(){
  if(visible||booting)return;
  if(bootCleanup)bootCleanup();booting=true;playback='loading';locked=false;semantics();
  var bootToken=++token,v=document.getElementById('clothing-forward'),timer=0,tick=0,frame=0,started=0;
  function valid(){return token===bootToken&&!visible;}
  function cleanup(){clearTimeout(timer);if(tick)caf(tick);if(frame&&v.cancelVideoFrameCallback)v.cancelVideoFrameCallback(frame);v.removeEventListener('loadeddata',check);document.removeEventListener('visibilitychange',visibility);bootCleanup=null;booting=false;}
  function commit(){if(!valid()||document.hidden||!ready(v)||v.currentTime>.001)return;v.pause();cleanup();reveal(v);playback='ready';semantics();hideNotice();announce('Editorial pronto. Escolha uma opção.');}
  function check(){if(!valid()||document.hidden)return;if(ready(v)&&!tick)tick=raf(function(){tick=raf(function(){tick=0;commit();});});}
  function decoded(now,meta){frame=0;if(!valid())return;if(meta.mediaTime<=.001&&ready(v))commit();else frame=v.requestVideoFrameCallback(decoded);}
  function startTimer(){if(document.hidden)return;started=Date.now();timer=setTimeout(function(){if(!valid()||document.hidden)return;cleanup();playback='error';semantics();setNotice('O editorial não carregou. Você pode continuar comprando abaixo.',true);announce('Editorial indisponível. Tente novamente ou explore a coleção.');},bootRemaining);}
  function visibility(){if(document.hidden){clearTimeout(timer);if(started)bootRemaining=Math.max(1,bootRemaining-(Date.now()-started));started=0;}else{startTimer();check();}}
  bootCleanup=cleanup;v.pause();v.addEventListener('loadeddata',check);document.addEventListener('visibilitychange',visibility);
  if(v.requestVideoFrameCallback)frame=v.requestVideoFrameCallback(decoded);
  startTimer();check();
 }
 var i;
 for(i=0;i<buttons.length;i++)(function(button,index){
  button.addEventListener('click',function(){begin(button.getAttribute('data-branch'),button);});
  button.addEventListener('mouseenter',function(){hoverIndex=index;highlight(index);});
  button.addEventListener('focus',function(){highlight(index);});
  button.addEventListener('blur',function(){restingHighlight();});
 })(buttons[i],i+1);
 controller.addEventListener('mouseleave',function(){hoverIndex=0;restingHighlight();});
 controller.addEventListener('pointermove',function(event){var bounds=controller.getBoundingClientRect();controller.style.setProperty('--glass-x',Math.max(0,Math.min(100,(event.clientX-bounds.left)/bounds.width*100))+'%');controller.style.setProperty('--glass-y',Math.max(0,Math.min(100,(event.clientY-bounds.top)/bounds.height*100))+'%');});
 for(i=0;i<videos.length;i++)(function(v){
  v.muted=true;
  function update(){semantics();if(!visible&&!booting&&playback!=='error')boot();}
  v.addEventListener('loadeddata',update);v.addEventListener('canplaythrough',update);
  v.addEventListener('error',function(){if(job&&job.video===v)fail(job,'Esta opção não carregou. Tente novamente.');else{semantics();setNotice('Uma opção não carregou. Tente novamente.',true);announce('Algumas opções estão indisponíveis. Tente novamente.');}});
 })(videos[i]);
 retry.addEventListener('click',function(){
  if(locked)return;
  if(failedJob){var failed=failedJob;begin(failed.branch,failed.button,failed);return;}
  hideNotice();bootRemaining=12000;var k;for(k=0;k<videos.length;k++)if(!ready(videos[k])&&videos[k]!==visible)videos[k].load();
  if(!visible){if(bootCleanup)bootCleanup();boot();}else{playback='ready';semantics();announce('Carregando as opções novamente.');}
 });
 document.addEventListener('visibilitychange',function(){
  var j=job;if(!j)return;
  if(document.hidden){
   j.video.pause();
   if(j.phase==='first'){cleanDeadline(j);cleanStart(j);j.attempt++;if(j.video!==visible){try{j.video.currentTime=0;}catch(e){/* Seek is retried on return. */}}}
   else cleanMonitor(j);
  }else if(j.phase==='first'){prepare(j);}
  else{var a=j.attempt,p;try{p=j.video.play();}catch(e){p=Promise.reject(e);}Promise.resolve(p).then(function(){if(current(j,a)&&!document.hidden)monitor(j);}).catch(function(){if(current(j,a)&&!document.hidden)fail(j,'Não foi possível retomar o vídeo. Tente novamente.');});}
 });
 window.addEventListener('resize',function(){var chosen=controller.querySelector('.chosen');if(chosen&&controller.classList.contains('collapsed'))labelPosition(chosen);});
 window.addEventListener('pagehide',function(){token++;if(job){job.video.pause();cleanDeadline(job);cleanStart(job);cleanMonitor(job);}if(bootCleanup)bootCleanup();for(var n=0;n<videos.length;n++)videos[n].pause();});
 window.addEventListener('pageshow',function(event){if(!event.persisted)return;if(job){job.token=token;prepare(job);}else if(!visible){boot();}});
 syncState();boot();
})();
