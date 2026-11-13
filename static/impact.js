(() => {
const esc = s => String(s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
try { if (new URLSearchParams(location.search).get("test") === "1") sessionStorage.setItem("dansh_test", "1"); } catch (_) {}
const f = v => v === null || v === undefined ? "–" : v + "%";
function ts(x){ if(!x) return "–"; const d=new Date(x*1000); return d.toLocaleString(undefined,{dateStyle:"medium",timeStyle:"short"}); }
async function load(){
  const r = await fetch("/api/impact", {cache:"no-store"}); const j = await r.json(); const L = j.learn;
  const out = document.getElementById("out");
  if (!L.completed) {
    out.innerHTML = `<div class="empty"><b>No completed checks yet.</b> Be the first: <a href="/check">take the 3-minute check</a>, then share it.</div>`;
    return;
  }
  const rows = Object.values(L.per_concept).map(c => `<tr><td><b>${esc(c.label_en)}</b><br><small>${esc(c.label_hi)}</small></td>
    <td>${f(c.correct_pre_pct)} → <b>${f(c.correct_post_pct)}</b></td>
    <td><div class="bar"><i class="pre" style="width:${c.correct_pre_pct||0}%;height:6px"></i><i class="post" style="width:${c.correct_post_pct||0}%;height:6px"></i></div></td>
    <td>${f(c.dangerous_pre_pct)} → <b>${f(c.dangerous_post_pct)}</b></td></tr>`).join("");
  const kv = o => Object.entries(o).sort((a,b)=>b[1]-a[1]).map(([k,v])=>`${esc(k)}: ${v}`).join(" · ") || "–";
  out.innerHTML = `
  <div class="big">
    <div><small>People who completed the check · जाँच पूरी की</small><b>${L.completed}</b><small>${L.unique_devices} devices · ${L.started} started</small></div>
    <div><small>Chose at least one dangerous action · कम से कम एक ख़तरनाक जवाब</small><b>${f(L.chose_dangerous_action_pre_pct)} <span class="arrow">→</span> ${f(L.chose_dangerous_action_post_pct)}</b><small>before → after the lesson${L.chose_dangerous_action_pre_ci95 ? ` · 95% CI ${L.chose_dangerous_action_pre_ci95.join("–")}% → ${L.chose_dangerous_action_post_ci95.join("–")}%` : ""}</small></div>
    <div><small>Average score · औसत स्कोर</small><b>${f(L.mean_score_pre_pct)} <span class="arrow">→</span> ${f(L.mean_score_post_pct)}</b><small>before → after</small></div>
    <div><small>Improved / same / worse</small><b>${L.improved} / ${L.same} / ${L.worse}</b><small>${L.shared} shared it onward</small></div>
  </div>
  <div class="card"><h2>By decision</h2>
  <p class="legend"><span><i style="background:#c9b48a"></i>before</span><span><i style="background:var(--leaf)"></i>after</span></p>
  <div class="tablewrap"><table><thead><tr><th>Decision</th><th>Correct</th><th></th><th>Dangerous choice</th></tr></thead><tbody>${rows}</tbody></table></div></div>
  <div class="card"><h2>Who took it</h2>
  <p><b>Language:</b> ${kv(L.by_lang)}<br><b>State (self-reported, optional):</b> ${kv(L.by_state)}<br><b>Role (optional):</b> ${kv(L.by_role)}<br>
  <b>Question-set order:</b> ${kv(L.by_form_order)}<br><b>By campaign link (src):</b> ${Object.entries((L.breakdown||{}).src||{}).map(([k,v])=>`${esc(k)}: n=${v.n}, dangerous ${f(v.dangerous_pre_pct)}→${f(v.dangerous_post_pct)}`).join(" · ") || "–"}<br><b>By order:</b> ${Object.entries((L.breakdown||{}).order||{}).map(([k,v])=>`${esc(k)}: n=${v.n}, score ${f(v.score_pre_pct)}→${f(v.score_post_pct)}`).join(" · ") || "–"}<br><b>Not counted (excluded):</b> ${kv(L.excluded || {})}<br><b>First / latest:</b> ${ts(L.first_completed_at)} / ${ts(L.last_completed_at)}</p>
  <p class="understood">Emergency-agent uses: ${j.consults.total} (${esc(j.consults.note)})</p></div>`;
}
load().catch(()=>{document.getElementById("out").innerHTML="<p>Could not load numbers.</p>"});
setInterval(()=>load().catch(()=>{}), 60000);
})();