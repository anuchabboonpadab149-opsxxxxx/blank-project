// --- ค่าเริ่มต้นและการตั้งค่าแชร์ ---
// หากเว็บไซต์ออนไลน์ ให้ตั้งค่า URL หน้าเว็บจริงไว้ที่นี่ เพื่อให้แชร์ไปยัง Line/Facebook ได้
const SITE_URL = ""; // ตัวอย่าง: "https://yourbrand.com/fortune"

// --- ฐานข้อมูลคำทำนาย (FORTUNE_DATA) ---
const FORTUNE_DATA = [
    { number: 1, headline: "มงคลสูงสุด: โชคใหญ่กำลังมา!", detail: "การงานราบรื่น การเงินโดดเด่น ความรักสมหวังทุกประการ สิ่งที่ตั้งใจจะสำเร็จภายใน 7 วัน ให้ทำบุญด้วยแสงสว่าง", icon: "💰" },
    { number: 2, headline: "ระวังเรื่องปากเสียง: ควรสงบสติอารมณ์", detail: "ช่วงนี้ให้หลีกเลี่ยงการตัดสินใจเรื่องสำคัญ อาจมีเหตุขัดแย้งกับคนใกล้ชิด ให้อุทิศบุญแก่เจ้ากรรมนายเวร", icon: "⚠️" },
    { number: 3, headline: "กัลยาณมิตร: มีคนยื่นมือเข้าช่วย", detail: "เรื่องที่กังวลจะคลี่คลาย มีคนรักหรือเพื่อนร่วมงานที่จริงใจเข้ามาช่วยเหลือ ให้รับฟังและน้อมรับความหวังดีนั้น", icon: "🤝" },
    { number: 4, headline: "ความสำเร็จต้องใช้เวลา: อดทนไว้ก่อน", detail: "อย่าเพิ่งท้อแท้กับอุปสรรคที่เจอ ความสำเร็จจะมาถึงช้ากว่าที่คิด แต่คุ้มค่ากับการรอคอย ให้สวดมนต์ก่อนนอน", icon: "⏳" },
    { number: 5, headline: "การเปลี่ยนแปลงครั้งใหญ่: เตรียมตัวรับมือ", detail: "ชีวิตกำลังจะเข้าสู่ช่วงเปลี่ยนผ่านครั้งสำคัญ ทั้งเรื่องงานและการเงิน การย้ายที่อยู่หรือเริ่มต้นใหม่จะนำพาโชคดีมาให้", icon: "🚀" },
    { number: 6, headline: "สุขภาพดี: ควรออกกำลังกาย", detail: "สุขภาพแข็งแรง แต่ควรหาเวลาพักผ่อนและออกกำลังกายอย่างสม่ำเสมอ ความกังวลเรื่องเล็กน้อยจะหายไป", icon: "🧘" },
    { number: 7, headline: "เดินทางปลอดภัย: ได้พบเจอสิ่งใหม่", detail: "มีเกณฑ์เดินทางไกล ทั้งเรื่องงานและพักผ่อน จะได้พบผู้คนและโอกาสใหม่ๆ ที่ดีต่อชีวิต", icon: "✈️" },
    { number: 8, headline: "ระวังเรื่องเงิน: ควรประหยัด", detail: "การเงินไม่สู้ดีนักในช่วงนี้ ควรระมัดระวังการใช้จ่ายฟุ่มเฟือย และหลีกเลี่ยงการให้คนยืมเงิน", icon: "💸" },
    { number: 9, headline: "ความรักสดใส: มีคนเข้ามาในชีวิต", detail: "สำหรับคนโสด จะมีคนน่าสนใจเข้ามาสานสัมพันธ์ สำหรับคนมีคู่ ความสัมพันธ์จะแน่นแฟ้นขึ้น", icon: "❤️" },
    { number: 10, headline: "โอกาสทางการงาน: ได้เลื่อนตำแหน่ง", detail: "ผลงานเป็นที่ประจักษ์ ผู้ใหญ่เห็นความสามารถ มีโอกาสได้เลื่อนขั้นหรือได้รับมอบหมายงานสำคัญ", icon: "💼" },
    { number: 11, headline: "เรื่องลับจะถูกเปิดเผย: ควรระวังตัว", detail: "สิ่งที่ซ่อนอยู่จะปรากฏขึ้นมา ทั้งเรื่องดีและเรื่องไม่ดี ควรทำทุกอย่างด้วยความสุจริตใจ", icon: "🤫" },
    { number: 12, headline: "ศัตรูพ่ายแพ้: ชัยชนะอยู่ใกล้แค่เอื้อม", detail: "ผู้ที่มุ่งร้ายต่อคุณจะพ่ายแพ้ไปเอง ความดีจะชนะทุกสิ่ง ให้ตั้งมั่นในความถูกต้อง", icon: "⚔️" },
    { number: 13, headline: "ให้รอต่อไป: ยังไม่ถึงเวลาที่เหมาะสม", detail: "สิ่งที่หวังยังไม่บรรลุผลในตอนนี้ อย่ารีบร้อน ให้รอจังหวะที่เหมาะสมกว่านี้", icon: "⏸️" },
    { number: 14, headline: "ความสุขในบ้าน: ครอบครัวเป็นสุข", detail: "เรื่องในครอบครัวจะราบรื่น ไม่มีเรื่องให้กังวลใจ ให้ใช้เวลากับคนที่คุณรักให้มากขึ้น", icon: "🏠" },
    { number: 15, headline: "บุญเก่าส่งผล: ได้รับการอุปถัมภ์", detail: "มีผู้ใหญ่ใจดีเข้ามาให้ความช่วยเหลืออย่างไม่คาดคิด ควรขอบคุณและใช้โอกาสนี้ให้เป็นประโยชน์", icon: "🙏" },
    { number: 16, headline: "ต้องตัดสินใจ: อย่าลังเล", detail: "คุณต้องทำการตัดสินใจครั้งสำคัญ อย่ากลัวความผิดพลาด ให้เชื่อมั่นในสัญชาตญาณตัวเอง", icon: "⚖️" },
    { number: 17, headline: "ปัญหาเล็กน้อย: จะคลี่คลายในเร็ววัน", detail: "อุปสรรคที่คุณเจอเป็นเพียงเรื่องเล็กน้อย จะมีคนเข้ามาช่วยแก้ไขให้ลุล่วงไปได้ด้วยดี", icon: "✅" },
    { number: 18, headline: "ระวังคำพูด: พูดดีเป็นศรีแก่ปาก", detail: "คำพูดของคุณมีผลกระทบต่อผู้อื่นมาก ควรคิดก่อนพูด หลีกเลี่ยงการนินทาว่าร้าย", icon: "🗣️" },
    { number: 19, headline: "ความหวังใหม่: มีโครงการใหม่เกิดขึ้น", detail: "ถึงเวลาเริ่มต้นโปรเจกต์หรือแผนการใหม่ ๆ ที่คุณใฝ่ฝันไว้ ความคิดสร้างสรรค์กำลังพุ่งขึ้น", icon: "💡" },
    { number: 20, headline: "โชคจากการเสี่ยง: ลองเสี่ยงโชคดู", detail: "มีเกณฑ์ได้ลาภลอย หรือโชคจากการเสี่ยงที่ไม่คาดคิด ควรลองซื้อสลากหรือลงทุนเล็กน้อย", icon: "🍀" },
    { number: 21, headline: "การให้อภัย: ปล่อยวางความโกรธ", detail: "การให้อภัยผู้อื่นจะเป็นการปลดปล่อยตัวคุณเอง ความโกรธแค้นจะนำมาซึ่งความทุกข์", icon: "🕊️" },
    { number: 22, headline: "มิตรแท้: ได้เจอเพื่อนร่วมทางที่ดี", detail: "คุณจะได้พบเพื่อนแท้ หรือหุ้นส่วนธุรกิจที่ซื่อสัตย์ การทำงานร่วมกันจะนำไปสู่ความสำเร็จ", icon: "👥" },
    { number: 23, headline: "สิ่งที่ไม่คาดฝัน: จะเกิดขึ้นเร็ว ๆ นี้", detail: "เตรียมรับมือกับเหตุการณ์ที่ไม่ได้วางแผนไว้ แต่ส่วนใหญ่จะเป็นเรื่องที่ดีและน่าตื่นเต้น", icon: "🎁" },
    { number: 24, headline: "การศึกษา: ควรหาความรู้เพิ่มเติม", detail: "เป็นช่วงเวลาที่ดีสำหรับการเรียนรู้ ทักษะใหม่ ๆ ที่ได้มาจะช่วยให้การงานก้าวหน้า", icon: "📚" },
    { number: 25, headline: "พลังงานลบ: ควรสวดมนต์แผ่เมตตา", detail: "รู้สึกไม่สบายใจหรือหดหู่ ควรหันเข้าสู่การปฏิบัติธรรม หรือทำบุญเพื่อปรับสมดุลพลังงาน", icon: "🌑" },
    { number: 26, headline: "การลงทุน: ควรศึกษาข้อมูลให้ดี", detail: "มีโอกาสในการลงทุน แต่ต้องระมัดระวังและศึกษาข้อมูลให้รอบคอบ อย่าใจร้อน", icon: "📈" },
    { number: 27, headline: "ได้รับความยุติธรรม: ปัญหาจะคลี่คลาย", detail: "ความจริงจะปรากฏ ผู้ที่ถูกใส่ร้ายจะได้รับความเป็นธรรมคืนมา", icon: "🛡️" },
    { number: 28, headline: "ความสมหวัง: ทุกสิ่งที่คิดจะสำเร็จ", detail: "คำทำนายที่ดีที่สุด! ทุกสิ่งที่ปรารถนาจะสำเร็จลุล่วงด้วยดี ให้ตั้งใจทำบุญใหญ่", icon: "👑" }
];

// --- Teaser Messages ---
const TEASERS = [
    "โชคดีกำลังมา... 💰 ความรักจะสมหวัง...",
    "ตั้งใจดี สิ่งดีจะเกิดขึ้น ✨",
    "อย่าลืมแผ่เมตตา วันนี้จะใจสงบ 🕊️",
    "โอกาสใหม่กำลังเคาะประตู 💼",
    "เดินทางแล้วได้ลาภ 🍀",
    "สุขภาพดี เริ่มจากใจที่เบิกบาน 🧘"
];

// --- รีวิวลูกค้าจริง (ตัวอย่าง) ---
const REVIEWS = [
    { author: "คุณมิ้นท์", comment: "แม่นมากค่ะ คำทำนายตรงกับสิ่งที่กำลังเจอจริง ๆ", stars: 5 },
    { author: "คุณต้น", comment: "ได้แนวทางแก้ปัญหา ทำให้ตัดสินใจได้ดีขึ้น ขอบคุณครับ", stars: 5 },
    { author: "คุณพลอย", comment: "เสี่ยงหลายรอบ คำทำนายให้กำลังใจดีมาก", stars: 4 },
    { author: "คุณบาส", comment: "ชอบระบบเขย่า สนุกและลื่นไหล คำทำนายอ่านแล้วมีกำลังใจ", stars: 4 }
];

// --- Logic การทำงาน ---

// 1) ฟังก์ชันหลัก: เมื่อผู้ใช้คลิกปุ่ม
function generateFortune() {
    const maxFortune = FORTUNE_DATA.length;
    const randomIndex = Math.floor(Math.random() * maxFortune);
    const result = FORTUNE_DATA[randomIndex];

    animateShaking();

    setTimeout(() => {
        if (result) {
            document.getElementById('fortune-number').textContent = result.number;
            document.getElementById('fortune-headline').innerHTML = `${result.icon} ${result.headline}`;
            document.getElementById('fortune-detail').textContent = result.detail;

            // Persist last fortune
            localStorage.setItem('lastFortuneIndex', String(randomIndex));

            document.getElementById('shaking-section').classList.add('hidden');
            document.getElementById('result-section').classList.remove('hidden');
        } else {
            alert("เกิดข้อผิดพลาดในการดึงคำทำนาย! กรุณาลองใหม่.");
        }
    }, 1500);
}

// 2) Animation เขย่า
function animateShaking() {
    const button = document.getElementById('shaking-button');
    button.textContent = "เขย่า... โปรดรอรับคำทำนาย";
    button.classList.add('shaking-effect');
    setTimeout(() => {
        button.classList.remove('shaking-effect');
        button.textContent = "👉 เสี่ยงเซียมซีตอนนี้";
    }, 1500);
}

// 3) รีเซ็ต
function resetFortune() {
    localStorage.removeItem('lastFortuneIndex');
    document.getElementById('result-section').classList.add('hidden');
    document.getElementById('shaking-section').classList.remove('hidden');
}

// 4) แชร์คำทำนายไปยัง Line / Twitter / Facebook
function getCurrentFortune() {
    const num = document.getElementById('fortune-number').textContent;
    const headline = document.getElementById('fortune-headline').textContent;
    const detail = document.getElementById('fortune-detail').textContent;
    if (!num || !headline) return null;
    return { num, headline, detail };
}

function buildShareText(f) {
    return `${f.headline}\n${f.detail}\n— เซียมซีจาก อ.โทนี่สะท้อนกรรม`;
}

function shareFortune(platform) {
    const f = getCurrentFortune();
    if (!f) {
        alert("ยังไม่มีคำทำนายสำหรับแชร์ กรุณาเสี่ยงเซียมซีก่อน");
        return;
    }
    const text = buildShareText(f);

    // ใช้ Web Share API ถ้ามีและแชร์ข้อความได้
    if (navigator.share) {
        navigator.share({ title: "คำทำนายเซียมซี", text })
            .catch(() => {}); // ไม่ต้องจับ error เป็นพิเศษ
        return;
    }

    // สร้างลิงก์สำหรับแต่ละแพลตฟอร์ม
    const encodedText = encodeURIComponent(text);
    const encodedURL = encodeURIComponent(SITE_URL || "");

    let url = "";
    if (platform === "twitter") {
        url = `https://twitter.com/intent/tweet?text=${encodedText}` + (SITE_URL ? `&url=${encodedURL}` : "");
    } else if (platform === "facebook") {
        if (!SITE_URL) {
            alert("การแชร์ไป Facebook ต้องมี URL หน้าเว็บจริง กรุณาตั้งค่า SITE_URL ในไฟล์ script.js");
            return;
        }
        url = `https://www.facebook.com/sharer/sharer.php?u=${encodedURL}`;
    } else if (platform === "line") {
        if (!SITE_URL) {
            // LINE share รองรับเฉพาะ URL เป็นหลัก
            alert("การแชร์ไป Line ต้องมี URL หน้าเว็บจริง กรุณาตั้งค่า SITE_URL ในไฟล์ script.js");
            return;
        }
        url = `https://social-plugins.line.me/lineit/share?url=${encodedURL}`;
    }

    if (url) {
        window.open(url, "_blank", "noopener,noreferrer");
    }
}

// 5) รีวิวลูกค้า: เติมลง DOM
function renderReviews() {
    const wrap = document.getElementById('reviews-list');
    if (!wrap) return;
    wrap.innerHTML = "";
    REVIEWS.forEach(r => {
        const item = document.createElement('div');
        item.className = "review-item";
        item.innerHTML = `
            <div class="author">${r.author}</div>
            <div class="comment">${r.comment}</div>
            <div class="stars">${"★".repeat(r.stars)}${"☆".repeat(5 - r.stars)}</div>
        `;
        wrap.appendChild(item);
    });
}

// 6) หมุนข้อความ Teaser
function startTeaserRotation() {
    const el = document.getElementById('random-teaser');
    if (!el) return;
    let i = 0;
    el.textContent = TEASERS[0];
    setInterval(() => {
        i = (i + 1) % TEASERS.length;
        el.textContent = TEASERS[i];
    }, 3000);
}

// 7) Restore ผลลัพธ์ล่าสุด
function restoreFortuneIfAny() {
    const idxStr = localStorage.getItem('lastFortuneIndex');
    if (!idxStr) return;
    const idx = parseInt(idxStr, 10);
    const result = FORTUNE_DATA[idx];
    if (!result) return;

    document.getElementById('fortune-number').textContent = result.number;
    document.getElementById('fortune-headline').innerHTML = `${result.icon} ${result.headline}`;
    document.getElementById('fortune-detail').textContent = result.detail;

    document.getElementById('shaking-section').classList.add('hidden');
    document.getElementById('result-section').classList.remove('hidden');
}

// 8) Smooth Scroll สำหรับเมนู
function attachNavSmoothScroll() {
    const links = document.querySelectorAll('header nav a[href^="#"]');
    links.forEach(link => {
        link.addEventListener('click', (e) => {
            const targetId = link.getAttribute('href');
            if (!targetId) return;
            const target = document.querySelector(targetId);
            if (!target) return;
            e.preventDefault();
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
    });
}

// 9) รองรับคีย์บอร์ด
function attachKeyboardSupport() {
    const button = document.getElementById('shaking-button');
    button.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            generateFortune();
        }
    });
}

// 10) ติดตั้ง Event แชร์
function attachShareButtons() {
    const lineBtn = document.getElementById('line-share');
    const twBtn = document.getElementById('twitter-share');
    const fbBtn = document.getElementById('facebook-share');
    if (lineBtn) lineBtn.addEventListener('click', () => shareFortune("line"));
    if (twBtn) twBtn.addEventListener('click', () => shareFortune("twitter"));
    if (fbBtn) fbBtn.addEventListener('click', () => shareFortune("facebook"));
}

// 11) เริ่มต้นระบบเมื่อโหลดหน้า
document.addEventListener('DOMContentLoaded', () => {
    startTeaserRotation();
    renderReviews();
    restoreFortuneIfAny();
    attachNavSmoothScroll();
    attachKeyboardSupport();
    attachShareButtons();
});

// 12) Click หลัก
document.getElementById('shaking-button').addEventListener('click', generateFortune);