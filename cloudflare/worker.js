const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
};

function json(data, status = 200) {
  return new Response(JSON.stringify(data, null, 2), {
    status,
    headers: {
      ...corsHeaders,
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store",
    },
  });
}

function text(data, status = 200) {
  return new Response(data, {
    status,
    headers: {
      ...corsHeaders,
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "no-store",
    },
  });
}

function uploadName(payload) {
  const kind = payload && payload.kind === "walk" ? "walk" : "motion";
  const stamp = new Date().toISOString().replace(/[-:.TZ]/g, "").slice(0, 14);
  const rand = crypto.randomUUID().slice(0, 8);
  return `${kind}_${stamp}_${rand}.json`;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders });
    }

    if (url.pathname === "/health") {
      return json({ ok: true, service: "phone-motion-tracker-upload" });
    }

    if (url.pathname === "/upload" && request.method === "POST") {
      if (!env.MOTION_UPLOADS) {
        return text("MOTION_UPLOADS KV binding is missing", 500);
      }

      const contentType = request.headers.get("Content-Type") || "";
      if (!contentType.includes("application/json")) {
        return text("Expected application/json", 415);
      }

      const bodyText = await request.text();
      if (bodyText.length > 10 * 1024 * 1024) {
        return text("Upload too large", 413);
      }

      let payload;
      try {
        payload = JSON.parse(bodyText);
      } catch {
        return text("Invalid JSON", 400);
      }

      const name = uploadName(payload);
      await env.MOTION_UPLOADS.put(name, bodyText, {
        metadata: {
          kind: payload.kind || "motion",
          samples: payload.samples ? payload.samples.length : 0,
          createdAt: new Date().toISOString(),
        },
      });

      return text(name);
    }

    if (url.pathname === "/uploads" && request.method === "GET") {
      if (!env.MOTION_UPLOADS) {
        return json({ error: "MOTION_UPLOADS KV binding is missing" }, 500);
      }
      const list = await env.MOTION_UPLOADS.list({ limit: 100 });
      return json({ uploads: list.keys });
    }

    // Public share viewer: /view/<name> renders an HTML page that loads the
    // recording from /uploads/<name> and visualizes it.
    if (url.pathname.startsWith("/view/") && request.method === "GET") {
      const name = decodeURIComponent(url.pathname.slice("/view/".length));
      return new Response(viewerHtml(name), {
        headers: { ...corsHeaders, "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store" },
      });
    }

    if (url.pathname.startsWith("/uploads/") && request.method === "GET") {
      if (!env.MOTION_UPLOADS) {
        return json({ error: "MOTION_UPLOADS KV binding is missing" }, 500);
      }
      const name = decodeURIComponent(url.pathname.slice("/uploads/".length));
      const value = await env.MOTION_UPLOADS.get(name);
      if (!value) return text("not found", 404);
      return new Response(value, {
        headers: {
          ...corsHeaders,
          "Content-Type": "application/json; charset=utf-8",
          "Cache-Control": "no-store",
        },
      });
    }

    return text("not found", 404);
  },
};

// Self-contained share viewer. Renders walk_dual / walk / gesture payloads:
// dual-foot ground path with step playback + the gait feature table.
function viewerHtml(name) {
  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Gait session — ${name.replace(/[<>&"]/g, "")}</title>
<style>
  :root{--bg:#0b0e14;--panel:#141a24;--line:#2a3445;--txt:#e6edf3;--mut:#8b98a9;--l:#4cc2ff;--r:#f0883e;--good:#3fb950;}
  body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:var(--bg);color:var(--txt);margin:0;padding:16px;display:flex;justify-content:center;}
  .wrap{width:100%;max-width:560px;}
  h1{font-size:1.25rem;margin:.2rem 0;}
  .mut{color:var(--mut);font-size:.85rem;}
  .card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px;margin:12px 0;}
  canvas{width:100%;border-radius:8px;background:#0e131c;touch-action:none;}
  button{font-size:.95rem;padding:8px 14px;border:none;border-radius:8px;background:var(--l);color:#06202e;font-weight:700;cursor:pointer;}
  button.ghost{background:#1b2330;color:var(--txt);border:1px solid var(--line);}
  table{width:100%;border-collapse:collapse;font-size:.85rem;}
  td,th{padding:5px 4px;border-bottom:1px solid #1b2330;text-align:right;}
  td:first-child,th:first-child{text-align:left;color:var(--mut);}
  th{color:var(--mut);font-weight:600;}
  th.l{color:var(--l)} th.r{color:var(--r)}
  td.sym{color:var(--good);}
  .legend{font-size:.8rem;margin-top:6px;}
  .legend b.l{color:var(--l)} .legend b.r{color:var(--r)}
  .row{display:flex;gap:8px;align-items:center;margin-top:8px;}
  .err{color:#ff7b72;}
</style>
</head>
<body>
<div class="wrap">
  <h1>Gait session</h1>
  <div class="mut" id="meta">Loading ${name.replace(/[<>&"]/g, "")}…</div>
  <div class="card">
    <canvas id="cv" width="640" height="480"></canvas>
    <div class="row">
      <button id="play">▶ Simulate steps</button>
      <span class="mut" id="clock"></span>
      <span class="legend" style="margin-left:auto"><b class="l">● Left</b> &nbsp;<b class="r">● Right</b></span>
    </div>
  </div>
  <div class="card">
    <table id="tbl"><tbody></tbody></table>
  </div>
  <div class="mut">Recorded with StrideSense XIAO foot pods · shared via Cloudflare Workers</div>
</div>
<script>
const NAME = ${JSON.stringify(name)};
const cv = document.getElementById('cv'), ctx = cv.getContext('2d');
const fmtN = (v, d=2) => (typeof v === 'number' && isFinite(v)) ? v.toFixed(d) : '--';
const sym = (a,b) => (isFinite(a)&&isFinite(b)&&(a+b)) ? (Math.abs(a-b)/((a+b)/2)*100).toFixed(0)+'%' : '';

function alignHeading(points){
  let i = 1;
  while (i < points.length && Math.hypot(points[i].x, points[i].y) < 0.3) i++;
  if (i >= points.length) return points;
  const a = Math.atan2(points[i].x, points[i].y), c = Math.cos(a), s = Math.sin(a);
  return points.map(p => ({x: p.x*c - p.y*s, y: p.x*s + p.y*c, z: p.z}));
}
function normalizeFeet(d){
  const feet = [];
  const asPts = (p) => !p ? [] : alignHeading((p.points || p).map(q => Array.isArray(q) ? {x:q[0],y:q[1],z:q[2]} : q));
  const asT = (p) => (p && p.times) ? p.times : null;
  if (d.kind === 'walk_dual') {
    feet.push({side:'L', color:'#4cc2ff', pts:asPts(d.left?.path), t:asT(d.left?.path), sum:d.left?.summary||{}});
    feet.push({side:'R', color:'#f0883e', pts:asPts(d.right?.path), t:asT(d.right?.path), sum:d.right?.summary||{}});
  } else if (d.kind === 'gesture_dual') {
    feet.push({side:'L', color:'#4cc2ff', pts:asPts(d.left?.samples), t:null, sum:{}});
    feet.push({side:'R', color:'#f0883e', pts:asPts(d.right?.samples), t:null, sum:{}});
  } else if (d.kind === 'walk') {
    feet.push({side:'L', color:'#4cc2ff', pts:asPts(d.path), t:asT(d.path), sum:d.summary||{}});
  } else {
    feet.push({side:'L', color:'#4cc2ff', pts:asPts(d.samples), t:null, sum:{}});
  }
  return feet.filter(f => f.pts.length);
}

let feet = [], simT = null, maxT = 0, timer = null;

function draw(){
  ctx.clearRect(0,0,cv.width,cv.height);
  let mnx=-0.1,mxx=0.1,mny=-0.1,mxy=0.1;
  for(const f of feet) for(const p of f.pts){ mnx=Math.min(mnx,p.x);mxx=Math.max(mxx,p.x);mny=Math.min(mny,p.y);mxy=Math.max(mxy,p.y);}
  const span=Math.max(mxx-mnx,mxy-mny,0.3), sc=(Math.min(cv.width,cv.height)-60)/span;
  const cx=(mnx+mxx)/2, cy=(mny+mxy)/2;
  const S=p=>[cv.width/2+(p.x-cx)*sc, cv.height/2-(p.y-cy)*sc];
  for(const f of feet){
    let pts=f.pts;
    if(simT!=null && f.t){ let n=1; while(n<pts.length && f.t[n]<=simT) n++; pts=pts.slice(0,n); }
    if(pts.length<2) continue;
    ctx.beginPath(); ctx.strokeStyle=f.color; ctx.lineWidth=3; ctx.lineJoin='round';
    const [x0,y0]=S(pts[0]); ctx.moveTo(x0,y0);
    for(let i=1;i<pts.length;i++){ const [x,y]=S(pts[i]); ctx.lineTo(x,y);}
    ctx.stroke();
    const [xs,ys]=S(pts[0]); ctx.fillStyle='#3fb950'; ctx.beginPath(); ctx.arc(xs,ys,5,0,7); ctx.fill();
    const [xe,ye]=S(pts[pts.length-1]);
    ctx.fillStyle=simT!=null?f.color:'#e6edf3'; ctx.beginPath(); ctx.arc(xe,ye,simT!=null?8:5,0,7); ctx.fill();
    if(simT!=null){ ctx.strokeStyle='#e6edf3'; ctx.lineWidth=1.5; ctx.stroke(); }
  }
}

document.getElementById('play').onclick = () => {
  if (timer) { clearInterval(timer); timer=null; simT=null; document.getElementById('play').textContent='▶ Simulate steps'; document.getElementById('clock').textContent=''; draw(); return; }
  simT = 0;
  document.getElementById('play').textContent='■ Stop';
  timer = setInterval(() => {
    simT += 0.1;
    document.getElementById('clock').textContent = 't = '+simT.toFixed(1)+'s / '+maxT.toFixed(1)+'s';
    if (simT >= maxT) { clearInterval(timer); timer=null; simT=null; document.getElementById('play').textContent='▶ Simulate steps'; }
    draw();
  }, 50);
};

function row(label, l, r, s){ return '<tr><td>'+label+'</td><td>'+l+'</td><td>'+r+'</td><td class="sym">'+(s||'')+'</td></tr>'; }
function single(label, v){ return '<tr><td>'+label+'</td><td colspan="3" style="text-align:right">'+v+'</td></tr>'; }

function table(feet){
  const L = feet.find(f=>f.side==='L')?.sum||{}, R = feet.find(f=>f.side==='R')?.sum||{};
  const avg=(a,b)=>{const v=[a,b].filter(x=>isFinite(x));return v.length?v.reduce((s,x)=>s+x,0)/v.length:NaN;};
  let h = '<tr><th></th><th class="l">Left</th><th class="r">Right</th><th>Sym%</th></tr>';
  h += single('1· Walking speed (m/s)', fmtN(avg(L.speed,R.speed)));
  h += row('2· Stride height (cm)', fmtN(L.clearance*100,1), fmtN(R.clearance*100,1), sym(L.clearance,R.clearance));
  h += row('3· Stride length (m)', fmtN(L.strideLengthMean), fmtN(R.strideLengthMean), sym(L.strideLengthMean,R.strideLengthMean));
  h += row('4· Landing position', L.landingPosition||'--', R.landingPosition||'--', '');
  h += row('5· Path distance (m)', fmtN(L.distanceM), fmtN(R.distanceM), sym(L.distanceM,R.distanceM));
  h += row('6· Leg speed (mm/s)', fmtN(L.avgFootVelocity,0), fmtN(R.avgFootVelocity,0), sym(L.avgFootVelocity,R.avgFootVelocity));
  h += single('7· Speed diff L–R (m/s)', (isFinite(L.speed)&&isFinite(R.speed))?fmtN(Math.abs(L.speed-R.speed),3):'--');
  h += row('8· Foot orientation (° HS/TO)', fmtN(L.pitchHSMean,0)+'/'+fmtN(L.pitchTOMean,0), fmtN(R.pitchHSMean,0)+'/'+fmtN(R.pitchTOMean,0), '');
  h += single('9· Cadence (steps/min)', fmtN(avg(L.cadence*2,R.cadence*2),0));
  h += row('10· Swing time (s)', fmtN(L.swingTimeMean,3), fmtN(R.swingTimeMean,3), sym(L.swingTimeMean,R.swingTimeMean));
  h += row('11· Stance time (s)', fmtN(L.stanceTimeMean), fmtN(R.stanceTimeMean), sym(L.stanceTimeMean,R.stanceTimeMean));
  document.querySelector('#tbl tbody').innerHTML = h;
}

fetch('/uploads/'+encodeURIComponent(NAME)).then(r => {
  if (!r.ok) throw new Error('HTTP '+r.status);
  return r.json();
}).then(d => {
  feet = normalizeFeet(d);
  for (const f of feet) if (f.t && f.t.length) maxT = Math.max(maxT, f.t[f.t.length-1]);
  document.getElementById('meta').textContent = (d.kind||'session')+' · '+NAME;
  if (!feet.some(f=>f.t)) document.getElementById('play').style.display='none';
  table(feet);
  draw();
}).catch(e => {
  document.getElementById('meta').innerHTML = '<span class="err">Could not load recording: '+e.message+'</span>';
});
</script>
</body>
</html>`;
}
