// Copy this file to config.js and fill in your Supabase credentials and image sources.
// These keys are safe to expose on the client (Anon key only).
window.APP_CONFIG = {
  SUPABASE_URL: "https://YOUR_PROJECT_REF.supabase.co",
  SUPABASE_ANON_KEY: "YOUR_PUBLIC_ANON_KEY",

  // Tarot image provider
  // mode: 'rws-wikimedia' | 'custom'
  TAROT_IMAGE_MODE: 'rws-wikimedia',
  // If you have your own deck, host all 78 images and put base url here, e.g. https://cdn.example.com/my-deck
  // Name your files as:
  //   majors: 00_Fool.jpg ... 21_World.jpg
  //   minors: Swords_Ace.jpg ... Cups_King.jpg etc. (see builder in script.js)
  CUSTOM_TAROT_BASE_URL: "https://cdn.example.com/my-deck",

  // Dice images 1..6 (override with your own)
  DICE_IMAGES: {
    1: "https://upload.wikimedia.org/wikipedia/commons/1/1b/Dice-1-b.svg",
    2: "https://upload.wikimedia.org/wikipedia/commons/5/5f/Dice-2-b.svg",
    3: "https://upload.wikimedia.org/wikipedia/commons/b/b1/Dice-3-b.svg",
    4: "https://upload.wikimedia.org/wikipedia/commons/f/fd/Dice-4-b.svg",
    5: "https://upload.wikimedia.org/wikipedia/commons/0/08/Dice-5-b.svg",
    6: "https://upload.wikimedia.org/wikipedia/commons/2/26/Dice-6-b.svg",
  },

  // Siemsi images (jar and stick). Replace with your own images if available.
  SIEMSI: {
    JAR: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/Kau_cim_2.jpg/480px-Kau_cim_2.jpg"
  },

  // Zodiac icons (override with your preferred set)
  ZODIAC_ICONS: {
    "มังกร": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Capricorn_symbol_%28fixed_width%29.svg/120px-Capricorn_symbol_%28fixed_width%29.svg.png",
    "กุมภ์": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/16/Aquarius_symbol_%28fixed_width%29.svg/120px-Aquarius_symbol_%28fixed_width%29.svg.png",
    "มีน": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Pisces_symbol_%28fixed_width%29.svg/120px-Pisces_symbol_%28fixed_width%29.svg.png",
    "เมษ": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Aries_symbol_%28fixed_width%29.svg/120px-Aries_symbol_%28fixed_width%29.svg.png",
    "พฤษภ": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Taurus_symbol_%28fixed_width%29.svg/120px-Taurus_symbol_%28fixed_width%29.svg.png",
    "เมถุน": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Gemini_symbol_%28fixed_width%29.svg/120px-Gemini_symbol_%28fixed_width%29.svg.png",
    "กรกฎ": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/99/Cancer_symbol_%28fixed_width%29.svg/120px-Cancer_symbol_%28fixed_width%29.svg.png",
    "สิงห์": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Leo_symbol_%28fixed_width%29.svg/120px-Leo_symbol_%28fixed_width%29.svg.png",
    "กันย์": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Virgo_symbol_%28fixed_width%29.svg/120px-Virgo_symbol_%28fixed_width%29.svg.png",
    "ตุลย์": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fb/Libra_symbol_%28fixed_width%29.svg/120px-Libra_symbol_%28fixed_width%29.svg.png",
    "พิจิก": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Scorpius_symbol_%28fixed_width%29.svg/120px-Scorpius_symbol_%28fixed_width%29.svg.png",
    "ธนู": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Sagittarius_symbol_%28fixed_width%29.svg/120px-Sagittarius_symbol_%28fixed_width%29.svg.png"
  }
};