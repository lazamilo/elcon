(function(){
  const d=document, html=d.documentElement;
  const reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const isDesk=()=>window.innerWidth>980;
  html.classList.add('js');
  const hasGsap=typeof gsap!=='undefined';
  if(hasGsap) gsap.registerPlugin(ScrollTrigger);

  /* smooth scroll */
  let lenis=null;
  if(!reduce && typeof Lenis!=='undefined'){
    lenis=new Lenis({lerp:.1,smoothWheel:true});
    lenis.on('scroll',()=>hasGsap&&ScrollTrigger.update());
    if(hasGsap){gsap.ticker.add(t=>lenis.raf(t*1000));gsap.ticker.lagSmoothing(0)}
    else{const raf=t=>{lenis.raf(t);requestAnimationFrame(raf)};requestAnimationFrame(raf)}
  }

  /* nav hide/show */
  const nav=d.querySelector('.nav');let lastY=0;
  const onScroll=()=>{const y=window.scrollY;nav.classList.toggle('scrolled',y>10);
    if(!d.body.classList.contains('menu-open')&&!d.querySelector('.mega.open'))nav.classList.toggle('hide',y>lastY&&y>400);lastY=y};
  window.addEventListener('scroll',onScroll,{passive:true});

  /* mega menu */
  const scrim=d.querySelector('.mega-scrim');let closeT;
  d.querySelectorAll('.has-mega').forEach(h=>{
    const id=h.dataset.mega, m=d.getElementById(id);if(!m)return;
    const open=()=>{clearTimeout(closeT);d.querySelectorAll('.mega.open').forEach(x=>x!==m&&x.classList.remove('open'));m.classList.add('open');scrim.classList.add('on')};
    const close=()=>{closeT=setTimeout(()=>{m.classList.remove('open');scrim.classList.remove('on')},180)};
    h.addEventListener('mouseenter',open);h.addEventListener('mouseleave',close);
    m.addEventListener('mouseenter',()=>clearTimeout(closeT));m.addEventListener('mouseleave',close);
    const imgs=m.querySelectorAll('.mega-media img');
    m.querySelectorAll('.mega-list a').forEach((a,i)=>a.addEventListener('mouseenter',()=>{imgs.forEach((im,j)=>im.classList.toggle('on',i===j))}));
  });

  /* mobile menu */
  const burger=d.querySelector('.burger');
  burger&&burger.addEventListener('click',()=>{d.body.classList.toggle('menu-open');nav.classList.remove('hide');lenis&&(d.body.classList.contains('menu-open')?lenis.stop():lenis.start())});

  /* loader (home, once per session) */
  const loader=d.querySelector('.loader');
  let seen=false;try{seen=sessionStorage.getItem('elcon-loaded')==='1'}catch(e){}
  const startPage=()=>{d.dispatchEvent(new Event('page:start'))};
  if(loader&&hasGsap&&!reduce&&!seen){
    try{sessionStorage.setItem('elcon-loaded','1')}catch(e){}
    lenis&&lenis.stop();
    const tl=gsap.timeline({onComplete:()=>{loader.remove();lenis&&lenis.start();}});
    tl.to('.loader img',{opacity:1,y:0,duration:.8,ease:'expo.out'})
      .to('.loader .bar i',{scaleX:1,duration:.9,ease:'power2.inOut'},'-=.4')
      .to('.loader img,.loader .bar',{opacity:0,y:-12,duration:.4,ease:'power2.in'})
      .to(loader,{clipPath:'inset(0 0 100% 0)',duration:.9,ease:'expo.inOut'},'-=.1')
      .add(startPage,'-=.55');
  } else { loader&&loader.remove(); requestAnimationFrame(startPage); }

  /* split headings into lines */
  function splitLines(el){
    const words=el.textContent.trim().split(/\s+/);
    const color=[...el.querySelectorAll('[data-c]')].map(s=>s.textContent.trim());
    el.innerHTML=words.map(w=>`<span class="sw" style="display:inline-block">${w}</span>`).join(' ');
    // recolor accent words
    if(color.length){const set=color.join(' ').split(/\s+/);el.querySelectorAll('.sw').forEach(s=>{if(set.includes(s.textContent))s.classList.add('blue')})}
    const lines=[];let top=null,cur=[];
    el.querySelectorAll('.sw').forEach(s=>{const t=s.offsetTop;if(top===null||Math.abs(t-top)>4){if(cur.length)lines.push(cur);cur=[];top=t}cur.push(s)});
    if(cur.length)lines.push(cur);
    el.innerHTML=lines.map(l=>`<span class="split-line"><span>${l.map(s=>s.outerHTML).join(' ')}</span></span>`).join('');
    return el.querySelectorAll('.split-line>span');
  }

  d.addEventListener('page:start',()=>{
    if(!hasGsap||reduce){d.querySelectorAll('[data-reveal]').forEach(e=>{e.style.opacity=1;e.style.transform='none'});initStatic();return}
    d.querySelectorAll('[data-split]').forEach(el=>{
      const inner=splitLines(el);
      gsap.from(inner,{yPercent:110,duration:1.15,ease:'expo.out',stagger:.08,delay:el.dataset.delay?+el.dataset.delay:0,
        scrollTrigger:el.hasAttribute('data-now')?null:{trigger:el,start:'top 88%'}});
    });
    d.querySelectorAll('[data-reveal]').forEach(el=>{
      gsap.to(el,{opacity:1,y:0,duration:1.1,ease:'expo.out',delay:el.dataset.delay?+el.dataset.delay:0,
        scrollTrigger:el.hasAttribute('data-now')?null:{trigger:el,start:'top 92%'}});
    });
    initMotion();initStatic();
  });

  function initMotion(){
    /* hero stage expands to full bleed */
    const stage=d.querySelector('.stage');
    if(stage){
      gsap.fromTo(stage,{clipPath:`inset(0 ${getComputedStyle(html).getPropertyValue('--g')} 0 ${getComputedStyle(html).getPropertyValue('--g')} round 12px)`},
        {clipPath:'inset(0 0px 0 0px round 0px)',ease:'none',scrollTrigger:{trigger:stage,start:'top 85%',end:'top 10%',scrub:true}});
    }
    d.querySelectorAll('.pimg').forEach(p=>{
      gsap.to(p,{clipPath:'inset(0 0px 0 0px round 0px)',ease:'none',scrollTrigger:{trigger:p,start:'top 85%',end:'top 15%',scrub:true}});
      const im=p.querySelector('img');gsap.fromTo(im,{yPercent:-6},{yPercent:6,ease:'none',scrollTrigger:{trigger:p,start:'top bottom',end:'bottom top',scrub:true}});
    });
    /* parallax inside frames */
    d.querySelectorAll('[data-parallax]').forEach(im=>{
      gsap.fromTo(im,{yPercent:-7},{yPercent:7,ease:'none',scrollTrigger:{trigger:im.parentElement,start:'top bottom',end:'bottom top',scrub:true}});
    });
    /* scrub words */
    d.querySelectorAll('.scrub').forEach(el=>{
      const parts=el.innerHTML.split(/(\s+|<[^>]+>)/).filter(Boolean);
      let open=false;el.innerHTML=parts.map(p=>{if(p.startsWith('<')){return p}if(/^\s+$/.test(p))return p;return `<span class="w">${p}</span>`}).join('');
      gsap.to(el.querySelectorAll('.w'),{opacity:1,stagger:.05,ease:'none',scrollTrigger:{trigger:el,start:'top 80%',end:'bottom 45%',scrub:true}});
    });
    /* count up */
    d.querySelectorAll('[data-count]').forEach(el=>{
      const end=+el.dataset.count, fmt=el.dataset.fmt==='plain'?(v=>String(Math.round(v))):(v=>Math.round(v).toLocaleString('en-US'));
      const o={v:el.dataset.from?+el.dataset.from:0};el.textContent=fmt(o.v);
      gsap.to(o,{v:end,duration:2.2,ease:'power3.out',onUpdate:()=>el.textContent=fmt(o.v),onComplete:()=>el.textContent=fmt(end),scrollTrigger:{trigger:el,start:'top 88%',once:true}});
    });
    /* process pin */
    const proc=d.querySelector('.proc');
    if(proc&&isDesk()){
      const steps=proc.querySelectorAll('.proc-step'), imgs=proc.querySelectorAll('.proc-r img'), bars=proc.querySelectorAll('.proc-bar b');const n=steps.length;
      let cur=-1;const set=i=>{if(i===cur)return;cur=i;steps.forEach((s,j)=>s.classList.toggle('on',j===i));imgs.forEach((s,j)=>s.classList.toggle('on',j===i))};
      set(0);
      ScrollTrigger.create({trigger:proc,start:'top top',end:()=>'+='+window.innerHeight*n*.7,pin:true,scrub:true,
        onUpdate:self=>{const p=self.progress*n;const i=Math.min(n-1,Math.floor(p));set(i);bars.forEach((b,j)=>gsap.set(b,{scaleX:Math.max(0,Math.min(1,p-j))}))}});
    }
    /* cases horizontal */
    const cases=d.querySelector('.cases');
    if(cases&&isDesk()){
      const track=cases.querySelector('.cases-track');const cnt=d.querySelector('.cases-count b');const items=track.querySelectorAll('.case');
      const dist=()=>track.scrollWidth-window.innerWidth;
      gsap.to(track,{x:()=>-dist(),ease:'none',scrollTrigger:{trigger:cases,start:()=>'top '+(d.querySelector('.cases-head').offsetHeight+parseFloat(getComputedStyle(html).getPropertyValue('--nav-h'))+30),end:()=>'+='+dist(),pin:'.cases-pin',scrub:.6,invalidateOnRefresh:true,
        onUpdate:s=>{if(cnt)cnt.textContent=String(Math.min(items.length,Math.floor(s.progress*(items.length-.001))+1)).padStart(2,'0')}}});
      track.querySelectorAll('.ph img').forEach(im=>gsap.fromTo(im,{xPercent:-6},{xPercent:6,ease:'none',scrollTrigger:{trigger:cases,start:'top top',end:()=>'+='+dist(),scrub:true}}));
    }
  }

  function initStatic(){
    /* hero slideshow */
    const stage=d.querySelector('.stage');
    if(stage){
      const slides=stage.querySelectorAll('.slide'), dots=stage.querySelectorAll('.stage-dots button'), cap=stage.querySelector('.stage-cap');let i=0,t;
      const go=n=>{i=(n+slides.length)%slides.length;slides.forEach((s,j)=>s.classList.toggle('on',j===i));dots.forEach((b,j)=>{b.classList.remove('on');void b.offsetWidth;b.classList.toggle('on',j===i)});
        if(cap){cap.style.opacity=0;setTimeout(()=>{cap.textContent=slides[i].dataset.cap;cap.style.opacity=1},350)}
        clearTimeout(t);t=setTimeout(()=>go(i+1),5500)};
      dots.forEach((b,j)=>b.addEventListener('click',()=>go(j)));go(0);
    }
    /* accordion */
    d.querySelectorAll('.accordion').forEach(a=>{const it=a.querySelectorAll('.acc');it.forEach(x=>{
      x.addEventListener('mouseenter',()=>{if(!isDesk())return;it.forEach(y=>y.classList.toggle('on',y===x))});
      x.addEventListener('focusin',()=>it.forEach(y=>y.classList.toggle('on',y===x)));})});
    /* testimonials */
    const tq=d.querySelectorAll('.testi-q blockquote'), tp=d.querySelectorAll('.person');
    if(tq.length){let i=0,tw;const go=n=>{i=n%tq.length;tq.forEach((q,j)=>q.classList.toggle('on',j===i));tp.forEach((p,j)=>p.classList.toggle('on',j===i));
      if(hasGsap){tw&&tw.kill();d.querySelectorAll('.person .prog').forEach(p=>gsap.set(p,{scaleX:0}));tw=gsap.to(tp[i].querySelector('.prog'),{scaleX:1,duration:9,ease:'none',onComplete:()=>go(i+1)})}};
      tp.forEach((p,j)=>p.addEventListener('click',()=>go(j)));go(0)}
    /* references filter */
    d.querySelectorAll('.refs-search').forEach(inp=>{const rows=d.querySelectorAll('.refs tbody tr');const c=d.querySelector('.refs-n');
      inp.addEventListener('input',()=>{const q=inp.value.toLowerCase().trim();let n=0;rows.forEach(r=>{const h=q&&!r.textContent.toLowerCase().includes(q);r.classList.toggle('hide',h);if(!h)n++});if(c)c.textContent=n;lenis&&ScrollTrigger.refresh()})});
    /* contact form -> mailto */
    d.querySelectorAll('form.f').forEach(f=>f.addEventListener('submit',e=>{e.preventDefault();const fd=new FormData(f);
      const body=[...fd.entries()].map(([k,v])=>`${k}: ${v}`).join('\n');
      window.location.href=`mailto:info@elcon.si?subject=${encodeURIComponent('Free call request: '+(fd.get('Company')||''))}&body=${encodeURIComponent(body)}`;
      f.style.display='none';const done=f.nextElementSibling;if(done)done.style.display='block'}));
    if(hasGsap) window.addEventListener('load',()=>ScrollTrigger.refresh());
  }
})();
