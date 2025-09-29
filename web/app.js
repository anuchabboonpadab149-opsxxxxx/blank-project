// Shared frontend logic for multi-page flow

(function(){
  const params = new URLSearchParams(location.search);
  const apiFromQS = params.get("api");
  if (apiFromQS) localStorage.setItem("api_base_override", apiFromQS);
})();

const API = (window.APP_CONFIG && window.APP_CONFIG.API_BASE) || "";
let token = localStorage.getItem("token") || "";
let userId = localStorage.getItem("user_id") || "";

function authHeaders(){
  return token ? { "Authorization": "Bearer " + token } : {};
}
function setAuth(id, tok){
  userId = id; token = tok;
  localStorage.setItem("user_id", id);
  localStorage.setItem("token", tok);
}
function clearAuth(){
  localStorage.removeItem("user_id");
  localStorage.removeItem("token");
  userId = ""; token = "";
}

function qsGet(name, d=""){ const u=new URLSearchParams(location.search); return u.get(name) || d; }
function goto(url){ location.href = url; }

// Header helpers
function attachAdminShortcut(){
  document.addEventListener("keydown", (e)=>{
    if (e.altKey && e.shiftKey && e.key.toLowerCase() === "a"){
      location.href = "../admin/index.html";
    }
  });
}
function updateAuthUI(){
  const s1 = document.getElementById("nav-auth");
  const s2 = document.getElementById("nav-me");
  if (!s1 || !s2) return;
  if (token){
    s1.classList.add("hidden");
    s2.classList.remove("hidden");
    const u = document.getElementById("me-id"); if (u) u.textContent = userId;
  }else{
    s1.classList.remove("hidden");
    s2.classList.add("hidden");
  }
}
function logout(){
  clearAuth();
  updateAuthUI();
  goto("../pages/login.html");
}
function requireAuth(redirectTo){
  if (!token){
    const next = encodeURIComponent(redirectTo || location.pathname + location.search);
    goto("../pages/login.html?next="+next);
    throw new Error("Auth required");
  }
}

// API wrappers
async function apiRegister(email, password){
  const r = await fetch(API + "/auth/register", { method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({email,password}) });
  const data = await r.json(); if (!r.ok) throw new Error(data.detail || JSON.stringify(data));
  setAuth(data.user_id, data.token);
  return data;
}
async function apiLogin(email, password){
  const r = await fetch(API + "/auth/login", { method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({email,password}) });
  const data = await r.json(); if (!r.ok) throw new Error(data.detail || JSON.stringify(data));
  setAuth(data.user_id, data.token);
  return data;
}
async function apiPackages(){
  const r = await fetch(API + "/packages");
  const data = await r.json(); if (!r.ok) throw new Error(JSON.stringify(data));
  return data;
}
async function apiCreatePayment(package_id){
  const r = await fetch(API + "/payment/create", { method:"POST", headers:{"Content-Type":"application/json", ...authHeaders()}, body: JSON.stringify({package_id}) });
  const data = await r.json(); if (!r.ok) throw new Error(JSON.stringify(data));
  return data; // {transaction_id, qr_code_url, ...}
}
async function apiVerifyPayment(transaction_id, slip_image_url){
  const r = await fetch(API + "/payment/verify", { method:"POST", headers:{"Content-Type":"application/json", ...authHeaders()}, body: JSON.stringify({transaction_id, slip_image_url}) });
  const data = await r.json(); if (!r.ok) throw new Error(JSON.stringify(data));
  return data;
}
async function apiPaymentStatus(tx){
  const r = await fetch(API + "/payment/status/" + encodeURIComponent(tx), { headers: {...authHeaders()} });
  if (!r.ok) return { status: "-" };
  return await r.json();
}
async function apiCredits(){
  const r = await fetch(API + "/user/credits", { headers: {...authHeaders()} });
  const data = await r.json(); if (!r.ok) throw new Error(JSON.stringify(data));
  return data.credit_balance || 0;
}
async function apiSources(){
  const r = await fetch(API + "/fortune/sources");
  const data = await r.json(); if (!r.ok) throw new Error(JSON.stringify(data));
  return data;
}
async function apiDraw(source_id){
  const r = await fetch(API + "/fortune/draw", { method:"POST", headers:{"Content-Type":"application/json", ...authHeaders()}, body: JSON.stringify({source_id}) });
  const data = await r.json();
  if (!r.ok || data.error) throw new Error(data.error || JSON.stringify(data));
  return data;
}
async function apiTarotMulti(source_id, count){
  const r = await fetch(API + "/fortune/tarot/draw-multi", { method:"POST", headers:{"Content-Type":"application/json", ...authHeaders()}, body: JSON.stringify({source_id, count}) });
  const data = await r.json(); if (!r.ok) throw new Error(JSON.stringify(data));
  return data;
}
async function apiHistory(){
  const r = await fetch(API + "/user/history/all", { headers: {...authHeaders()} });
  const data = await r.json(); if (!r.ok) throw new Error(JSON.stringify(data));
  return data;
}

// Watchers
let creditTimer = null;
async function startCreditWatcher(before, onCredited){
  if (creditTimer) clearInterval(creditTimer);
  creditTimer = setInterval(async ()=>{
    try{
      const now = await apiCredits();
      if (now > before){
        clearInterval(creditTimer);
        creditTimer = null;
        if (onCredited) onCredited(now);
      }
    }catch(_){}
  }, 3000);
}

// Expose to pages
window.FT = {
  API, token, userId,
  authHeaders, setAuth, clearAuth, updateAuthUI, logout, requireAuth, attachAdminShortcut,
  qsGet, goto,
  apiRegister, apiLogin, apiPackages, apiCreatePayment, apiVerifyPayment, apiPaymentStatus,
  apiCredits, apiSources, apiDraw, apiTarotMulti, apiHistory,
  startCreditWatcher
};