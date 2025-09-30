import { createClient } from "@supabase/supabase-js";

export default async function handler(req, res) {
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

  if (req.method === 'GET') {
    const { data, error } = await supabaseAdmin
      .from('histories')
      .select('id, created_at, type, prompt, result')
      .eq('user_id', user.id)
      .order('created_at', { ascending: false })
      .limit(50);
    if (error) return res.status(500).json({ error: error.message });
    return res.status(200).json({ items: data || [] });
  }

  if (req.method === 'DELETE') {
    const { error } = await supabaseAdmin
      .from('histories')
      .delete()
      .eq('user_id', user.id);
    if (error) return res.status(500).json({ error: error.message });
    return res.status(200).json({ ok: true });
  }

  return res.status(405).json({ error: 'Method not allowed' });
}