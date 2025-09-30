-- Run this SQL in your Supabase project

create table if not exists plan_limits (
  plan_code text primary key,
  daily_quota int not null default 10
);

insert into plan_limits (plan_code, daily_quota)
values ('free', 10), ('basic', 50), ('pro', 200)
on conflict (plan_code) do nothing;

create table if not exists user_plans (
  user_id uuid primary key references auth.users(id) on delete cascade,
  plan_code text not null references plan_limits(plan_code),
  updated_at timestamptz default now()
);

-- default all users to free plan via trigger or manage via API
-- optional: set a default policy in your app

create table if not exists usage_counters (
  user_id uuid references auth.users(id) on delete cascade,
  ymd date not null,
  count int not null default 0,
  primary key (user_id, ymd)
);

create table if not exists histories (
  id bigserial primary key,
  user_id uuid not null references auth.users(id) on delete cascade,
  type text,
  prompt text,
  result text,
  created_at timestamptz default now()
);

-- Function to increment usage safely
create or replace function increment_usage(u_user_id uuid, u_ymd date)
returns void
language plpgsql
as $$
begin
  insert into usage_counters(user_id, ymd, count)
  values (u_user_id, u_ymd, 1)
  on conflict (user_id, ymd) do update set count = usage_counters.count + 1;
end;
$$;

-- RLS policies
alter table user_plans enable row level security;
alter table usage_counters enable row level security;
alter table histories enable row level security;

drop policy if exists "user can read own plan" on user_plans;
create policy "user can read own plan" on user_plans
for select using (auth.uid() = user_id);

drop policy if exists "service can write plans" on user_plans;
create policy "service can write plans" on user_plans
for all using (true) with check (true);

drop policy if exists "user can read own usage" on usage_counters;
create policy "user can read own usage" on usage_counters
for select using (auth.uid() = user_id);

drop policy if exists "service can write usage" on usage_counters;
create policy "service can write usage" on usage_counters
for all using (true) with check (true);

drop policy if exists "user read own histories" on histories;
create policy "user read own histories" on histories
for select using (auth.uid() = user_id);

drop policy if exists "service write histories" on histories;
create policy "service write histories" on histories
for all using (true) with check (true);