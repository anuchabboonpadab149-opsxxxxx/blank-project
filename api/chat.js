import { createClient } from "@supabase/supabase-js";

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const { prompt } = req.body || {};
  if (!prompt) return res.status(400).json({ error: 'Missing prompt' });

  const apiKey = process.env.OPENAI_API_KEY;
  const supaUrl = process.env.SUPABASE_URL;
  const supaServiceKey = process.env.SUPABASE_SERVICE_ROLE;
  if (!apiKey || !supaUrl || !supaServiceKey) {
    return res.status(500).json({ error: 'Server misconfigured: missing OPENAI_API_KEY / SUPABASE_URL / SUPABASE_SERVICE_ROLE' });
  }

  // Verify user via Supabase JWT from Authorization header
  const authHeader = req.headers.authorization || '';
  const token = authHeader.startsWith('Bearer ') ? authHeader.slice(7) : null;
  if (!token) return res.status(401).json({ error: 'Unauthorized' });

  const supabaseAdmin = createClient(supaUrl, supaServiceKey, { auth: { persistSession: false } });
  const { data: userData, error: userErr } = await supabaseAdmin.auth.getUser(token);
  if (userErr || !userData?.user) return res.status(401).json({ error: 'Invalid token' });
  const user = userData.user;

  // Enforce simple daily quota by plan
  // Default FREE: 10 calls/day. Example plans can be set in DB: user_plans(plan_code), plan_limits(plan_code, daily_quota)
  const today = new Date().toISOString().slice(0,10);
  const plan = await getUserPlan(supabaseAdmin, user.id);
  const dailyQuota = plan?.daily_quota ?? 10;

  const used = await getUsage(supabaseAdmin, user.id, today);
  if (used >= dailyQuota) {
    return res.status(402).json({ error: `Daily quota reached (${dailyQuota}). Upgrade plan.` });
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

    const textBody = await r.text();
    if (!r.ok) return res.status(r.status).send(textBody);

    const data = JSON.parse(textBody);
    const text = data.choices?.[0]?.message?.content || '';

    // Record usage and history
    await Promise.all([
      incrementUsage(supabaseAdmin, user.id, today),
      insertHistory(supabaseAdmin, user.id, prompt, text),
    ]);

    res.status(200).json({ text });
  } catch (e) {
    res.status(500).json({ error: String(e.message || e) });
  }
}

async function getUserPlan(supabase, user_id) {
  // Expected tables:
  // user_plans(user_id uuid pk, plan_code text, updated_at)
  // plan_limits(plan_code text pk, daily_quota int)
  const { data: up } = await supabase
    .from('user_plans')
    .select('plan_code, plans:plan_limits!inner(daily_quota)')
    .eq('user_id', user_id)
    .maybeSingle();
  if (!up) return null;
  return { plan_code: up.plan_code, daily_quota: up.plans?.daily_quota ?? 10 };
}

async function getUsage(supabase, user_id, ymd) {
  // usage_counters(user_id uuid, ymd date, count int, primary key (user_id, ymd))
  const { data } = await supabase
    .from('usage_counters')
    .select('count')
    .eq('user_id', user_id)
    .eq('ymd', ymd)
    .maybeSingle();
  return data?.count ?? 0;
}

async function incrementUsage(supabase, user_id, ymd) {
  const { error } = await supabase
    .from('usage_counters')
    .upsert({ user_id, ymd, count: 1 }, { onConflict: 'user_id,ymd' });
  if (!error) {
    await supabase.rpc('increment_usage', { u_user_id: user_id, u_ymd: ymd });
  }
}

async function insertHistory(supabase, user_id, prompt, text) {
  await supabase.from('histories').insert({
    user_id,
    prompt,
    result: text,
  });
}