import { createClient } from "@supabase/supabase-js";

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const { plan_code } = req.body || {};
  if (!plan_code) return res.status(400).json({ error: 'Missing plan_code' });

  const supaUrl = process.env.SUPABASE_URL;
  const supaServiceKey = process.env.SUPABASE_SERVICE_ROLE;
  if (!supaUrl || !supaServiceKey) return res.status(500).json({ error: 'Server misconfigured' });

  const authHeader = req.headers.authorization || '';
  const token = authHeader.startsWith('Bearer ') ? authHeader.slice(7) : null;
  if (!token) return res.status(401).json({ error: 'Unauthorized' });

  const supabaseAdmin = createClient(supaUrl, supaServiceKey, { auth: { persistSession: false } });
  const { data: userData, error: userErr } = await supabaseAdmin.auth.getUser(token);
  if (userErr || !userData?.user) return res.status(401).json({ error: 'Invalid token' });
  const user = userData.user;

  // Ensure plan exists
  const { data: plan } = await supabaseAdmin
    .from('plan_limits')
    .select('plan_code')
    .eq('plan_code', plan_code)
    .maybeSingle();
  if (!plan) return res.status(400).json({ error: 'Unknown plan_code' });

  const { error } = await supabaseAdmin
    .from('user_plans')
    .upsert({ user_id: user.id, plan_code }, { onConflict: 'user_id' });
  if (error) return res.status(500).json({ error: error.message });

  return res.status(200).json({ ok: true, plan_code });
}