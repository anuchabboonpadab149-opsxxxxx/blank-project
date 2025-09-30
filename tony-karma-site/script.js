const $, $ = (sel, ctx = document) => ctx.querySelector(sel), (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));

/* State */
const state = {
  user: null, // {email}
};

/* Persisted OpenAI key */
(() => {
  const keyInput = $('#openai-key');
  const saveBtn = $('#save-key');
  const clearBtn = $('#clear-key');

  const saved = localStorage.getItem('openai_key');
  if (saved && keyInput) keyInput.value = saved;

  if (saveBtn) saveBtn.addEventListener('click', () => {
    localStorage.setItem('openai_key', keyInput.value.trim());
    saveBtn.textContent = 'บันทึกแล้ว';
    setTimeout(() => (saveBtn.textContent = 'บันทึกคีย์'), 1200);
  });
  if (clearBtn) clearBtn.addEventListener('click', () => {
    localStorage.removeItem('openai_key');
    if (keyInput) keyInput.value = '';
  });
})();

/* Auth (demo - localStorage only) */
(() => {
  const authStatus = $('#auth-status');
  const btnLogin = $('#btn-login');
  const btnRegister = $('#btn-register');
  const btnLogout = $('#btn-logout');
  const modalLogin = $('#modal-login');
  const modalRegister = $('#modal-register');

  const savedUser = localStorage.getItem('user');
  if (savedUser) {
    state.user = JSON.parse(savedUser);
  }
  renderAuth();

  btnLogin?.addEventListener('click', () => modalLogin.hidden = false);
  btnRegister?.addEventListener('click', () => modalRegister.hidden = false);
  $('[data-close="login"]')?.addEventListener('click', () => modalLogin.hidden = true);
  $('[data-close="register"]')?.addEventListener('click', () => modalRegister.hidden = true);

  $('#do-login')?.addEventListener('click', () => {
    const email = $('#login-email').value.trim().toLowerCase();
    const pass = $('#login-password').value;
    const users = JSON.parse(localStorage.getItem('users') || '{}');
    if (users[email] && users[email].pass === pass) {
      state.user = { email };
      localStorage.setItem('user', JSON.stringify(state.user));
      modalLogin.hidden = true;
      renderAuth();
    } else {
      alert('อีเมลหรือรหัสผ่านไม่ถูกต้อง');
    }
  });

  $('#do-register')?.addEventListener('click', () => {
    const email = $('#reg-email').value.trim().toLowerCase();
    const pass = $('#reg-password').value;
    if (!email || !pass || pass.length < 8) {
      alert('กรอกอีเมลและรหัสผ่านอย่างน้อย 8 ตัว');
      return;
    }
    const users = JSON.parse(localStorage.getItem('users') || '{}');
    if (users[email]) {
      alert('อีเมลนี้ถูกใช้แล้ว');
      return;
    }
    users[email] = { pass };
    localStorage.setItem('users', JSON.stringify(users));
    state.user = { email };
    localStorage.setItem('user', JSON.stringify(state.user));
    $('#modal-register').hidden = true;
    renderAuth();
  });

  btnLogout?.addEventListener('click', () => {
    state.user = null;
    localStorage.removeItem('user');
    renderAuth();
  });

  function renderAuth() {
    if (state.user) {
      authStatus.textContent = `เข้าสู่ระบบ: ${state.user.email}`;
      btnLogin.style.display = 'none';
      btnRegister.style.display = 'none';
      btnLogout.style.display = 'inline-flex';
    } else {
      authStatus.textContent = 'ยังไม่ได้เข้าสู่ระบบ';
      btnLogin.style.display = 'inline-flex';
      btnRegister.style.display = 'inline-flex';
      btnLogout.style.display = 'none';
    }
  }
})();

/* Utils */
const formatDateTh = (d) =>
  d ? new Date(d).toLocaleDateString('th-TH', { year: 'numeric', month: 'long', day: 'numeric' }) : '';
const dayOfWeekTh = (d) => {
  if (!d) return '';
  return new Date(d).toLocaleDateString('th-TH', { weekday: 'long' });
};
const seeded = (seedStr) => {
  let h = 2166136261 >>> 0;
  for (let i = 0; i < seedStr.length; i++) h ^= seedStr.charCodeAt(i), h += (h << 1) + (h << 4) + (h << 7) + (h << 8) + (h << 24);
  return () => {
    h += 0x6D2B79F5;
    let t = Math.imul(h ^ (h >>> 15), 1 | h);
    t ^= t + Math.imul(t ^ (t >>> 7), 61 | t);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
};
const pick = (arr, rnd = Math.random) => arr[Math.floor(rnd() * arr.length)];

/* Presets */
const ASTRO_PRESETS = {
  balanced: 'โทนสมดุล เน้นข้อแนะนำปฏิบัติได้',
  love: 'โฟกัสความรักและความสัมพันธ์เป็นพิเศษ',
  career: 'โฟกัสงาน การเติบโต รายได้ และการเงิน',
  health: 'โฟกัสสุขภาพกายใจ การพักผ่อน สมดุลชีวิต',
};
const DREAM_PRESETS = {
  balanced: 'โทนสมดุล สะท้อนใจอย่างอ่อนโยน',
  relationship: 'โฟกัสความสัมพันธ์ ความรู้สึก ความผูกพัน',
  career: 'โฟกัสเป้าหมาย งาน การตัดสินใจ',
  healing: 'โฟกัสการเยียวยา การเติบโต และสติ',
};

/* History */
function pushHistory(item) {
  // Gate history for logged-in users only
  const user = JSON.parse(localStorage.getItem('user') || 'null');
  if (!user) return;
  const key = `history:${user.email}`;
  const list = JSON.parse(localStorage.getItem(key) || '[]');
  list.unshift({ ...item, ts: Date.now() });
  localStorage.setItem(key, JSON.stringify(list.slice(0, 100)));
  renderHistory();
}
function renderHistory() {
  const container = $('#history-list');
  if (!container) return;
  const user = JSON.parse(localStorage.getItem('user') || 'null');
  if (!user) { container.innerHTML = '<p class="small">กรุณาเข้าสู่ระบบเพื่อดูประวัติ</p>'; return; }
  const key = `history:${user.email}`;
  const list = JSON.parse(localStorage.getItem(key) || '[]');
  if (!list.length) { container.innerHTML = '<p class="small">ยังไม่มีประวัติ</p>'; return; }
  container.innerHTML = list.map(it => {
    const dt = new Date(it.ts).toLocaleString('th-TH');
    return `<div class="card" style="margin:8px 0;">
      <div class="small">${dt} • ประเภท: ${it.type}</div>
      <div>${it.html}</div>
    </div>`;
  }).join('');
}
$('#clear-history')?.addEventListener('click', () => {
  const user = JSON.parse(localStorage.getItem('user') || 'null');
  if (!user) return;
  localStorage.removeItem(`history:${user.email}`);
  renderHistory();
});
renderHistory();

/* ASTROLOGY */
const zodiac = (month, day) => {
  const z = [
    ['มังกร', 1, 20], ['กุมภ์', 2, 19], ['มีน', 3, 20],
    ['เมษ', 4, 20], ['พฤษภ', 5, 21], ['เมถุน', 6, 21],
    ['กรกฎ', 7, 22], ['สิงห์', 8, 23], ['กันย์', 9, 23],
    ['ตุลย์', 10, 23], ['พิจิก', 11, 22], ['ธนู', 12, 21],
    ['มังกร', 12, 31],
  ];
  for (let i = 0; i < z.length - 1; i++) {
    const [name, m, d] = z[i], [nextName, nm, nd] = z[i + 1];
    if ((month === m && day >= d) || (month === nm && day <= nd)) return name;
  }
  return 'มังกร';
};
const zodiacElement = (sign) => {
  const fire = ['เมษ', 'สิงห์', 'ธนู'];
  const earth = ['พฤษภ', 'กันย์', 'มังกร'];
  const air = ['เมถุน', 'ตุลย์', 'กุมภ์'];
  const water = ['กรกฎ', 'พิจิก', 'มีน'];
  if (fire.includes(sign)) return 'ไฟ';
  if (earth.includes(sign)) return 'ดิน';
  if (air.includes(sign)) return 'ลม';
  if (water.includes(sign)) return 'น้ำ';
  return 'ธาตุ';
};
const chineseZodiac = (year) => {
  const names = ['ชวด(หนู)','ฉลู(วัว)','ขาล(เสือ)','เถาะ(กระต่าย)','มะโรง(มังกร)','มะเส็ง(งู)','มะเมีย(ม้า)','มะแม(แพะ)','วอก(ลิง)','ระกา(ไก่)','จอ(สุนัข)','กุน(หมู)'];
  const offset = (year - 2020) % 12;
  return names[(offset + 12) % 12];
};

$('#astro-form')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const name = $('#name').value.trim() || 'ผู้ถาม';
  const dob = $('#dob').value;
  const tob = $('#tob').value;
  const pob = $('#pob').value.trim();
  const preset = $('#astro-preset')?.value || 'balanced';

  if (!dob) {
    $('#astro-output').innerHTML = `<p class="danger">กรุณาระบุวันเกิด</p>`;
    return;
  }
  const date = new Date(dob);
  const sign = zodiac(date.getMonth() + 1, date.getDate());
  const element = zodiacElement(sign);
  const cz = chineseZodiac(date.getFullYear());
  const day = dayOfWeekTh(dob);

  const seed = seeded(`${name}|${dob}|${tob}|${pob}`);
  const love = pick([
    `ความสัมพันธ์มีแนวโน้มอบอุ่น เปิดใจสื่อสารจะช่วยคลี่คลายความเข้าใจคลาดเคลื่อน`,
    `โสดมีโอกาสพบคนที่คล้ายกันทางความคิด แต่ต้องค่อยๆทำความรู้จัก`,
    `ควรดูแลขอบเขตส่วนตัว ความรักเติบโตจากการเคารพซึ่งกันและกัน`,
    `อดีตคนรักอาจกลับมาทำให้ใจสั่น แต่ให้ตัดสินใจจากคุณค่าปัจจุบัน`
  ], seed);
  const career = pick([
    `งานขยับตัวดี มีโอกาสเรียนรู้สกิลใหม่ ควรกล้ารับผิดชอบงานท้าทาย`,
    `เน้นวางระบบ ลดงานซ้ำซ้อน จะเห็นผลชัดใน ${pick(['2-3 สัปดาห์','ปลายเดือน','ต้นเดือนหน้า'], seed)}`,
    `ผู้ใหญ่สนับสนุน แต่ต้องชัดเจนเรื่องเป้าหมายและวิธีวัดผล`,
    `ระวังการสื่อสารคลาดเคลื่อน ใช้เอกสาร/ข้อความยืนยัน`
  ], seed);
  const money = pick([
    `การเงินทรงตัว มีค่าใช้จ่ายด้านเครื่องใช้/เทคโนโลยี`,
    `มีโชคเล็กๆ จากการเสี่ยงแบบพอประมาณ ไม่ควรทุ่ม`,
    `ควรจัดงบสำรองฉุกเฉิน จะรู้สึกมั่นคงขึ้น`,
    `การลงทุนควรศึกษาข้อมูลและแบ่งพอร์ต ไม่ไล่ตามกระแส`
  ], seed);
  const health = pick([
    `พักผ่อนให้เพียงพอ ระวังออฟฟิศซินโดรม ควรยืดกล้ามเนื้อ`,
    `ระบบทางเดินอาหาร/ผิวหนัง ต้องดูแลเป็นพิเศษ`,
    `สุขภาพจิตดีขึ้นเมื่อมีสมดุลงาน-ชีวิต`,
    `การออกกำลังแบบสม่ำเสมอช่วยปรับสมดุลพลังงานธาตุ ${element}`
  ], seed);
  const luck = pick([
    `เลขนำโชค: ${Math.floor(seed()*90+10)} สีเสริมดวง: ${pick(['ม่วง','น้ำเงิน','เขียว','ทอง','ชมพู'], seed)}`,
    `ช่วงเวลาที่ดี: ${pick(['เช้า','บ่าย','ค่ำ'], seed)} วัน${day}`,
    `สวดมนต์/ทำสมาธิ ${pick(['9 นาที','15 นาที','21 นาที'], seed)} ช่วยเสริมพลังบวก`,
    `ทำบุญด้านการศึกษา/หนังสือ จะเสริมปัญญาและการตัดสินใจ`
  ], seed);

  const content = `
    <h4>ข้อมูลกำเนิด</h4>
    <p><strong>ชื่อ:</strong> ${name} • <strong>วันเกิด:</strong> ${formatDateTh(dob)} (${day}) • <strong>ราศี:</strong> ${sign} (ธาตุ ${element}) • <strong>นักษัตร:</strong> ${cz}${pob ? ` • <strong>เกิดที่:</strong> ${pob}` : ''}</p>
    <h4>คำทำนาย</h4>
    <ul class="list">
      <li><strong>ความรัก:</strong> ${love}</li>
      <li><strong>การงาน:</strong> ${career}</li>
      <li><strong>การเงิน:</strong> ${money}</li>
      <li><strong>สุขภาพ:</strong> ${health}</li>
      <li><strong>โชคลาภ:</strong> ${luck}</li>
    </ul>
  `;

  const basePrompt = `
คุณคือหมอดูชื่อ "อ.โทนี่สะท้อนกรรม" ให้คำทำนายภาษาไทย สุภาพ จริงใจ เชิงบวกแต่ไม่โอเวอร์
ข้อมูลผู้ถาม: ชื่อ=${name}, วันเกิด=${formatDateTh(dob)} (${day}), ราศี=${sign} ธาตุ=${element}, นักษัตร=${cz}, เวลาเกิด=${tob||'-'}, สถานที่เกิด=${pob||'-'}
โทน/ชุดคำถาม: ${ASTRO_PRESETS[preset]}
โปรดสรุปคำทำนาย 5 ด้าน: ความรัก การงาน การเงิน สุขภาพ โชคลาภ ให้เป็นย่อหน้าอ่านง่าย 5-7 บรรทัด รวมข้อแนะนำสั้นๆที่ปฏิบัติได้
  `.trim();

  const key = localStorage.getItem('openai_key')?.trim();
  if (key) {
    try {
      const aiText = await askOpenAI(key, basePrompt);
      const html = content + `<div class="output"><h4>โหมด AI</h4><p>${aiText}</p></div>`;
      $('#astro-output').innerHTML = html;
      pushHistory({ type: 'โหราศาสตร์', html });
    } catch (err) {
      $('#astro-output').innerHTML = content + `<p class="small">โหมด AI ไม่พร้อมใช้งาน: ${err.message}</p>`;
      pushHistory({ type: 'โหราศาสตร์', html: content });
    }
  } else {
    // Try serverless proxy if logged in
    try {
      const user = JSON.parse(localStorage.getItem('user') || 'null');
      if (user) {
        const aiText = await askOpenAIProxy(basePrompt);
        const html = content + `<div class="output"><h4>โหมด AI (พร็อกซี)</h4><p>${aiText}</p></div>`;
        $('#astro-output').innerHTML = html;
        pushHistory({ type: 'โหราศาสตร์', html });
        return;
      }
    } catch (e) {
      // ignore and fallback
    }
    $('#astro-output').innerHTML = content;
    pushHistory({ type: 'โหราศาสตร์', html: content });
  }
});

/* TAROT */
const TAROT = [
  { name: 'The Fool (การเริ่มต้น)', meaning: 'เริ่มต้นใหม่ เปิดใจ กล้าลอง สิ่งที่ไม่คุ้นเคยอาจนำโอกาส' },
  { name: 'The Magician (นักมายากล)', meaning: 'ทรัพยากรพร้อม ใช้ทักษะและการสื่อสาร สร้างผลลัพธ์' },
  { name: 'The High Priestess (สตรีนักบวช)', meaning: 'ใช้สัญชาตญาณ ความลับ ความนิ่งช่วยให้เห็นคำตอบ' },
  { name: 'The Empress (จักรพรรดินี)', meaning: 'ความอุดมสมบูรณ์ ความรัก การดูแลตัวเองและผู้อื่น' },
  { name: 'The Emperor (จักรพรรดิ)', meaning: 'โครงสร้าง ภาวะผู้นำ วางขอบเขตและกติกา' },
  { name: 'The Hierophant (พระสันตะปาปา)', meaning: 'การเรียนรู้จากครู ระบบ ความเชื่อดั้งเดิม' },
  { name: 'The Lovers (คนรัก)', meaning: 'การเลือก ความสัมพันธ์ ความกลมกลืนด้วยความจริงใจ' },
  { name: 'The Chariot (รถศึก)', meaning: 'ก้าวไปข้างหน้า มีวินัย ฝ่าข้อจำกัดด้วยความมุ่งมั่น' },
  { name: 'Strength (พลัง)', meaning: 'ใจเข้มแข็ง อ่อนโยนแต่หนักแน่น จัดการความกลัว' },
  { name: 'The Hermit (ฤาษี)', meaning: 'ถอยกลับมาทบทวน ค้นหาความหมายภายใน' },
  { name: 'Wheel of Fortune (วงล้อโชคชะตา)', meaning: 'วงจรเปลี่ยนแปลง โอกาสหมุนมาถึง จังหวะสำคัญ' },
  { name: 'Justice (ความยุติธรรม)', meaning: 'ความเที่ยงตรง ผลลัพธ์ตามเหตุปัจจัย รับผิดชอบการตัดสินใจ' },
  { name: 'The Hanged Man (คนถูกแขวน)', meaning: 'มุมมองใหม่ ยอมหยุดเพื่อเห็นทางออก' },
  { name: 'Death (ความตาย)', meaning: 'ปิดฉากเพื่อเริ่มใหม่ เปลี่ยนแปลงเชิงลึก' },
  { name: 'Temperance (ความพอดี)', meaning: 'สมดุล ปรับตัว ค่อยเป็นค่อยไป' },
  { name: 'The Devil (ปีศาจ)', meaning: 'พันธนาการ ความยึดติด ตระหนักรู้แล้วค่อยๆปล่อย' },
  { name: 'The Tower (หอคอย)', meaning: 'ความจริงเปิดเผย สิ่งที่ไม่มั่นคงพังเพื่อสร้างใหม่' },
  { name: 'The Star (ดาว)', meaning: 'ความหวัง การเยียวยา มองไกลและซื่อสัตย์กับตนเอง' },
  { name: 'The Moon (พระจันทร์)', meaning: 'สัญญาณคลุมเครือ อารมณ์สูงต่ำ เชื่อมกับสัญชาตญาณ' },
  { name: 'The Sun (พระอาทิตย์)', meaning: 'ความสำเร็จ ความสุข ความชัดเจน' },
  { name: 'Judgement (การพิพากษา)', meaning: 'ตื่นรู้ เรียกคืนพลัง เรียนจากอดีต' },
  { name: 'The World (โลก)', meaning: 'ครบถ้วน สมบูรณ์ วงจรเสร็จสิ้นพร้อมเริ่มใหม่' },
];

$('#draw-tarot')?.addEventListener('click', () => {
  const n = parseInt($('#tarot-count').value, 10);
  const rnd = seeded(String(Date.now()));
  const cards = [];
  for (let i = 0; i < n; i++) {
    const idx = Math.floor(rnd()*TAROT.length);
    const upright = rnd() > 0.5;
    const data = TAROT[idx];
    cards.push({ ...data, upright });
  }
  const grid = $('#tarot-output');
  grid.innerHTML = '';
  cards.forEach((c, i) => {
    const el = document.createElement('div');
    el.className = 'tarot-card';
    el.innerHTML = `
      <h4>${n === 3 ? ['อดีต','ปัจจุบัน','อนาคต'][i] + ' • ' : ''}${c.name} ${c.upright ? '(ไพ่ตั้ง)' : '(ไพ่กลับหัว)'}</h4>
      <p>${c.upright ? c.meaning : invertMeaning(c.meaning)}</p>
      <p class="minor">ข้อแนะนำ: ${adviceFromTarot(c)}</p>
    `;
    grid.appendChild(el);
  });
  pushHistory({ type: 'ไพ่ยิปซี', html: grid.innerHTML });
});

const invertMeaning = (m) => {
  return 'พลังด้านเงา: ' + m.replace(' ', ' อาจมีความท้าทายด้าน ');
};
const adviceFromTarot = (c) => {
  const base = [
    'สื่อสารอย่างจริงใจและชัดเจน',
    'รักษาสมดุลงาน-ชีวิต',
    'จัดระบบและตั้งเป้าหมายเล็กๆ',
    'ฝึกสติและฟังหัวใจตัวเอง',
    'เปิดรับการเปลี่ยนแปลงทีละก้าว'
  ];
  return pick(base);
};

/* SIEMSI */
const SIEMSI = [
  { no: 1, tone: 'ดีมาก', text: 'สิ่งที่ตั้งใจมีโอกาสสำเร็จ หากเพียรพยายามและไม่รีบร้อน' },
  { no: 2, tone: 'ดี', text: 'โชคดีมาจากคนช่วยเหลือ อย่าลืมขอบคุณผู้มีพระคุณ' },
  { no: 3, tone: 'กลาง', text: 'ต้องวางแผนให้รอบคอบ ตั้งงบประมาณให้ชัดเจน' },
  { no: 4, tone: 'พอใช้', text: 'ค่อยเป็นค่อยไป ทำทีละขั้นจะปลอดภัย' },
  { no: 5, tone: 'ระวัง', text: 'อย่าเชื่อข่าวลือ ตรวจสอบข้อมูล' },
  { no: 6, tone: 'ดี', text: 'ได้รับโอกาสจากผู้ใหญ่ แสดงความสามารถให้เต็มที่' },
  { no: 7, tone: 'กลาง', text: 'ใจเย็น ฟังทั้งหัวใจและเหตุผล' },
  { no: 8, tone: 'ดีมาก', text: 'การเงินมีผู้สนับสนุน โอกาสปรับฐานะ' },
  { no: 9, tone: 'ระวัง', text: 'อย่าใจร้อน อดทนจะผ่านไป' },
  { no: 10, tone: 'ดี', text: 'เดินทางเจอโอกาสใหม่ พบผู้ร่วมทางที่ดี' },
  { no: 11, tone: 'กลาง', text: 'ผลลัพธ์ขึ้นกับการสื่อสาร ยืนยันด้วยเอกสาร' },
  { no: 12, tone: 'ดีมาก', text: 'อธิษฐานด้วยใจใส จะเห็นทางออกชัดเจน' },
  { no: 13, tone: 'เปลี่ยน', text: 'สิ่งเก่าปิดฉากเพื่อเริ่มใหม่ กล้าปรับวิธี' },
  { no: 14, tone: 'พอดี', text: 'ทางสายกลางจะพาไปถึงเป้าหมาย' },
  { no: 15, tone: 'ผูกพัน', text: 'ปล่อยวางความยึดติดทีละน้อย' },
  { no: 16, tone: 'เปิดเผย', text: 'ความจริงต้องเผชิญ เพื่อสร้างใหม่ให้มั่นคง' },
  { no: 17, tone: 'หวัง', text: 'ดูแลตัวเอง เติมพลังใจ แล้วค่อยเดินต่อ' },
  { no: 18, tone: 'คลุมเครือ', text: 'อย่ารีบตัดสิน เปิดพื้นที่ให้ความรู้สึก' },
  { no: 19, tone: 'ชัดเจน', text: 'พลังงานบวกสูง ทำเรื่องสำคัญได้ผลดี' },
  { no: 20, tone: 'ตื่นรู้', text: 'เรียนจากบทเรียนเก่า โอกาสใหม่กำลังมา' },
];

$('#shake-siemsi')?.addEventListener('click', () => {
  const s = pick(SIEMSI);
  $('#siemsi-output').innerHTML = `
    <p>ใบที่ <strong>${s.no}</strong> (${s.tone})</p>
    <p>${s.text}</p>
  `;
  pushHistory({ type: 'เซียมซี', html: $('#siemsi-output').innerHTML });
});

/* DICE */
$('#roll-dice')?.addEventListener('click', () => {
  const diceEl = document.createElement('span');
  diceEl.className = 'dice spin';
  diceEl.textContent = '🎲';
  $('#dice-output').innerHTML = '';
  $('#dice-output').appendChild(diceEl);
  setTimeout(() => {
    diceEl.classList.remove('spin');
    const n = Math.floor(Math.random()*6)+1;
    const advice = [
      'โฟกัสหนึ่งเรื่องให้จบ',
      'ขอความช่วยเหลือเมื่อจำเป็น',
      'วางแผนและทำตามทีละขั้น',
      'พักสั้นๆ แล้วกลับมาลุยต่อ',
      'ทบทวนเป้าหมายและปรับวิธี',
      'ลงมือทำทันที ไม่ผัดวัน'
    ][n-1];
    $('#dice-output').innerHTML = `<p>ผลการทอย: <strong>${n}</strong></p><p>คำแนะนำ: ${advice}</p>`;
    pushHistory({ type: 'ลูกเต๋า', html: $('#dice-output').innerHTML });
  }, 500);
});

/* DREAM */
const DREAM_MAP = [
  { keys: ['งู','เลื้อย'], topic: 'ความรัก/พันธะ', meaning: 'ความสัมพันธ์ขยับตัว ระวังความผูกพันที่ทำให้อึดอัด' },
  { keys: ['ฟัน','ฟันหัก'], topic: 'ความมั่นใจ', meaning: 'กังวลภาพลักษณ์ ดูแลสุขภาพช่องปากและใจ' },
  { keys: ['พระ','วัด'], topic: 'จิตวิญญาณ', meaning: 'ต้องการความสงบ แนะนำทำสมาธิสั้นๆ' },
  { keys: ['เงิน','ทอง'], topic: 'การเงิน', meaning: 'โอกาสเรื่องทรัพย์ แต่อย่าประมาทค่าใช้จ่าย' },
  { keys: ['สุนัข','แมว'], topic: 'เพื่อน/ความภักดี', meaning: 'คนรอบตัวพร้อมช่วยเหลือ เปิดใจรับความช่วยเหลือ' },
  { keys: ['น้ำ','ฝน','ทะเล'], topic: 'อารมณ์', meaning: 'อารมณ์ขึ้นลง ฟังหัวใจและพักผ่อน' },
  { keys: ['ขี้','ขับถ่าย'], topic: 'ปล่อยวาง', meaning: 'กำลังปล่อยของเก่า เตรียมพื้นที่ให้สิ่งใหม่' },
  { keys: ['ตาย','ศพ'], topic: 'การเปลี่ยนแปลง', meaning: 'สิ่งเก่าปิดฉากเพื่อเริ่มใหม่' },
  { keys: ['เด็ก','โรงเรียน'], topic: 'การเรียนรู้', meaning: 'โฟกัสทักษะใหม่ จะเกิดผลดี' },
  { keys: ['บ้าน','ครอบครัว'], topic: 'ความมั่นคง', meaning: 'ดูแลบ้านและครอบครัว เติมความอบอุ่น' },
];

$('#dream-form')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const text = $('#dream-text').value.trim();
  const preset = $('#dream-preset')?.value || 'balanced';
  if (!text) {
    $('#dream-output').innerHTML = `<p class="danger">กรุณาเล่าความฝัน</p>`;
    return;
  }
  const lower = text.toLowerCase();
  const hit = DREAM_MAP.filter(m => m.keys.some(k => lower.includes(k)));
  const baseMsg = hit.length
    ? hit.map(m => `• หัวข้อ: <strong>${m.topic}</strong> — ${m.meaning}`).join('<br>')
    : 'ฝันสะท้อนความรู้สึกภายใน ให้เวลาและพื้นที่กับตัวเอง แล้วค่อยตัดสินใจเรื่องสำคัญ';
  const advice = pick([
    'จดบันทึกความฝัน 3 คืนติดต่อกัน เพื่อเห็นรูปแบบซ้ำ',
    'ทำสมาธิ 9 นาที ก่อนนอน ปรับสมดุลอารมณ์',
    'สื่อสารกับคนสำคัญอย่างเปิดใจ ลดความคลุมเครือ'
  ]);
  const templated = `<p>${baseMsg}</p><p class="minor">ข้อแนะนำ: ${advice}</p>`;

  const prompt = `
คุณคือหมอดู "อ.โทนี่สะท้อนกรรม" วิเคราะห์ความฝันภาษาไทยให้เป็นเชิงบวกและปฏิบัติได้
บริบท/ชุดคำถาม: ${DREAM_PRESETS[preset]}
ความฝัน: """${text}"""
สรุปประเด็นที่สะท้อนใจ และให้ข้อแนะนำสั้นๆ 4-6 บรรทัด
  `.trim();

  const key = localStorage.getItem('openai_key')?.trim();
  if (key) {
    try {
      const aiText = await askOpenAI(key, prompt);
      const html = templated + `<div class="output"><h4>โหมด AI</h4><p>${aiText}</p></div>`;
      $('#dream-output').innerHTML = html;
      pushHistory({ type: 'ทำนายฝัน', html });
    } catch (err) {
      $('#dream-output').innerHTML = templated + `<p class="small">โหมด AI ไม่พร้อมใช้งาน: ${err.message}</p>`;
      pushHistory({ type: 'ทำนายฝัน', html: templated });
    }
  } else {
    try {
      const user = JSON.parse(localStorage.getItem('user') || 'null');
      if (user) {
        const aiText = await askOpenAIProxy(prompt);
        const html = templated + `<div class="output"><h4>โหมด AI (พร็อกซี)</h4><p>${aiText}</p></div>`;
        $('#dream-output').innerHTML = html;
        pushHistory({ type: 'ทำนายฝัน', html });
        return;
      }
    } catch (e) {}
    $('#dream-output').innerHTML = templated;
    pushHistory({ type: 'ทำนายฝัน', html: templated });
  }
});

/* Payment copy */
$('#copy-account')?.addEventListener('click', () => {
  const t = $('#scb-account').textContent.trim();
  navigator.clipboard.writeText(t);
});

/* OpenAI helper - direct (unsafe for production) */
async function askOpenAI(key, prompt) {
  const res = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${key}`,
    },
    body: JSON.stringify({
      model: 'gpt-4o-mini',
      messages: [
        { role: 'system', content: 'คุณเป็นหมอดูที่ให้คำทำนายอย่างอ่อนโยน จริงใจ และยึดโยงกับการปฏิบัติได้' },
        { role: 'user', content: prompt }
      ],
      temperature: 0.7,
    })
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  const data = await res.json();
  const choice = data.choices?.[0]?.message?.content;
  return choice || '';
}

/* OpenAI helper - serverless proxy */
async function askOpenAIProxy(prompt) {
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt }),
  });
  if (!res.ok) throw new Error(await res.text());
  const data = await res.json();
  return data.text || '';
}