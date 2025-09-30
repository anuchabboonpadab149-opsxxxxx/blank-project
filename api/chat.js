export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }
  const { prompt } = req.body || {};
  if (!prompt) {
    res.status(400).json({ error: 'Missing prompt' });
    return;
  }

  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    res.status(500).json({ error: 'Server misconfigured: OPENAI_API_KEY not set' });
    return;
  }

  try {
    const r = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model: 'gpt-4o-mini',
        messages: [
          { role: 'system', content: 'คุณเป็นหมอดูที่ให้คำทำนายอย่างอ่อนโยน จริงใจ และยึดโยงกับการปฏิบัติได้' },
          { role: 'user', content: prompt }
        ],
        temperature: 0.7,
      }),
    });
    if (!r.ok) {
      const t = await r.text();
      res.status(r.status).send(t);
      return;
    }
    const data = await r.json();
    const text = data.choices?.[0]?.message?.content || '';
    res.status(200).json({ text });
  } catch (e) {
    res.status(500).json({ error: String(e.message || e) });
  }
}