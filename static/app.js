(() => {
"use strict";
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const params = new URLSearchParams(location.search);
function ss(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (_) { return null; } }
if (params.get("test") === "1") ss("dansh_test", "1");
if (params.get("test") === "0") ss("dansh_test", "0");
const TEST = ss("dansh_test") === "1";
const SRC = (params.get("src") || "").slice(0, 24);
const GH = "https://github.com/";  // replaced at build time by REPO_URL below if set
const REPO_URL = document.documentElement.dataset.repo || "";

const T = {
  en: {
    tab_help: "Bitten now", tab_check: "3-min check", tab_impact: "Impact",
    callbar: "Snakebite? Call 108 now (free ambulance)",
    help_h: "Someone was bitten by a snake?",
    help_lede: "Tell me what happened, in Hindi or English. I'll give you the steps from the Government of India's snakebite guidelines.",
    msg_label: "What happened?", msg_ph: "e.g. snake bit my father on the leg 10 minutes ago, we tied a rope",
    send: "Tell me what to do", speak: "Speak", thinking: "Checking…",
    ex1: "Snake bit my father on the leg 10 min ago, we tied a rope",
    ex2: "Child slept on the floor, woke up vomiting, eyes drooping",
    ex3: "Something bit me in the field, not sure what",
    disclaimer: "Dansh is not a doctor and does not diagnose. It only repeats the first-aid steps in the Ministry of Health's Standard Treatment Guidelines (2017). Every snakebite needs a hospital.",
    do_h: "Do this now", dont_h: "Do NOT do this", fix_h: "About what was already done", ask_h: "Answer these quickly (it changes the advice)",
    yes: "Yes", no: "No", understood: "I understood these danger signs:",
    hosp_h: "Nearest hospitals", hosp_btn: "📍 Find hospitals near me", hosp_wait: "Finding hospitals near you…",
    hosp_none: "Couldn't load nearby hospitals. Use the map search instead:", hosp_map: "Open map: government hospital near me",
    hosp_note: "Prefer a government district hospital or CHC: they keep antivenom (ASV). Call ahead if you can.",
    hosp_denied: "Location is off. Use the map search instead:", directions: "Directions", call: "Call",
    why: "Why this advice? (rules and sources)", source: "source", page: "p.",
    check_h: "Would you know what to do?",
    check_lede: "Snakebite kills thousands of people in India every year, most of them farmers, labourers and children in villages. Many die before reaching a hospital. Doing the right thing in the first hour saves lives. Answer 6 quick questions, learn the answers, then try 6 more.",
    check_f1: "About 3 minutes", check_f2: "No name, no phone number",
    check_f3: "Your answers are added anonymously to the public impact numbers",
    state_q: "Your state (optional)", role_q: "You are (optional)", skip: "Skip",
    r_farmer: "Farmer / farm worker", r_student: "Student", r_health: "ASHA / health worker", r_teacher: "Teacher",
    r_parent: "Parent", r_other: "Other", start: "Start the check",
    phase_pre: "Part 1 of 3 · What would you do?", phase_lesson: "Part 2 of 3 · The right answers",
    phase_post: "Part 3 of 3 · Try again", q_of: "Question {i} of {n}",
    lesson_lede: "You got {c} of {n} right. Here is what the Government of India guidelines say, starting with the ones you missed.",
    missed: "You missed this", next_part: "I've read these, continue",
    result_h: "Your result", before: "Before", after: "After",
    danger_before: "Dangerous choices before: {d}", danger_after: "Dangerous choices after: {d}",
    review_h: "Remember these", perfect: "Perfect. You know what to do.",
    share_h: "One share can save a life. Send this to your family group:",
    share_wa: "Share on WhatsApp", share_copy: "Copy link", copied: "Copied!",
    share_text: "Would you know what to do if a snake bit someone in your family? Tying a rope or going to an ojha can cost a life. I took this free 3-minute check (Hindi/English): ",
    see_impact: "See how everyone is doing →", again: "Back to emergency help",
    test_banner: "Test mode: nothing you do here is counted in the impact numbers.",
    err: "Something went wrong. If someone was bitten: call 108 and go to the nearest government hospital now.",
    foot1: "Free and open source (MIT).", foot_src: "Source: MoHFW guidelines",
  },
  hi: {
    tab_help: "मदद", tab_check: "जाँच", tab_impact: "असर",
    callbar: "साँप ने काटा? अभी 108 पर फ़ोन करें (मुफ़्त एम्बुलेंस)",
    help_h: "किसी को साँप ने काटा है?",
    help_lede: "बताइए क्या हुआ, हिंदी या अंग्रेज़ी में। मैं भारत सरकार की सर्पदंश गाइडलाइन के कदम बताऊँगा।",
    msg_label: "क्या हुआ?", msg_ph: "जैसे: पापा को 10 मिनट पहले पैर में साँप ने काटा, रस्सी बाँध दी है",
    send: "बताइए क्या करें", speak: "बोलें", thinking: "देख रहे हैं…",
    ex1: "पापा को 10 मिनट पहले पैर में साँप ने काटा, रस्सी बाँध दी",
    ex2: "बच्चा ज़मीन पर सोया था, उल्टी हो रही है, पलकें झुक रही हैं",
    ex3: "खेत में कुछ ने काटा, पता नहीं क्या था",
    disclaimer: "दंश डॉक्टर नहीं है और कोई निदान नहीं करता। यह सिर्फ़ स्वास्थ्य मंत्रालय की स्टैंडर्ड ट्रीटमेंट गाइडलाइन (2017) के प्राथमिक उपचार के कदम बताता है। हर सर्पदंश में अस्पताल ज़रूरी है।",
    do_h: "अभी यह करें", dont_h: "यह बिल्कुल न करें", fix_h: "जो पहले हो चुका है उसके बारे में", ask_h: "जल्दी जवाब दें (इससे सलाह बदलती है)",
    yes: "हाँ", no: "नहीं", understood: "ये ख़तरे के लक्षण समझ आए:",
    hosp_h: "नज़दीकी अस्पताल", hosp_btn: "📍 मेरे पास के अस्पताल दिखाएँ", hosp_wait: "पास के अस्पताल ढूँढ रहे हैं…",
    hosp_none: "पास के अस्पताल लोड नहीं हुए। मैप में खोजें:", hosp_map: "मैप खोलें: पास का सरकारी अस्पताल",
    hosp_note: "सरकारी ज़िला अस्पताल या CHC चुनें: वहाँ एंटीवेनम (ASV) रहता है। हो सके तो पहले फ़ोन कर लें।",
    hosp_denied: "लोकेशन बंद है। मैप में खोजें:", directions: "रास्ता", call: "फ़ोन",
    why: "यह सलाह क्यों? (नियम और स्रोत)", source: "स्रोत", page: "पृ.",
    check_h: "क्या आप जानते हैं क्या करना है?",
    check_lede: "भारत में हर साल हज़ारों लोग सर्पदंश से मरते हैं, ज़्यादातर गाँव के किसान, मज़दूर और बच्चे। कई अस्पताल पहुँचने से पहले ही दम तोड़ देते हैं। पहले घंटे में सही कदम जान बचाता है। 6 छोटे सवालों के जवाब दें, सही जवाब सीखें, फिर 6 और सवाल।",
    check_f1: "लगभग 3 मिनट", check_f2: "कोई नाम नहीं, कोई फ़ोन नंबर नहीं",
    check_f3: "आपके जवाब बिना पहचान के सार्वजनिक असर के आँकड़ों में जुड़ते हैं",
    state_q: "आपका राज्य (वैकल्पिक)", role_q: "आप हैं (वैकल्पिक)", skip: "छोड़ें",
    r_farmer: "किसान / खेत मज़दूर", r_student: "विद्यार्थी", r_health: "आशा / स्वास्थ्य कार्यकर्ता", r_teacher: "शिक्षक",
    r_parent: "माता-पिता", r_other: "अन्य", start: "जाँच शुरू करें",
    phase_pre: "भाग 1/3 · आप क्या करेंगे?", phase_lesson: "भाग 2/3 · सही जवाब", phase_post: "भाग 3/3 · फिर से कोशिश",
    q_of: "सवाल {i} / {n}",
    lesson_lede: "आपके {n} में से {c} सही थे। भारत सरकार की गाइडलाइन यह कहती है, पहले वे जो आपसे छूटे।",
    missed: "यह छूटा", next_part: "पढ़ लिया, आगे चलें",
    result_h: "आपका नतीजा", before: "पहले", after: "बाद में",
    danger_before: "पहले ख़तरनाक जवाब: {d}", danger_after: "बाद में ख़तरनाक जवाब: {d}",
    review_h: "ये याद रखें", perfect: "बहुत बढ़िया। आपको पता है क्या करना है।",
    share_h: "एक शेयर किसी की जान बचा सकता है। अपने परिवार के ग्रुप में भेजें:",
    share_wa: "WhatsApp पर भेजें", share_copy: "लिंक कॉपी करें", copied: "कॉपी हो गया!",
    share_text: "अगर घर में किसी को साँप काट ले तो क्या आपको पता है क्या करना है? रस्सी बाँधना या ओझा के पास जाना जान ले सकता है। मैंने यह मुफ़्त 3 मिनट की जाँच की (हिंदी/English): ",
    see_impact: "सबका नतीजा देखें →", again: "आपात मदद पर वापस",
    test_banner: "टेस्ट मोड: यहाँ जो भी करेंगे, असर के आँकड़ों में नहीं गिना जाएगा।",
    err: "कुछ गड़बड़ हुई। अगर किसी को साँप ने काटा है: 108 पर फ़ोन करें और अभी नज़दीकी सरकारी अस्पताल जाएँ।",
    foot1: "मुफ़्त और ओपन सोर्स (MIT)।", foot_src: "स्रोत: स्वास्थ्य मंत्रालय गाइडलाइन",
  },
};
const STATES = ["Andhra Pradesh","Arunachal Pradesh","Assam","Bihar","Chhattisgarh","Delhi","Goa","Gujarat","Haryana",
  "Himachal Pradesh","Jammu and Kashmir","Jharkhand","Karnataka","Kerala","Ladakh","Madhya Pradesh","Maharashtra",
  "Manipur","Meghalaya","Mizoram","Nagaland","Odisha","Puducherry","Punjab","Rajasthan","Sikkim","Tamil Nadu",
  "Telangana","Tripura","Uttar Pradesh","Uttarakhand","West Bengal","Other UT","Outside India"];

function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (_) { return null; } }
let lang = store("dansh_lang") || ((navigator.language || "").startsWith("hi") ? "hi" : "en");
const t = (k, vars) => { let s = (T[lang] && T[lang][k]) || T.en[k] || k; if (vars) for (const [a, b] of Object.entries(vars)) s = s.replace("{" + a + "}", b); return s; };
const esc = s => String(s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));

async function api(path, body) {
  const headers = {"content-type": "application/json"};
  if (TEST) headers["x-dansh-test"] = "1";
  const r = await fetch(path, {method: body ? "POST" : "GET", headers, body: body ? JSON.stringify(body) : undefined});
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.error || r.status);
  return data;
}

function applyLang() {
  document.documentElement.lang = lang;
  $("#lang").textContent = lang === "hi" ? "English" : "हिंदी";
  $$("[data-i18n]").forEach(el => { el.textContent = t(el.dataset.i18n); });
  $$("[data-i18n-ph]").forEach(el => { el.placeholder = t(el.dataset.i18nPh); });
  $$(".chip").forEach(el => { el.textContent = t(el.dataset.ex); });
  if (lastPlanReq) runConsult(lastPlanReq.message, lastPlanReq.answered, true);
}
$("#lang").addEventListener("click", () => { lang = lang === "hi" ? "en" : "hi"; store("dansh_lang", lang); applyLang(); });

// --------------------------------------------------------------------------- tabs
function show(view) {
  $$(".view").forEach(v => v.hidden = v.id !== "view-" + view);
  $$(".tabs [role=tab]").forEach(b => b.setAttribute("aria-selected", String(b.dataset.view === view)));
  window.scrollTo(0, 0);
}
$$(".tabs [role=tab]").forEach(b => b.addEventListener("click", () => { show(b.dataset.view); history.replaceState(null, "", (b.dataset.view === "check" ? "/check" : "/") + location.search); }));

// --------------------------------------------------------------------------- emergency agent
let lastPlanReq = null;
function src(s) {
  if (!s) return "";
  const pg = s.page ? ` ${t("page")}${s.page}` : "";
  return ` <a class="src" href="${esc(s.url)}" target="_blank" rel="noopener" title="${esc(s.title)}">${esc(s.key)}${pg}</a>`;
}
function renderPlan(p) {
  const el = $("#plan");
  const calls = (p.calls || []).map((n, i) => `<a href="tel:${n}" class="${i ? "alt" : ""}">📞 ${n}</a>`).join("");
  let h = `<div class="level ${p.level}" role="alert">${p.level === "CRITICAL" ? "⚠️" : "🩺"} ${esc(p.title)}</div>`;
  if (calls) h += `<div class="calls">${calls}</div>`;
  if (p.understood && p.understood.length) h += `<p class="understood">${t("understood")} <b>${p.understood.map(esc).join(", ")}</b></p>`;
  if (p.ask && p.ask.length) {
    h += `<div class="card ask"><h2>${t("ask_h")}</h2>` + p.ask.map(a => `<div class="q"><span>${esc(a.q)}</span><span class="yn"><button class="yes" data-flag="${a.flag}" data-v="1">${t("yes")}</button><button data-flag="${a.flag}" data-v="0">${t("no")}</button></span></div>`).join("") + `</div>`;
  }
  h += p.notes.map(n => `<div class="note">${esc(n.text)}${src(n.source)}</div>`).join("");
  if (p.fixes.length) h += `<h2>${t("fix_h")}</h2>` + p.fixes.map(n => `<div class="fix">${esc(n.text)}${src(n.source)}</div>`).join("");
  if (p.do.length) h += `<div class="card"><h2>${t("do_h")}</h2><ol class="steps">${p.do.map(n => `<li>${esc(n.text)}${src(n.source)}</li>`).join("")}</ol></div>`;
  if (p.dont.length) h += `<div class="card"><h2>${t("dont_h")}</h2><ul class="donts">${p.dont.map(n => `<li>${esc(n.text)}${src(n.source)}</li>`).join("")}</ul></div>`;
  if (p.show_hospitals) h += `<div class="card hosp" id="hosp"><h2>${t("hosp_h")}</h2><p class="understood">${t("hosp_note")}</p><button class="primary" id="findh">${t("hosp_btn")}</button><div id="hlist"></div></div>`;
  h += `<details class="card"><summary>${t("why")}</summary><ul class="trace">${(p.rule_trace || []).map(r => `<li>${esc(r)}</li>`).join("")}<li>parser: ${esc(p.parser.used)}${p.parser.llm_model ? " (" + esc(p.parser.llm_model) + ")" : ""}, ${p.parser.ms} ms</li></ul></details>`;
  el.innerHTML = h;
  $$(".yn button", el).forEach(b => b.addEventListener("click", () => {
    const answered = Object.assign({}, lastPlanReq.answered, {[b.dataset.flag]: b.dataset.v === "1"});
    runConsult(lastPlanReq.message, answered);
  }));
  const fh = $("#findh"); if (fh) fh.addEventListener("click", findHospitals);
}
async function runConsult(message, answered = {}, keepScroll = false) {
  const repeat = !!lastPlanReq && lastPlanReq.message === message;
  lastPlanReq = {message, answered};
  const btn = $("#ask button[type=submit]");
  btn.disabled = true; btn.textContent = t("thinking");
  try {
    const p = await api("/api/consult", {message, lang, answered, repeat});
    renderPlan(p);
    if (!keepScroll) $("#plan").scrollIntoView({behavior: "smooth", block: "start"});
  } catch (e) {
    $("#plan").innerHTML = `<div class="level CRITICAL" role="alert">⚠️ ${esc(t("err"))}</div><div class="calls"><a href="tel:108">📞 108</a><a class="alt" href="tel:112">📞 112</a></div>`;
  } finally { btn.disabled = false; btn.textContent = t("send"); }
}
$("#ask").addEventListener("submit", e => { e.preventDefault(); const m = $("#msg").value.trim(); if (m) runConsult(m); });
$$(".chip").forEach(c => c.addEventListener("click", () => { $("#msg").value = c.textContent; runConsult(c.textContent); }));

// voice input (browser speech recognition, where available)
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
if (SR) {
  const mic = $("#mic"); mic.hidden = false;
  mic.addEventListener("click", () => {
    const r = new SR(); r.lang = lang === "hi" ? "hi-IN" : "en-IN"; r.interimResults = false;
    r.onresult = ev => { const s = ev.results[0][0].transcript; $("#msg").value = s; runConsult(s); };
    try { r.start(); } catch (_) {}
  });
}

// --------------------------------------------------------------------------- hospitals (OpenStreetMap)
const GOV = /(govt|government|district|civil|sadar|community health|chc|phc|primary health|medical college|aiims|esi|general hospital|सरकारी|जिला|ज़िला|सामुदायिक|प्राथमिक)/i;
function km(a, b, c, d) { const R = 6371, r = x => x * Math.PI / 180; const x = Math.sin(r(c - a) / 2) ** 2 + Math.cos(r(a)) * Math.cos(r(c)) * Math.sin(r(d - b) / 2) ** 2; return 2 * R * Math.asin(Math.sqrt(x)); }
function mapFallback(msgKey) {
  const q = encodeURIComponent(lang === "hi" ? "सरकारी अस्पताल" : "government hospital");
  return `<p>${t(msgKey)} <a href="https://www.google.com/maps/search/${q}/" target="_blank" rel="noopener">${t("hosp_map")}</a></p>`;
}
function findHospitals() {
  const out = $("#hlist");
  out.innerHTML = `<p>${t("hosp_wait")}</p>`;
  if (!navigator.geolocation) { out.innerHTML = mapFallback("hosp_denied"); return; }
  navigator.geolocation.getCurrentPosition(async pos => {
    const {latitude: la, longitude: lo} = pos.coords;
    const q = `[out:json][timeout:15];(node[amenity=hospital](around:30000,${la},${lo});way[amenity=hospital](around:30000,${la},${lo});node[healthcare=centre](around:15000,${la},${lo}););out center tags 60;`;
    try {
      const ctl = new AbortController(); setTimeout(() => ctl.abort(), 16000);
      const r = await fetch("https://overpass-api.de/api/interpreter", {method: "POST", body: "data=" + encodeURIComponent(q), signal: ctl.signal});
      const j = await r.json();
      const list = (j.elements || []).map(e => {
        const lat = e.lat || (e.center && e.center.lat), lon = e.lon || (e.center && e.center.lon);
        const tg = e.tags || {}; const name = tg["name:" + lang] || tg.name || tg["name:en"] || "Hospital";
        return {name, lat, lon, d: km(la, lo, lat, lon), gov: GOV.test(name + " " + (tg.operator || "") + " " + (tg["operator:type"] || "")) || tg["operator:type"] === "government", phone: tg.phone || tg["contact:phone"]};
      }).filter(x => x.lat);
      // Government hospitals keep antivenom: prefer one up to 10 km further than a private one.
      list.forEach(h => { h.score = h.d - (h.gov ? 10 : 0); });
      list.sort((a, b) => a.score - b.score);
      const top = list.slice(0, 6);
      if (!top.length) { out.innerHTML = mapFallback("hosp_none"); return; }
      out.innerHTML = `<ol>${top.map(h => `<li><b>${esc(h.name)}</b>${h.gov ? " 🏥" : ""}<div class="meta">${h.d.toFixed(1)} km · <a href="https://www.google.com/maps/dir/?api=1&destination=${h.lat},${h.lon}" target="_blank" rel="noopener">${t("directions")}</a>${h.phone ? ` · <a href="tel:${esc(h.phone.split(";")[0])}">${t("call")}</a>` : ""}</div></li>`).join("")}</ol>` + `<p><a href="https://www.google.com/maps/search/${encodeURIComponent(lang === "hi" ? "सरकारी अस्पताल" : "government hospital")}/" target="_blank" rel="noopener">${t("hosp_map")}</a></p>`;
    } catch (_) { out.innerHTML = mapFallback("hosp_none"); }
  }, () => { out.innerHTML = mapFallback("hosp_denied"); }, {enableHighAccuracy: false, timeout: 10000, maximumAge: 300000});
}

// --------------------------------------------------------------------------- 3-minute check
const sel = $("#state");
STATES.forEach(s => { const o = document.createElement("option"); o.value = s; o.textContent = s; sel.appendChild(o); });
let S = null;
function renderQuestion() {
  const run = $("#check-run");
  const q = S.questions[S.i];
  const phase = S.stage === "pre" ? t("phase_pre") : t("phase_post");
  const done = (S.stage === "pre" ? 0 : 7) + S.i;
  run.innerHTML = `<div class="phase">${phase}</div><div class="progress"><i style="width:${Math.round(100 * done / 13)}%"></i></div>
    <div class="understood">${t("q_of", {i: S.i + 1, n: S.questions.length})}</div>
    <div class="qtext">${esc(q.text)}</div>
    <div class="opts">${q.options.map(o => `<button class="opt" data-id="${o.id}">${esc(o.text)}</button>`).join("")}</div>`;
  $$(".opt", run).forEach(b => b.addEventListener("click", () => {
    S.answers[q.concept] = b.dataset.id; S.i++;
    if (S.i < S.questions.length) renderQuestion(); else submitStage();
  }));
  window.scrollTo(0, 0);
}
async function submitStage() {
  const run = $("#check-run");
  run.innerHTML = `<p>${t("thinking")}</p>`;
  try {
    if (S.stage === "pre") {
      const r = await api("/api/learn/pre", {session: S.id, answers: S.answers});
      S.pre = r.pre; S.post_questions = r.questions;
      run.innerHTML = `<div class="phase">${t("phase_lesson")}</div><div class="progress"><i style="width:${Math.round(600 / 13)}%"></i></div>
        <p class="lede">${t("lesson_lede", {c: r.pre.correct, n: r.pre.total})}</p>
        <div class="lesson">${r.lesson.map(c => `<div class="card ${c.missed ? "missed" : ""}">${c.missed ? `<div class="tag">${t("missed")}</div>` : ""}<h2>${esc(c.title)}</h2><p>${esc(c.text)}${src(c.source)}</p></div>`).join("")}</div>
        <button class="primary big" id="go-post">${t("next_part")}</button>`;
      $("#go-post").addEventListener("click", () => { S.stage = "post"; S.i = 0; S.answers = {}; S.questions = S.post_questions; renderQuestion(); });
      window.scrollTo(0, 0);
    } else {
      const r = await api("/api/learn/post", {session: S.id, answers: S.answers, state: $("#state").value || null, role: $("#role").value || null});
      const link = location.origin + "/check?src=share";
      const text = t("share_text") + link;
      run.innerHTML = `<h1>${t("result_h")}</h1>
        <div class="score"><div>${t("before")}<b>${r.pre.correct}/${r.total}</b><small>${t("danger_before", {d: r.pre.dangerous})}</small></div>
        <div>${t("after")}<b>${r.post.correct}/${r.total}</b><small>${t("danger_after", {d: r.post.dangerous})}</small></div></div>
        ${r.review.length ? `<div class="card"><h2>${t("review_h")}</h2><ul class="donts">${r.review.map(x => `<li><b>${esc(x.title)}:</b> ${esc(x.text)}</li>`).join("")}</ul></div>` : `<div class="card"><b>${t("perfect")}</b></div>`}
        <div class="card"><p><b>${t("share_h")}</b></p><div class="share">
          <a class="wa" id="wa" href="https://wa.me/?text=${encodeURIComponent(text)}" target="_blank" rel="noopener">${t("share_wa")}</a>
          <button class="copy" id="copy">${t("share_copy")}</button></div></div>
        <p><a href="/impact">${t("see_impact")}</a></p>
        <p><a href="/" id="back">${t("again")}</a></p>`;
      const mark = () => api("/api/learn/shared", {session: S.id}).catch(() => {});
      $("#wa").addEventListener("click", mark);
      $("#copy").addEventListener("click", async () => { try { await navigator.clipboard.writeText(link); $("#copy").textContent = t("copied"); mark(); } catch (_) { $("#copy").outerHTML = `<input class="copy" id="copyfield" value="${esc(link)}" readonly>`; const cf = $("#copyfield"); cf.addEventListener("focus", () => cf.select()); cf.focus(); } });
      window.scrollTo(0, 0);
    }
  } catch (e) {
    run.innerHTML = `<div class="note">${esc(String(e.message || e))}</div><button class="primary" id="reload">↻</button>`;
    $("#reload").addEventListener("click", () => location.reload());
  }
}
$("#start").addEventListener("click", async () => {
  $("#start").disabled = true;
  try {
    let client = store("dansh_client");
    if (!client) { client = (crypto.randomUUID ? crypto.randomUUID() : String(Math.random()).slice(2) + Date.now()).replace(/[^A-Za-z0-9_-]/g, ""); store("dansh_client", client); }
    const r = await api("/api/learn/start", {lang, src: SRC || null, client});
    S = {id: r.session, questions: r.questions, i: 0, answers: {}, stage: "pre"};
    $("#check-intro").hidden = true; $("#check-run").hidden = false;
    renderQuestion();
  } catch (e) { $("#start").disabled = false; $("#check-intro").insertAdjacentHTML("beforeend", `<div class="note">${esc(t("err"))}</div>`); }
});

// --------------------------------------------------------------------------- boot
if (TEST) { $$("a[href^='/']").forEach(a => { if (!a.href.includes("test=")) a.href += (a.href.includes("?") ? "&" : "?") + "test=1"; }); }
if (TEST) { const b = document.createElement("div"); b.className = "note"; b.style.margin = "0"; b.dataset.i18n = "test_banner"; document.body.insertBefore(b, $("main")); }
if (REPO_URL) $("#gh").href = REPO_URL; else $("#gh").href = GH;
applyLang();
if (location.pathname.startsWith("/check")) show("check");
})();
