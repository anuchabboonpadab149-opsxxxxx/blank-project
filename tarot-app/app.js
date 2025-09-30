/* ========= DECK DATA ========= */

const TAROT_DECK = [
  // Major Arcana
  { key: "MA_0", en: "The Fool", th: "The Fool (คนโง่)", arcana: "Major", suit: null, number: 0,
    upright: "การเริ่มต้นใหม่ อิสระ การเดินทางโดยเชื่อใจหัวใจของตนเอง",
    reversed: "ขาดแผนการ ความสะเพร่า ลังเล ไม่กล้าก้าว" },
  { key: "MA_1", en: "The Magician", th: "The Magician (นักมายากล)", arcana: "Major", suit: null, number: 1,
    upright: "พลังสร้างสรรค์ ควบคุมทรัพยากรได้ดี เริ่มลงมือทำ",
    reversed: "ใช้กลอุบาย ขาดทิศทาง พลังงานกระจัดกระจาย" },
  { key: "MA_2", en: "The High Priestess", th: "The High Priestess (สตรีนักบวช)", arcana: "Major", suit: null, number: 2,
    upright: "สัญชาตญาณ ความลับ การฟังเสียงภายใน",
    reversed: "สับสน ปกปิดตนเอง ไม่เชื่อสัญชาตญาณ" },
  { key: "MA_3", en: "The Empress", th: "The Empress (จักรพรรดินี)", arcana: "Major", suit: null, number: 3,
    upright: "ความอุดมสมบูรณ์ ความรัก การดูแล เอื้ออาทร",
    reversed: "ฟุ่มเฟือย ขาดการดูแลตนเอง หรือให้มากเกินไป" },
  { key: "MA_4", en: "The Emperor", th: "The Emperor (จักรพรรดิ)", arcana: "Major", suit: null, number: 4,
    upright: "โครงสร้าง ระเบียบ ความมั่นคง ภาวะผู้นำ",
    reversed: "เผด็จการ แข็งกร้าว ควบคุมมากเกินไป" },
  { key: "MA_5", en: "The Hierophant", th: "The Hierophant (พระสังฆราช)", arcana: "Major", suit: null, number: 5,
    upright: "ขนบธรรมเนียม ครูผู้สอน คำแนะนำตามหลักการ",
    reversed: "กบฏ ต่อต้านกฎเกณฑ์ แนวทางนอกกรอบ" },
  { key: "MA_6", en: "The Lovers", th: "The Lovers (คนรัก)", arcana: "Major", suit: null, number: 6,
    upright: "ความรัก ความสามัคคี ทางเลือกที่สอดคล้องกับคุณค่า",
    reversed: "ความไม่ลงรอย การตัดสินใจผิด ความสัมพันธ์ไม่สมดุล" },
  { key: "MA_7", en: "The Chariot", th: "The Chariot (รถศึก)", arcana: "Major", suit: null, number: 7,
    upright: "มุ่งมั่น ชัยชนะ ควบคุมอารมณ์และทิศทาง",
    reversed: "หลุดโฟกัส ควบคุมไม่ได้ หุนหันพลันแล่น" },
  { key: "MA_8", en: "Strength", th: "Strength (พละกำลัง)", arcana: "Major", suit: null, number: 8,
    upright: "ความกล้าหาญ อดทน ควบคุมตนเองด้วยความเมตตา",
    reversed: "ขาดความเชื่อมั่น โกรธง่าย ใช้พลังผิดทาง" },
  { key: "MA_9", en: "The Hermit", th: "The Hermit (ฤาษี)", arcana: "Major", suit: null, number: 9,
    upright: "สันโดษ แสวงหาความจริง ไตร่ตรองภายใน",
    reversed: "โดดเดี่ยวเกินไป ปิดกั้นคำแนะนำจากผู้อื่น" },
  { key: "MA_10", en: "Wheel of Fortune", th: "Wheel of Fortune (กงล้อแห่งโชคชะตา)", arcana: "Major", suit: null, number: 10,
    upright: "การเปลี่ยนแปลงตามวงจร โชคดี โอกาสใหม่",
    reversed: "ติดขัด ดวงตก รู้สึกควบคุมอะไรไม่ได้" },
  { key: "MA_11", en: "Justice", th: "Justice (ความยุติธรรม)", arcana: "Major", suit: null, number: 11,
    upright: "ความจริง ความยุติธรรม การรับผิดชอบต่อการตัดสินใจ",
    reversed: "ความไม่ยุติธรรม ลำเอียง หลีกเลี่ยงความจริง" },
  { key: "MA_12", en: "The Hanged Man", th: "The Hanged Man (ชายแขวนคอ)", arcana: "Major", suit: null, number: 12,
    upright: "มุมมองใหม่ การหยุดพักและยอมสละเพื่อสิ่งที่ใหญ่กว่า",
    reversed: "ติดอยู่ ไม่ยอมเปลี่ยน มองไม่เห็นทางออก" },
  { key: "MA_13", en: "Death", th: "Death (ความตาย)", arcana: "Major", suit: null, number: 13,
    upright: "การสิ้นสุดที่จำเป็น เริ่มต้นใหม่ ปลดปล่อยจากสิ่งเดิม",
    reversed: "กลัวการเปลี่ยนแปลง ยึดติดอดีต วงจรซ้ำ" },
  { key: "MA_14", en: "Temperance", th: "Temperance (ความพอดี)", arcana: "Major", suit: null, number: 14,
    upright: "สมดุล ประสานสิ่งต่างๆ อย่างลงตัว เยียวยา",
    reversed: "สุดโต่ง ขาดความอดทน ผสมผสานไม่ลงตัว" },
  { key: "MA_15", en: "The Devil", th: "The Devil (ปีศาจ)", arcana: "Major", suit: null, number: 15,
    upright: "พันธนาการ ความยึดติด การเสพติด วัตถุนิยม",
    reversed: "ตระหนักรู้และปลดปล่อย เปลี่ยนนิสัยที่ฉุดรั้ง" },
  { key: "MA_16", en: "The Tower", th: "The Tower (หอคอย)", arcana: "Major", suit: null, number: 16,
    upright: "การพังทลายฉับพลัน ความจริงกระแทก ฟ้าแลบ",
    reversed: "ความเสียหายลดระดับ หนีปัญหาแต่ยังต้องรับมือ" },
  { key: "MA_17", en: "The Star", th: "The Star (ดาว)", arcana: "Major", suit: null, number: 17,
    upright: "ความหวัง การเยียวยา ความศรัทธาในเส้นทาง",
    reversed: "หมดแรง ขาดศรัทธา มองไม่เห็นแสงสว่าง" },
  { key: "MA_18", en: "The Moon", th: "The Moon (พระจันทร์)", arcana: "Major", suit: null, number: 18,
    upright: "สัญชาตญาณ ความฝัน ความสับสน ต้องฟังใจให้มากขึ้น",
    reversed: "ความจริงเปิดเผย คลายความกลัว สัญชาตญาณชัดเจนขึ้น" },
  { key: "MA_19", en: "The Sun", th: "The Sun (พระอาทิตย์)", arcana: "Major", suit: null, number: 19,
    upright: "ความสุข ความสำเร็จ ความชัดเจน พลังชีวิต",
    reversed: "ดีแต่ช้าลง ความคาดหวังเกินจริง หรือความสุขชั่วคราว" },
  { key: "MA_20", en: "Judgement", th: "Judgement (การพิพากษา)", arcana: "Major", suit: null, number: 20,
    upright: "ตื่นรู้ การปลุกพลังใหม่ การทบทวนและตัดสินใจ",
    reversed: "กลัวการตัดสิน ผัดวันประกันพรุ่ง ยึดติดอดีต" },
  { key: "MA_21", en: "The World", th: "The World (โลก)", arcana: "Major", suit: null, number: 21,
    upright: "จบวัฏจักรอย่างสมบูรณ์ บรรลุเป้าหมาย เริ่มบทใหม่",
    reversed: "เรื่องยังไม่จบ วนซ้ำ ต้องปิดงานให้สำเร็จ" },

  // Cups (ความรู้สึก/ความสัมพันธ์)
  { key: "CU_1", en: "Ace of Cups", th: "Ace of Cups (เอซ ถ้วย)", arcana: "Minor", suit: "Cups", number: 1,
    upright: "เริ่มต้นความรัก/ความรู้สึกใหม่ หัวใจเปิดรับ",
    reversed: "อารมณ์ล้น ไม่มั่นคง ปิดกั้นความรู้สึก" },
  { key: "CU_2", en: "Two of Cups", th: "Two of Cups (ถ้วย 2)", arcana: "Minor", suit: "Cups", number: 2,
    upright: "ความสัมพันธ์ที่สมดุล หุ้นส่วนที่เกื้อหนุน",
    reversed: "ความไม่สมดุล เข้าใจผิด การเชื่อมต่อที่สั่นคลอน" },
  { key: "CU_3", en: "Three of Cups", th: "Three of Cups (ถ้วย 3)", arcana: "Minor", suit: "Cups", number: 3,
    upright: "การเฉลิมฉลอง เพื่อน ความสุขร่วมกัน",
    reversed: "ใช้ชีวิตมากเกิน ขาดสมดุล กลุ่มปิดกั้น" },
  { key: "CU_4", en: "Four of Cups", th: "Four of Cups (ถ้วย 4)", arcana: "Minor", suit: "Cups", number: 4,
    upright: "เฉื่อยชา ไม่สนใจสิ่งที่มี โอกาสลอยมาแต่ไม่รับ",
    reversed: "ตื่นจากภวังค์ เปิดใจรับโอกาสใหม่" },
  { key: "CU_5", en: "Five of Cups", th: "Five of Cups (ถ้วย 5)", arcana: "Minor", suit: "Cups", number: 5,
    upright: "ความเสียใจ มองสิ่งที่หายไปมากกว่าสิ่งที่ยังมี",
    reversed: "เยียวยา กลับมามองด้านบวก เดินต่อ" },
  { key: "CU_6", en: "Six of Cups", th: "Six of Cups (ถ้วย 6)", arcana: "Minor", suit: "Cups", number: 6,
    upright: "ความทรงจำที่ดี กลับไปหาอดีต ความอบอุ่น",
    reversed: "ติดอดีต ไม่กล้าก้าวไปข้างหน้า" },
  { key: "CU_7", en: "Seven of Cups", th: "Seven of Cups (ถ้วย 7)", arcana: "Minor", suit: "Cups", number: 7,
    upright: "ตัวเลือกมากมาย จินตนาการสูง ต้องโฟกัส",
    reversed: "เลือกอย่างชัดเจน ลดฝันเฟื่อง ลงมือจริง" },
  { key: "CU_8", en: "Eight of Cups", th: "Eight of Cups (ถ้วย 8)", arcana: "Minor", suit: "Cups", number: 8,
    upright: "เดินจากสิ่งที่ไม่เติมเต็ม แสวงหาคุณค่าใหม่",
    reversed: "กลับไปหาอดีต ยึดติด ทั้งที่ควรก้าวต่อ" },
  { key: "CU_9", en: "Nine of Cups", th: "Nine of Cups (ถ้วย 9)", arcana: "Minor", suit: "Cups", number: 9,
    upright: "ความสมหวัง พึงพอใจในสิ่งที่มี",
    reversed: "ความฟุ่มเฟือย พอใจชั่วคราว ไม่ลึกซึ้ง" },
  { key: "CU_10", en: "Ten of Cups", th: "Ten of Cups (ถ้วย 10)", arcana: "Minor", suit: "Cups", number: 10,
    upright: "ครอบครัวสุขใจ ความสุขร่วมกัน ความสมบูรณ์ทางใจ",
    reversed: "ความคาดหวังต่อครอบครัวไม่ตรงกัน ความตึงเครียด" },
  { key: "CU_11", en: "Page of Cups", th: "Page of Cups (เด็ก ถ้วย)", arcana: "Minor", suit: "Cups", number: 11,
    upright: "ความคิดสร้างสรรค์ทางอารมณ์ ข่าวดี/สารจากใจ",
    reversed: "อ่อนไหวเกินไป ปิดกั้นความคิดสร้างสรรค์" },
  { key: "CU_12", en: "Knight of Cups", th: "Knight of Cups (อัศวิน ถ้วย)", arcana: "Minor", suit: "Cups", number: 12,
    upright: "การตามหัวใจ โรแมนติก เสนอข่าวดี",
    reversed: "อารมณ์ขึ้นลง ฝันมากกว่าลงมือ" },
  { key: "CU_13", en: "Queen of Cups", th: "Queen of Cups (ราชินี ถ้วย)", arcana: "Minor", suit: "Cups", number: 13,
    upright: "ความเมตตา เข้าอกเข้าใจ ดูแลใจคนอื่น",
    reversed: "อารมณ์เปราะบาง เก็บความรู้สึกมากไป" },
  { key: "CU_14", en: "King of Cups", th: "King of Cups (ราชา ถ้วย)", arcana: "Minor", suit: "Cups", number: 14,
    upright: "สมดุลอารมณ์ ผู้นำที่อ่อนโยน",
    reversed: "กดอารมณ์ไว้ ไม่ซื่อสัตย์ต่อความรู้สึก" },

  // Swords (ความคิด/การสื่อสาร/ความท้าทาย)
  { key: "SW_1", en: "Ace of Swords", th: "Ace of Swords (เอซ ดาบ)", arcana: "Minor", suit: "Swords", number: 1,
    upright: "ความชัดเจน ความจริง ไอเดียใหม่ที่คมชัด",
    reversed: "สับสน สื่อสารผิดพลาด ความจริงถูกบิดเบือน" },
  { key: "SW_2", en: "Two of Swords", th: "Two of Swords (ดาบ 2)", arcana: "Minor", suit: "Swords", number: 2,
    upright: "ชั่งใจ ตัดสินใจยาก ปิดตาชั่วคราว",
    reversed: "เปิดตารับความจริง ตัดสินใจที่คั่งค้าง" },
  { key: "SW_3", en: "Three of Swords", th: "Three of Swords (ดาบ 3)", arcana: "Minor", suit: "Swords", number: 3,
    upright: "ความเจ็บปวด การแตกหัก การถูกทำร้ายทางใจ",
    reversed: "เยียวยา ปลดปล่อยความเจ็บปวด เรียนรู้" },
  { key: "SW_4", en: "Four of Swords", th: "Four of Swords (ดาบ 4)", arcana: "Minor", suit: "Swords", number: 4,
    upright: "พักฟื้น พักใจ วางแผนใหม่",
    reversed: "พักมากเกินไป หรือพักไม่พอ ความเครียดสะสม" },
  { key: "SW_5", en: "Five of Swords", th: "Five of Swords (ดาบ 5)", arcana: "Minor", suit: "Swords", number: 5,
    upright: "ชนะด้วยวิธีที่ไม่งาม ความขัดแย้ง สูญเสียความไว้ใจ",
    reversed: "ยุติความขัดแย้ง ยอมปล่อยวางเพื่อความสงบ" },
  { key: "SW_6", en: "Six of Swords", th: "Six of Swords (ดาบ 6)", arcana: "Minor", suit: "Swords", number: 6,
    upright: "เคลื่อนตัวไปสู่ที่ดีขึ้น ฟื้นตัวจากความทุกข์",
    reversed: "ติดอยู่ ไม่ยอมขยับ เปลี่ยนแปลงไม่ได้" },
  { key: "SW_7", en: "Seven of Swords", th: "Seven of Swords (ดาบ 7)", arcana: "Minor", suit: "Swords", number: 7,
    upright: "กลยุทธ์ ลับๆ ล่อๆ ระวังการคดโกง",
    reversed: "เปิดเผยความจริง ยอมรับความผิดพลาด" },
  { key: "SW_8", en: "Eight of Swords", th: "Eight of Swords (ดาบ 8)", arcana: "Minor", suit: "Swords", number: 8,
    upright: "ติดกับความคิด กังวล พันธนาการตนเอง",
    reversed: "ปลดปล่อยจากกรอบ คิดใหม่ทำใหม่" },
  { key: "SW_9", en: "Nine of Swords", th: "Nine of Swords (ดาบ 9)", arcana: "Minor", suit: "Swords", number: 9,
    upright: "กังวล นอนไม่หลับ ความเครียดเล่นงาน",
    reversed: "ความกังวลลดลง เรียนรู้รับมือความกลัว" },
  { key: "SW_10", en: "Ten of Swords", th: "Ten of Swords (ดาบ 10)", arcana: "Minor", suit: "Swords", number: 10,
    upright: "จบสิ้นอย่างเจ็บปวด แต่เป็นจุดเริ่มใหม่",
    reversed: "เจ็บปวดยืดเยื้อ ปล่อยไม่ลง วงจรซ้ำ" },
  { key: "SW_11", en: "Page of Swords", th: "Page of Swords (เด็ก ดาบ)", arcana: "Minor", suit: "Swords", number: 11,
    upright: "อยากรู้อยากเห็น สื่อสารไว ระมัดระวังคำพูด",
    reversed: "ข่าวลือ พูดโดยไม่คิด ความจริงครึ่งๆกลางๆ" },
  { key: "SW_12", en: "Knight of Swords", th: "Knight of Swords (อัศวิน ดาบ)", arcana: "Minor", suit: "Swords", number: 12,
    upright: "พุ่งชน เป้าหมายชัด แต่เสี่ยงชนสิ่งรอบข้าง",
    reversed: "หุนหัน ขาดไตร่ตรอง ทำให้เกิดความเสียหาย" },
  { key: "SW_13", en: "Queen of Swords", th: "Queen of Swords (ราชินี ดาบ)", arcana: "Minor", suit: "Swords", number: 13,
    upright: "เหตุผลชัดเจน ขีดเส้นตาย ความจริงตรงไปตรงมา",
    reversed: "เย็นชา วิจารณ์แรง ปิดกั้นหัวใจ" },
  { key: "SW_14", en: "King of Swords", th: "King of Swords (ราชา ดาบ)", arcana: "Minor", suit: "Swords", number: 14,
    upright: "ความคิดเป็นระบบ ยุติธรรม ผู้นำทางปัญญา",
    reversed: "เผด็จการทางความคิด ใช้อำนาจเกินพอดี" },

  // Wands (แรงบันดาลใจ/การงาน/การลงมือทำ)
  { key: "WA_1", en: "Ace of Wands", th: "Ace of Wands (เอซ ไม้เท้า)", arcana: "Minor", suit: "Wands", number: 1,
    upright: "ประกายใหม่ โอกาสทางงาน/โปรเจกต์ จุดไฟสร้างสรรค์",
    reversed: "แรงบันดาลใจดับ เหนื่อยล้า ชะลอการเริ่มต้น" },
  { key: "WA_2", en: "Two of Wands", th: "Two of Wands (ไม้เท้า 2)", arcana: "Minor", suit: "Wands", number: 2,
    upright: "วางแผน มองไกล เลือกทางเดิน",
    reversed: "ลังเล กลัวการเปลี่ยนแปลง อยู่ในกรอบเดิม" },
  { key: "WA_3", en: "Three of Wands", th: "Three of Wands (ไม้เท้า 3)", arcana: "Minor", suit: "Wands", number: 3,
    upright: "โอกาสขยายตัว การเดินทาง ความคืบหน้า",
    reversed: "ล่าช้า โอกาสพลาด หรือรอคอยนานเกินไป" },
  { key: "WA_4", en: "Four of Wands", th: "Four of Wands (ไม้เท้า 4)", arcana: "Minor", suit: "Wands", number: 4,
    upright: "เฉลิมฉลอง ความมั่นคงในบ้าน/ทีม",
    reversed: "ความมั่นคงสั่นคลอน งานเลี้ยงที่ไม่เป็นใจ" },
  { key: "WA_5", en: "Five of Wands", th: "Five of Wands (ไม้เท้า 5)", arcana: "Minor", suit: "Wands", number: 5,
    upright: "การแข่งขัน ความเห็นต่าง ฝึกฝนทักษะ",
    reversed: "ความขัดแย้งรุนแรงหรือถูกกดทับ เสียพลังไปเปล่าๆ" },
  { key: "WA_6", en: "Six of Wands", th: "Six of Wands (ไม้เท้า 6)", arcana: "Minor", suit: "Wands", number: 6,
    upright: "ชัยชนะ การยอมรับ ความภาคภูมิใจ",
    reversed: "ยึดติดคำชม ชัยชะนะแบบฉาบฉวย" },
  { key: "WA_7", en: "Seven of Wands", th: "Seven of Wands (ไม้เท้า 7)", arcana: "Minor", suit: "Wands", number: 7,
    upright: "ปกป้องจุดยืน สู้ต่อไป แม้ถูกกดดัน",
    reversed: "เหนื่อยล้า ยอมถอย หรือป้องกันมากเกินไป" },
  { key: "WA_8", en: "Eight of Wands", th: "Eight of Wands (ไม้เท้า 8)", arcana: "Minor", suit: "Wands", number: 8,
    upright: "เร็ว ข่าวดี การสื่อสารฉับไว",
    reversed: "ล่าช้า ข้อมูลติดขัด ติดต่อไม่สะดวก" },
  { key: "WA_9", en: "Nine of Wands", th: "Nine of Wands (ไม้เท้า 9)", arcana: "Minor", suit: "Wands", number: 9,
    upright: "ยืนหยัด แม้เหนื่อย ยังไม่ยอมแพ้",
    reversed: "หมดแรง ป้องกันเกินไป ไม่ไว้ใจใคร" },
  { key: "WA_10", en: "Ten of Wands", th: "Ten of Wands (ไม้เท้า 10)", arcana: "Minor", suit: "Wands", number: 10,
    upright: "ภาระหนัก แบกหลายอย่าง แต่ใกล้ถึงเส้นชัย",
    reversed: "แบกมากเกินไป จำเป็นต้องปล่อยหรือลดภาระ" },
  { key: "WA_11", en: "Page of Wands", th: "Page of Wands (เด็ก ไม้เท้า)", arcana: "Minor", suit: "Wands", number: 11,
    upright: "ข่าวดีเรื่องงาน/โปรเจกต์ ทดลองสิ่งใหม่",
    reversed: "วู่วาม ไร้ทิศทาง เริ่มแล้วเลิก" },
  { key: "WA_12", en: "Knight of Wands", th: "Knight of Wands (อัศวิน ไม้เท้า)", arcana: "Minor", suit: "Wands", number: 12,
    upright: "พลังแรง บุกตะลุย การผจญภัย",
    reversed: "หุนหัน โครงการล่ม ล้มเหลวเพราะรีบ" },
  { key: "WA_13", en: "Queen of Wands", th: "Queen of Wands (ราชินี ไม้เท้า)", arcana: "Minor", suit: "Wands", number: 13,
    upright: "เสน่ห์ ความมั่นใจ บริหารงานอย่างอุ่นใจ",
    reversed: "อิจฉา ขาดความเชื่อมั่น หรือควบคุมมากไป" },
  { key: "WA_14", en: "King of Wands", th: "King of Wands (ราชา ไม้เท้า)", arcana: "Minor", suit: "Wands", number: 14,
    upright: "วิสัยทัศน์ ผู้นำเชิงปฏิบัติ กล้าตัดสินใจ",
    reversed: "เผด็จการ ใจร้อน ใช้อำนาจผิดที่" },

  // Pentacles (เงิน/งานรูปธรรม/ทรัพย์สิน)
  { key: "PE_1", en: "Ace of Pentacles", th: "Ace of Pentacles (เอซ เหรียญ)", arcana: "Minor", suit: "Pentacles", number: 1,
    upright: "โอกาสทางการเงิน/งานใหม่ ฐานมั่นคง",
    reversed: "โอกาสหลุดมือ ขาดการวางแผนทางการเงิน" },
  { key: "PE_2", en: "Two of Pentacles", th: "Two of Pentacles (เหรียญ 2)", arcana: "Minor", suit: "Pentacles", number: 2,
    upright: "จัดสมดุลการเงิน/งานหลายด้าน เล่นแร่แปรธาตุได้ดี",
    reversed: "จัดการไม่ทัน ล้มเหลวในสมดุล หนี้สินเพิ่ม" },
  { key: "PE_3", en: "Three of Pentacles", th: "Three of Pentacles (เหรียญ 3)", arcana: "Minor", suit: "Pentacles", number: 3,
    upright: "งานทีม งานฝีมือ การยอมรับจากผู้เชี่ยวชาญ",
    reversed: "ทีมขาดประสิทธิภาพ ขาดมาตรฐาน งานไม่ละเอียด" },
  { key: "PE_4", en: "Four of Pentacles", th: "Four of Pentacles (เหรียญ 4)", arcana: "Minor", suit: "Pentacles", number: 4,
    upright: "เก็บออม รักษาความปลอดภัย ยึดสิ่งที่มี",
    reversed: "ยึดติดมากไป หรือใช้เงินสุรุ่ยสุร่าย" },
  { key: "PE_5", en: "Five of Pentacles", th: "Five of Pentacles (เหรียญ 5)", arcana: "Minor", suit: "Pentacles", number: 5,
    upright: "ความยากลำบากทางการเงิน/สุขภาพ แต่ยังมีความช่วยเหลือ",
    reversed: "ฟื้นตัว หาโอกาสใหม่ พึ่งพาชุมชน" },
  { key: "PE_6", en: "Six of Pentacles", th: "Six of Pentacles (เหรียญ 6)", arcana: "Minor", suit: "Pentacles", number: 6,
    upright: "ให้และรับอย่างสมดุล การสนับสนุนทางการเงิน",
    reversed: "ให้มากไป/รับมากไป ไม่เท่าเทียม มีเงื่อนไข" },
  { key: "PE_7", en: "Seven of Pentacles", th: "Seven of Pentacles (เหรียญ 7)", arcana: "Minor", suit: "Pentacles", number: 7,
    upright: "อดทน รอผล การลงทุนระยะยาว",
    reversed: "ใจร้อน ไม่เห็นผล ล้มเลิกก่อนเวลา" },
  { key: "PE_8", en: "Eight of Pentacles", th: "Eight of Pentacles (เหรียญ 8)", arcana: "Minor", suit: "Pentacles", number: 8,
    upright: "ฝึกฝนทักษะ งานละเอียด พัฒนาต่อเนื่อง",
    reversed: "เบื่อหน่าย งานซ้ำซาก คุณภาพตก" },
  { key: "PE_9", en: "Nine of Pentacles", th: "Nine of Pentacles (เหรียญ 9)", arcana: "Minor", suit: "Pentacles", number: 9,
    upright: "ความมั่งคั่งส่วนตัว ความเป็นอิสระ ภูมิใจในผลงาน",
    reversed: "พึ่งพาคนอื่น ใช้จ่ายเกินตัว หรือโดดเดี่ยว" },
  { key: "PE_10", en: "Ten of Pentacles", th: "Ten of Pentacles (เหรียญ 10)", arcana: "Minor", suit: "Pentacles", number: 10,
    upright: "ทรัพย์สิน ครอบครัว ความมั่นคงรุ่นสู่รุ่น",
    reversed: "ทรัพย์สินมีปัญหา ความขัดแย้งในครอบครัว/มรดก" },
  { key: "PE_11", en: "Page of Pentacles", th: "Page of Pentacles (เด็ก เหรียญ)", arcana: "Minor", suit: "Pentacles", number: 11,
    upright: "ข่าวดีด้านงาน/เงิน เรียนรู้ทักษะใหม่",
    reversed: "ขาดสมาธิ ใช้ทรัพยากรไม่เกิดผล" },
  { key: "PE_12", en: "Knight of Pentacles", th: "Knight of Pentacles (อัศวิน เหรียญ)", arcana: "Minor", suit: "Pentacles", number: 12,
    upright: "สม่ำเสมอ เชื่อถือได้ ทำงานหนัก มีวินัย",
    reversed: "ดื้อ ช้าเกินไป หรือทำงานแบบเครื่องจักร" },
  { key: "PE_13", en: "Queen of Pentacles", th: "Queen of Pentacles (ราชินี เหรียญ)", arcana: "Minor", suit: "Pentacles", number: 13,
    upright: "ดูแลบ้าน/การเงินอย่างอบอุ่น สมดุลชีวิต",
    reversed: "ดูแลคนอื่นจนลืมตนเอง ใช้เงินเพื่อปลอบใจ" },
  { key: "PE_14", en: "King of Pentacles", th: "King of Pentacles (ราชา เหรียญ)", arcana: "Minor", suit: "Pentacles", number: 14,
    upright: "มั่งคั่ง มั่นคง นักบริหารที่ปฏิบัติได้จริง",
    reversed: "ยึดติดวัตถุ โลภ ใช้อำนาจเพื่อผลประโยชน์" },
];

/* ========= UTILITIES ========= */

// Seeded RNG (xmur3 + mulberry32)
function xmur3(str) {
  let h = 1779033703 ^ str.length;
  for (let i = 0; i < str.length; i++) {
    h = Math.imul(h ^ str.charCodeAt(i), 3432918353);
    h = (h << 13) | (h >>> 19);
  }
  return function() {
    h = Math.imul(h ^ (h >>> 16), 2246822507);
    h = Math.imul(h ^ (h >>> 13), 3266489909);
    return (h ^= h >>> 16) >>> 0;
  };
}
function mulberry32(a) {
  return function() {
    let t = (a += 0x6D2B79F5);
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
function createSeededRng(seedStr) {
  const seedFn = xmur3(seedStr);
  return mulberry32(seedFn());
}
function shuffle(rng, arr) {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}
function randomOrientation(rng) {
  return rng() < 0.5 ? "upright" : "reversed";
}
function dateSeed(scope) {
  const now = new Date();
  if (scope === "year") return `${now.getFullYear()}`;
  if (scope === "month") return `${now.getFullYear()}-${now.getMonth() + 1}`;
  return `${now.getFullYear()}-${now.getMonth() + 1}-${now.getDate()}`;
}

/* ========= AUTH & API ========= */

const el = {
  // Reading
  userName: document.getElementById("userName"),
  readingType: document.getElementById("readingType"),
  focusBtn: document.getElementById("focusBtn"),
  shuffleBtn: document.getElementById("shuffleBtn"),
  cutBtn: document.getElementById("cutBtn"),
  startReadingBtn: document.getElementById("startReadingBtn"),
  deck: document.getElementById("deck"),
  spreadBoard: document.getElementById("spreadBoard"),
  resultsList: document.getElementById("resultsList"),
  dailyScope: document.getElementById("dailyScope"),
  dailyReadBtn: document.getElementById("dailyReadBtn"),
  dailyResults: document.getElementById("dailyResults"),
  // Siemsee
  siemseeName: document.getElementById("siemseeName"),
  siemseeTemple: document.getElementById("siemseeTemple"),
  siemseeShakeBtn: document.getElementById("seamseeShakeBtn"),
  siemseeDrawBtn: document.getElementById("siemseeDrawBtn"),
  siemseeCylinder: document.getElementById("siemseeCylinder"),
  siemseeResult: document.getElementById("siemseeResult"),
  // Account
  accountPanel: document.getElementById("accountPanel"),
  loginBtn: document.getElementById("loginBtn"),
  // Modals
  overlay: document.getElementById("modalOverlay"),
  authModal: document.getElementById("authModal"),
  authClose: document.getElementById("authClose"),
  tabLogin: document.getElementById("tabLogin"),
  tabSignup: document.getElementById("tabSignup"),
  loginPane: document.getElementById("loginPane"),
  signupPane: document.getElementById("signupPane"),
  loginPhone: document.getElementById("loginPhone"),
  loginPassword: document.getElementById("loginPassword"),
  doLogin: document.getElementById("doLogin"),
  signupName: document.getElementById("signupName"),
  signupPhone: document.getElementById("signupPhone"),
  signupPassword: document.getElementById("signupPassword"),
  doSignup: document.getElementById("doSignup"),
  // Topup
  topupModal: document.getElementById("topupModal"),
  topupClose: document.getElementById("topupClose"),
  packageGrid: document.getElementById("packageGrid"),
  paymentPane: document.getElementById("paymentPane"),
  selectedPackageText: document.getElementById("selectedPackageText"),
  qrImage: document.getElementById("qrImage"),
  orderId: document.getElementById("orderId"),
  verifyBtn: document.getElementById("verifyBtn"),
  cancelTopup: document.getElementById("cancelTopup"),
};

let workingDeck = [...TAROT_DECK];
let currentOrderId = null;

const TOKEN_KEY = "ts_token";
function setToken(token) { localStorage.setItem(TOKEN_KEY, token); }
function getToken() { return localStorage.getItem(TOKEN_KEY) || ""; }
function clearToken() { localStorage.removeItem(TOKEN_KEY); }

const API_BASE = window.API_BASE || "";
async function api(path, method = "GET", body = null) {
  const headers = { "Content-Type": "application/json" };
  const token = getToken();
  if (token) headers["Authorization"] = "Bearer " + token;
  const res = await fetch(`${API_BASE}/api${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const msg = data && (data.error || data.message) ? (data.error || data.message) : res.statusText;
    throw new Error(msg);
  }
  return data;
}
async function getMe() {
  try { return await api("/me", "GET"); } catch { return null; }
}

/* ========= ACCOUNT UI ========= */

function updateAccountPanel() {
  const panel = el.accountPanel;
  panel.innerHTML = "";
  const token = getToken();
  if (!token) {
    const btn = document.createElement("button");
    btn.id = "loginBtn";
    btn.className = "primary";
    btn.textContent = "เข้าสู่ระบบ/สมัครสมาชิก";
    btn.addEventListener("click", () => openAuthModal());
    panel.appendChild(btn);
  } else {
    getMe().then((me) => {
      const name = document.createElement("div");
      name.className = "name";
      name.textContent = `สวัสดี, ${me?.name || "สมาชิก"}`;
      const credits = document.createElement("div");
      credits.className = "badge";
      credits.textContent = `สิทธิ์คงเหลือ: ${me?.credits ?? 0}`;
      const topup = document.createElement("button");
      topup.id = "topupBtn";
      topup.textContent = "เติมสิทธิ์";
      topup.addEventListener("click", () => openTopupModal());
      const logout = document.createElement("button");
      logout.className = "ghost";
      logout.textContent = "ออกจากระบบ";
      logout.addEventListener("click", () => logoutUser());
      panel.appendChild(name);
      panel.appendChild(credits);
      panel.appendChild(topup);
      panel.appendChild(logout);
    }).catch(() => {
      clearToken();
      updateAccountPanel();
    });
  }
}
function logoutUser() {
  clearToken();
  updateAccountPanel();
}

/* ========= AUTH MODAL ========= */

function openAuthModal() {
  el.overlay.classList.remove("hidden");
  el.authModal.classList.remove("hidden");
}
function closeAuthModal() {
  el.overlay.classList.add("hidden");
  el.authModal.classList.add("hidden");
}
function switchTab(tab) {
  if (tab === "login") {
    el.tabLogin.classList.add("active");
    el.tabSignup.classList.remove("active");
    el.loginPane.classList.remove("hidden");
    el.signupPane.classList.add("hidden");
  } else {
    el.tabSignup.classList.add("active");
    el.tabLogin.classList.remove("active");
    el.signupPane.classList.remove("hidden");
    el.loginPane.classList.add("hidden");
  }
}
async function signup() {
  const name = (el.signupName.value || "").trim();
  const phone = (el.signupPhone.value || "").trim();
  const password = (el.signupPassword.value || "").trim();
  if (!name || !phone || !password) {
    alert("กรุณากรอกข้อมูลให้ครบ");
    return;
  }
  try {
    const resp = await api("/signup", "POST", { name, phone, password });
    if (resp && resp.token) {
      setToken(resp.token);
      closeAuthModal();
      updateAccountPanel();
    } else {
      alert("สมัครสมาชิกไม่สำเร็จ");
    }
  } catch (e) {
    alert(e.message || "สมัครสมาชิกไม่สำเร็จ");
  }
}
async function login() {
  const phone = (el.loginPhone.value || "").trim();
  const password = (el.loginPassword.value || "").trim();
  if (!phone || !password) {
    alert("กรุณากรอกเบอร์และรหัสผ่าน");
    return;
  }
  try {
    const resp = await api("/login", "POST", { phone, password });
    if (resp && resp.token) {
      setToken(resp.token);
      closeAuthModal();
      updateAccountPanel();
    } else {
      alert("เข้าสู่ระบบไม่สำเร็จ");
    }
  } catch (e) {
    alert(e.message || "เข้าสู่ระบบไม่สำเร็จ");
  }
}

/* ========= TOPUP ========= */

function openTopupModal() {
  if (!ensureAuth()) return;
  el.overlay.classList.remove("hidden");
  el.topupModal.classList.remove("hidden");
  el.paymentPane.classList.add("hidden");
  renderPackages();
}
function closeTopupModal() {
  el.overlay.classList.add("hidden");
  el.topupModal.classList.add("hidden");
  el.paymentPane.classList.add("hidden");
}
async function renderPackages() {
  el.packageGrid.innerHTML = "";
  let pkgs = [];
  try { pkgs = await api("/packages", "GET"); } catch { pkgs = PACKAGES; }
  pkgs.forEach(pkg => {
    const box = document.createElement("div");
    box.className = "package";
    const title = document.createElement("div");
    title.className = "title";
    title.textContent = `${pkg.title}`;
    const price = document.createElement("div");
    price.className = "price";
    price.textContent = `${pkg.price} บาท`;
    const cta = document.createElement("div");
    cta.className = "cta";
    const btn = document.createElement("button");
    btn.className = "primary";
    btn.textContent = "เลือกแพ็กเกจ";
    btn.addEventListener("click", () => selectPackage(pkg));
    cta.appendChild(btn);
    box.appendChild(title);
    box.appendChild(price);
    box.appendChild(cta);
    el.packageGrid.appendChild(box);
  });
}
async function selectPackage(pkg) {
  try {
    const resp = await api("/topup/create-order", "POST", { packageId: pkg.id });
    currentOrderId = resp.orderId;
    el.selectedPackageText.textContent = `แพ็กเกจที่เลือก: ${pkg.title} — ราคา ${pkg.price} บาท (จะได้รับ ${pkg.credits} สิทธิ์)`;
    el.qrImage.src = resp.qrImage || "";
    el.orderId.textContent = resp.orderId;
    el.paymentPane.classList.remove("hidden");
  } catch (e) {
    alert(e.message || "สร้างคำสั่งซื้อไม่ได้ กรุณาลองใหม่");
  }
}
async function verifyPayment() {
  if (!currentOrderId) return;
  el.verifyBtn.disabled = true;
  el.verifyBtn.textContent = "กำลังตรวจสอบ...";
  try {
    const status = await api(`/orders/${currentOrderId}`, "GET");
    if (status && status.status === "paid") {
      alert("ชำระเงินสำเร็จ! ระบบเพิ่มสิทธิ์ให้ในบัญชีของคุณแล้ว");
      updateAccountPanel();
      currentOrderId = null;
      closeTopupModal();
    } else if (status && status.status === "failed") {
      alert("การชำระเงินล้มเหลว กรุณาลองใหม่");
    } else {
      alert("ยังไม่พบการชำระ กรุณารอสักครู่แล้วกดตรวจสอบอีกครั้ง");
    }
  } catch (e) {
    alert(e.message || "ตรวจสอบคำสั่งซื้อไม่ได้");
  } finally {
    el.verifyBtn.disabled = false;
    el.verifyBtn.textContent = "ตรวจสอบการชำระเงินอัตโนมัติ";
  }
}

/* ========= CREDIT FLOW ========= */

function ensureAuth() {
  if (!getToken()) {
    openAuthModal();
    return false;
  }
  return true;
}
async function consumeOneCredit() {
  try {
    await api("/credits/consume", "POST");
    updateAccountPanel();
    return true;
  } catch {
    return false;
  }
}
async function requireCreditOrTopup() {
  if (!ensureAuth()) return false;
  const ok = await consumeOneCredit();
  if (!ok) {
    alert("สิทธิ์คงเหลือไม่เพียงพอ กรุณาเติมสิทธิ์ก่อนใช้งาน");
    openTopupModal();
    return false;
  }
  return true;
}

/* ========= TAROT RENDERING ========= */

function renderDeckPreview(count = 18) {
  el.deck.innerHTML = "";
  const demoCards = shuffle(Math.random, [...TAROT_DECK]).slice(0, count);
  demoCards.forEach((card, idx) => {
    const cardEl = createCardBackEl();
    cardEl.style.position = "absolute";
    cardEl.style.left = "calc(50% - 80px)";
    cardEl.style.top = "calc(50% - 130px)";
    cardEl.style.transform = `translate(${(idx - count / 2) * 2}px, ${(idx - count / 2) * -1.5}px) rotate(${(idx - count / 2) * 0.8}deg)`;
    el.deck.appendChild(cardEl);
  });
}
function createCardBackEl() {
  const cardEl = document.createElement("div");
  cardEl.className = "tarot-card";
  const inner = document.createElement("div");
  inner.className = "inner";
  const back = document.createElement("div");
  back.className = "face back";
  back.innerHTML = "<span class='card-tag'>tarot</span>";
  const front = document.createElement("div");
  front.className = "face front";
  inner.appendChild(back);
  inner.appendChild(front);
  cardEl.appendChild(inner);
  return cardEl;
}

/* Image URL mapping (Wikimedia Commons public domain) */
function imageUrl(card) {
  if (card.arcana === "Major") {
    const names = {
      0: "Fool", 1: "Magician", 2: "High_Priestess", 3: "Empress", 4: "Emperor",
      5: "Hierophant", 6: "Lovers", 7: "Chariot", 8: "Strength", 9: "Hermit",
      10: "Wheel_of_Fortune", 11: "Justice", 12: "Hanged_Man", 13: "Death",
      14: "Temperance", 15: "Devil", 16: "Tower", 17: "Star", 18: "Moon",
      19: "Sun", 20: "Judgement", 21: "World"
    };
    const num = String(card.number).padStart(2, "0");
    const fname = `RWS_Tarot_${num}_${names[card.number]}.jpg`;
    return `https://commons.wikimedia.org/wiki/Special:FilePath/${fname}`;
  }
  const suitMap = { Cups: "Cups", Swords: "Swords", Wands: "Wands", Pentacles: "Pents" };
  const suitName = suitMap[card.suit] || card.suit || "Cups";
  const num = String(card.number).padStart(2, "0");
  const fname = `${suitName}${num}.jpg`;
  return `https://commons.wikimedia.org/wiki/Special:FilePath/${fname}`;
}
function createFace(card, orientation) {
  const wrap = document.createElement("div");
  wrap.className = "tarot-card";
  wrap.style.setProperty("--rev", orientation === "reversed" ? "180deg" : "0deg");

  const inner = document.createElement("div");
  inner.className = "inner";

  const back = document.createElement("div");
  back.className = "face back";
  back.innerHTML = "<span class='card-tag'>หยิบไพ่</span>";

  const front = document.createElement("div");
  front.className = "face front";

  const img = document.createElement("img");
  img.className = "card-img";
  img.src = imageUrl(card);
  img.alt = card.en;
  img.referrerPolicy = "no-referrer";
  img.onerror = () => {
    img.remove();
    const fallback = document.createElement("div");
    fallback.className = "card-meaning";
    fallback.textContent = "ไม่พบรูปไพ่ (แสดงเฉพาะข้อความ)";
    front.appendChild(fallback);
  };

  const tag = document.createElement("span");
  tag.className = "card-tag" + (orientation === "reversed" ? " rev" : "");
  tag.textContent = orientation === "reversed" ? "กลับหัว" : "ตั้งตรง";

  const name = document.createElement("div");
  name.className = "card-name";
  name.textContent = `${card.th}`;

  const meaning = document.createElement("div");
  meaning.className = "card-meaning";
  meaning.textContent = orientation === "reversed" ? card.reversed : card.upright;

  front.appendChild(img);
  front.appendChild(tag);
  front.appendChild(name);
  front.appendChild(meaning);

  inner.appendChild(back);
  inner.appendChild(front);
  wrap.appendChild(inner);
  return wrap;
}
function clearResults() {
  el.resultsList.innerHTML = "";
}
function addResult(title, card, orientation) {
  const item = document.createElement("div");
  item.className = "result-item";
  const t = document.createElement("div");
  t.className = "title";
  t.textContent = title;
  const d = document.createElement("div");
  d.className = "desc";
  d.textContent = `${card.th} — ${orientation === "reversed" ? card.reversed : card.upright}`;
  item.appendChild(t);
  item.appendChild(d);
  el.resultsList.appendChild(item);
}

/* ========= INTERACTION ========= */

function focusBreath() {
  el.focusBtn.disabled = true;
  el.focusBtn.textContent = "หายใจเข้า — ออก";
  setTimeout(() => {
    el.focusBtn.textContent = "พร้อมแล้ว";
    el.focusBtn.disabled = false;
  }, 2000);
}
function performShuffle() {
  el.deck.classList.add("shuffling");
  const rng = createSeededRng(`${Date.now()}-${Math.random()}`);
  workingDeck = shuffle(rng, [...TAROT_DECK]);
  setTimeout(() => {
    el.deck.classList.remove("shuffling");
  }, 1800);
}
function performCut() {
  el.deck.classList.add("cutting");
  const half = Math.floor(workingDeck.length / 2);
  const top = workingDeck.slice(0, half);
  const bottom = workingDeck.slice(half);
  workingDeck = [...bottom, ...top];
  setTimeout(() => {
    el.deck.classList.remove("cutting");
  }, 1200);
}

async function startReading() {
  if (!(await requireCreditOrTopup())) return;

  clearResults();
  el.spreadBoard.classList.remove("hidden");
  const type = el.readingType.value;

  let positions = [];
  if (type === "single") {
    positions = [{ label: "สารจากไพ่ 1 ใบ", posClass: "" }];
    el.spreadBoard.className = "spread-board";
  } else if (type === "four") {
    positions = [
      { label: "ความรัก", posClass: "" },
      { label: "การงาน", posClass: "" },
      { label: "การเงิน", posClass: "" },
      { label: "สุขภาพ", posClass: "" },
    ];
    el.spreadBoard.className = "spread-board spread-grid-4";
  } else if (type === "ten") {
    positions = [
      { label: "ปัจจุบัน", posClass: "" },
      { label: "ท้าทาย", posClass: "" },
      { label: "อดีต", posClass: "" },
      { label: "อนาคต", posClass: "" },
      { label: "เป้าหมาย", posClass: "" },
      { label: "รากฐาน", posClass: "" },
      { label: "ตัวเอง", posClass: "" },
      { label: "คนรอบข้าง", posClass: "" },
      { label: "ความหวัง/ความกลัว", posClass: "" },
      { label: "ผลลัพธ์", posClass: "" },
    ];
    el.spreadBoard.className = "spread-board spread-grid-10";
  } else if (type === "celtic") {
    positions = [
      { label: "1) ปัจจุบัน", posClass: "pos-1" },
      { label: "2) สิ่งท้าทาย", posClass: "pos-2" },
      { label: "3) อดีตใกล้", posClass: "pos-3" },
      { label: "4) อนาคตใกล้", posClass: "pos-4" },
      { label: "5) เป้าหมาย", posClass: "pos-5" },
      { label: "6) รากฐาน", posClass: "pos-6" },
      { label: "7) ตัวตน", posClass: "pos-7" },
      { label: "8) สิ่งแวดล้อม", posClass: "pos-8" },
      { label: "9) ความหวัง/กลัว", posClass: "pos-9" },
      { label: "10) ผลลัพธ์", posClass: "pos-10" },
    ];
    el.spreadBoard.className = "spread-board spread-celtic";
  }

  const seedBase = `${el.userName.value || "guest"}-${Date.now()}`;
  const rng = createSeededRng(seedBase);
  const picks = shuffle(rng, [...workingDeck]).slice(0, positions.length);

  el.spreadBoard.innerHTML = "";
  picks.forEach((card, i) => {
    const orientation = randomOrientation(rng);
    const cardEl = createFace(card, orientation);
    cardEl.addEventListener("click", () => cardEl.classList.toggle("flipped"));
    cardEl.classList.add(positions[i].posClass);
    el.spreadBoard.appendChild(cardEl);
    addResult(positions[i].label, card, orientation);
  });
}

async function doDailyReading() {
  if (!(await requireCreditOrTopup())) return;

  el.dailyResults.innerHTML = "";
  const scope = el.dailyScope.value;
  const seed = `${dateSeed(scope)}-${el.userName.value || "guest"}`;
  const rng = createSeededRng(seed);

  const topicEls = Array.from(document.querySelectorAll('#daily .topics input[type="checkbox"]:checked'));
  const topics = topicEls.map(el => el.value);

  const picks = shuffle(rng, [...TAROT_DECK]);
  topics.forEach((topic, idx) => {
    const card = picks[idx % picks.length];
    const orientation = randomOrientation(rng);

    const item = document.createElement("div");
    item.className = "result-item";
    const t = document.createElement("div");
    t.className = "title";
    t.textContent = `${topic} (${scope})`;
    const d = document.createElement("div");
    d.className = "desc";
    d.textContent = `${card.th} — ${orientation === "reversed" ? card.reversed : card.upright}`;
    item.appendChild(t);
    item.appendChild(d);
    el.dailyResults.appendChild(item);
  });
}

/* ========= SIEMSEE (เซียมซี) ========= */

function siemseeShake() {
  if (!el.siemseeCylinder) return;
  el.siemseeCylinder.classList.add("shaking");
  setTimeout(() => el.siemseeCylinder.classList.remove("shaking"), 1800);
}
function siemseeFortune(no, luckLabel) {
  const labels = {
    "โชคดีมาก": {
      general: "ดวงเปิดทาง ชัยชนะและความสำเร็จมาเร็ว แผนที่ตั้งใจจะเห็นผลเป็นรูปธรรม",
      love: "ความรักสดใส คนโสดมีเกณฑ์เจอคนเข้ากันดี",
      work: "งานเดินหน้า ผู้ใหญ่สนับสนุน โอกาสใหม่ชัดเจน",
      money: "การเงินคล่องตัว พบช่องทางรายได้ใหม่",
      health: "แข็งแรง หากดูแลตัวเองต่อเนื่องผลลัพธ์ดี"
    },
    "โชคดี": {
      general: "โชคดีพอดี ผลสำเร็จค่อยๆปรากฏ ขยันและสม่ำเสมอ",
      love: "สัมพันธ์ดี ต้องคุยกันให้มากขึ้น",
      work: "ก้าวหน้าอย่างพอดี รายละเอียดต้องใส่ใจ",
      money: "เก็บออมเพิ่มขึ้น ระวังรายจ่ายฟุ่มเฟือย",
      health: "ดีโดยรวม พักผ่อนให้พอ"
    },
    "เสมอตัว": {
      general: "เสมอตัว เน้นความพอดี โฟกัสที่ควบคุมได้",
      love: "คุยกันเยอะขึ้น ปรับความเข้าใจ",
      work: "ตั้งใจและวางแผนให้ชัด ลดการผัดวัน",
      money: "รับ-จ่ายสมดุล ไม่เสี่ยงสูง",
      health: "ดูแลพื้นฐาน อาหาร นอน ออกกำลัง"
    },
    "ระวัง": {
      general: "ชะลอเรื่องใหญ่ ระวังอารมณ์และคำพูด",
      love: "อาจเกิดความไม่เข้าใจ ใจเย็นและรับฟัง",
      work: "มีอุปสรรค ต้องอดทนและแก้เป็นจุดๆ",
      money: "ระวังรายจ่ายบาน งดเสี่ยง",
      health: "ระวังออฟฟิศซินโดรม/พักผ่อนไม่พอ"
    },
    "ร้าย": {
      general: "ให้หยุดพักและทบทวน งดตัดสินใจใหญ่ ระวังคำพูด",
      love: "ใจเย็น หลีกเลี่ยงการปะทะ ถอยหนึ่งก้าว",
      work: "เลื่อนแผน ตรวจงานให้ละเอียด อย่าฝืน",
      money: "งดใช้จ่ายฟุ่มเฟือย หลีกเลี่ยงความเสี่ยง",
      health: "ถ้ามีอาการผิดปกติพบแพทย์"
    }
  };
  const tpl = labels[luckLabel] || labels["เสมอตัว"];
  const msg = `ดวงโดยรวม: ${tpl.general} ความรัก: ${tpl.love} การงาน: ${tpl.work} การเงิน: ${tpl.money} สุขภาพ: ${tpl.health}`;
  return { no, title: `ใบที่ ${no} — ${luckLabel}`, message: msg };
}
async function siemseeDraw() {
  if (!(await requireCreditOrTopup())) return;

  // Visual: shake + drop
  if (el.siemseeCylinder) {
    el.siemseeCylinder.classList.add("shaking");
    setTimeout(() => el.siemseeCylinder.classList.remove("shaking"), 900);
    el.siemseeCylinder.innerHTML = "";
    const stick = document.createElement("div");
    stick.className = "siemsee-stick";

    // Seeded pick by name + time
    const seed = `${(el.siemseeName?.value || "guest").trim()}-${Date.now()}`;
    const rng = createSeededRng(seed);
    const no = Math.floor(rng() * 60) + 1;

    const luckLabels = ["โชคดีมาก", "โชคดี", "เสมอตัว", "ระวัง", "ร้าย"];
    const luckLabel = luckLabels[no % luckLabels.length];

    const num = document.createElement("div");
    num.className = "num";
    num.textContent = `เลข ${no}`;
    stick.appendChild(num);
    el.siemseeCylinder.appendChild(stick);

    setTimeout(() => {
      const f = siemseeFortune(no, luckLabel);
      // show result
      el.siemseeResult.innerHTML = "";
      const item = document.createElement("div");
      item.className = "result-item";
      const t = document.createElement("div");
      t.className = "title";
      t.textContent = f.title;
      const d = document.createElement("div");
      d.className = "desc";
      d.textContent = f.message;
      item.appendChild(t);
      item.appendChild(d);
      el.siemseeResult.appendChild(item);
    }, 950);
  }
}

/* ========= INIT ========= */

function init() {
  updateAccountPanel();

  renderDeckPreview(18);

  // Reading controls
  el.focusBtn.addEventListener("click", focusBreath);
  el.shuffleBtn.addEventListener("click", performShuffle);
  el.cutBtn.addEventListener("click", performCut);
  el.startReadingBtn.addEventListener("click", startReading);
  el.dailyReadBtn.addEventListener("click", doDailyReading);

  // Siemsee controls
  el.siemseeShakeBtn && el.siemseeShakeBtn.addEventListener("click", siemseeShake);
  el.siemseeDrawBtn && el.siemseeDrawBtn.addEventListener("click", siemseeDraw);

  // Auth modal events
  el.loginBtn && el.loginBtn.addEventListener("click", openAuthModal);
  el.authClose.addEventListener("click", closeAuthModal);
  el.tabLogin.addEventListener("click", () => switchTab("login"));
  el.tabSignup.addEventListener("click", () => switchTab("signup"));
  el.doSignup.addEventListener("click", signup);
  el.doLogin.addEventListener("click", login);

  // Topup modal events
  el.topupClose.addEventListener("click", closeTopupModal);
  el.verifyBtn.addEventListener("click", verifyPayment);
  el.cancelTopup.addEventListener("click", openTopupModal);
}
init();