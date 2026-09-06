-- L'Esprit Léger Premium V1
-- Préparation uniquement : ce fichier n'est pas encore déployé.
-- Objectif : foyer partagé, propriétaire unique, privé/partagé, lecture familiale,
-- écriture uniquement par le propriétaire.

create extension if not exists pgcrypto;
create schema if not exists private;

create table if not exists public.profiles (
  user_id uuid primary key references auth.users(id) on delete cascade,
  display_name text not null check (char_length(display_name) between 1 and 80),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.premium_access (
  user_id uuid primary key references auth.users(id) on delete cascade,
  family_premium boolean not null default false,
  source text not null default 'manual-test',
  valid_until timestamptz,
  updated_at timestamptz not null default now()
);

create table if not exists public.households (
  id uuid primary key default gen_random_uuid(),
  name text not null check (char_length(name) between 1 and 80),
  created_by uuid not null references auth.users(id) on delete restrict,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.household_members (
  household_id uuid not null references public.households(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  role text not null default 'member' check (role in ('owner','member')),
  joined_at timestamptz not null default now(),
  primary key (household_id, user_id)
);

create index if not exists household_members_user_idx
  on public.household_members(user_id, household_id);

create table if not exists public.calendar_items (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references auth.users(id) on delete cascade,
  household_id uuid references public.households(id) on delete cascade,
  item_kind text not null check (item_kind in ('appointment','task','typical_week')),
  visibility text not null default 'private' check (visibility in ('private','shared')),
  fixed boolean not null default false,
  payload jsonb not null default '{}'::jsonb,
  revision bigint not null default 1,
  deleted_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint shared_item_requires_household check (
    (visibility = 'private') or (visibility = 'shared' and household_id is not null)
  )
);

create index if not exists calendar_items_owner_idx
  on public.calendar_items(owner_id, updated_at desc);
create index if not exists calendar_items_household_idx
  on public.calendar_items(household_id, visibility, updated_at desc);

create table if not exists public.family_advice (
  id uuid primary key default gen_random_uuid(),
  household_id uuid not null references public.households(id) on delete cascade,
  advice_key text not null,
  advice_date date not null,
  period_key text not null default 'day',
  text text not null,
  metadata jsonb not null default '{}'::jsonb,
  engine_version text not null default 'premium-v1',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (household_id, advice_date, period_key, advice_key)
);

create index if not exists family_advice_household_date_idx
  on public.family_advice(household_id, advice_date desc);

-- Helpers RLS. SECURITY DEFINER évite les boucles de politiques sur household_members.
create or replace function private.user_household_ids()
returns setof uuid
language sql
security definer
set search_path = ''
stable
as $$
  select hm.household_id
  from public.household_members hm
  where hm.user_id = (select auth.uid())
$$;

create or replace function private.is_household_member(target_household uuid)
returns boolean
language sql
security definer
set search_path = ''
stable
as $$
  select exists (
    select 1
    from public.household_members hm
    where hm.household_id = target_household
      and hm.user_id = (select auth.uid())
  )
$$;

create or replace function private.is_household_creator(target_household uuid)
returns boolean
language sql
security definer
set search_path = ''
stable
as $$
  select exists (
    select 1
    from public.households h
    where h.id = target_household
      and h.created_by = (select auth.uid())
  )
$$;

revoke execute on function private.user_household_ids() from public;
revoke execute on function private.is_household_member(uuid) from public;
revoke execute on function private.is_household_creator(uuid) from public;
grant usage on schema private to authenticated;
grant execute on function private.user_household_ids() to authenticated;
grant execute on function private.is_household_member(uuid) to authenticated;
grant execute on function private.is_household_creator(uuid) to authenticated;

alter table public.profiles enable row level security;
alter table public.premium_access enable row level security;
alter table public.households enable row level security;
alter table public.household_members enable row level security;
alter table public.calendar_items enable row level security;
alter table public.family_advice enable row level security;

revoke all on table public.profiles from anon, authenticated;
revoke all on table public.premium_access from anon, authenticated;
revoke all on table public.households from anon, authenticated;
revoke all on table public.household_members from anon, authenticated;
revoke all on table public.calendar_items from anon, authenticated;
revoke all on table public.family_advice from anon, authenticated;

grant select, insert, update on table public.profiles to authenticated;
grant select on table public.premium_access to authenticated;
grant select, insert, update, delete on table public.households to authenticated;
grant select, insert, delete on table public.household_members to authenticated;
grant select, insert, update, delete on table public.calendar_items to authenticated;
grant select on table public.family_advice to authenticated;

-- Profil : chaque utilisateur ne voit et ne modifie que son propre profil.
create policy "profile_select_self"
on public.profiles for select to authenticated
using ((select auth.uid()) = user_id);

create policy "profile_insert_self"
on public.profiles for insert to authenticated
with check ((select auth.uid()) = user_id);

create policy "profile_update_self"
on public.profiles for update to authenticated
using ((select auth.uid()) = user_id)
with check ((select auth.uid()) = user_id);

-- Droit Premium : lecture uniquement de son propre droit. Écriture future côté serveur/billing.
create policy "premium_access_select_self"
on public.premium_access for select to authenticated
using ((select auth.uid()) = user_id);

-- Foyers.
create policy "household_select_member_or_creator"
on public.households for select to authenticated
using (
  created_by = (select auth.uid())
  or id in (select private.user_household_ids())
);

create policy "household_insert_creator"
on public.households for insert to authenticated
with check (created_by = (select auth.uid()));

create policy "household_update_creator"
on public.households for update to authenticated
using (created_by = (select auth.uid()))
with check (created_by = (select auth.uid()));

create policy "household_delete_creator"
on public.households for delete to authenticated
using (created_by = (select auth.uid()));

-- Membres : les membres d'un foyer peuvent voir la composition du foyer.
create policy "household_members_select_same_household"
on public.household_members for select to authenticated
using (
  user_id = (select auth.uid())
  or household_id in (select private.user_household_ids())
  or (select private.is_household_creator(household_id))
);

-- Préparation du prototype : seul le créateur du foyer peut ajouter un membre.
-- L'invitation par code/QR passera ensuite par une fonction serveur atomique.
create policy "household_members_insert_creator"
on public.household_members for insert to authenticated
with check ((select private.is_household_creator(household_id)));

create policy "household_members_delete_creator_or_self"
on public.household_members for delete to authenticated
using (
  (select private.is_household_creator(household_id))
  or user_id = (select auth.uid())
);

-- Calendrier partagé :
-- - propriétaire : toujours visible ;
-- - autre membre : visible uniquement si partagé et dans le même foyer ;
-- - écriture/modification/suppression : propriétaire uniquement.
create policy "calendar_item_select_owner_or_shared_household"
on public.calendar_items for select to authenticated
using (
  owner_id = (select auth.uid())
  or (
    visibility = 'shared'
    and household_id is not null
    and (select private.is_household_member(household_id))
  )
);

create policy "calendar_item_insert_owner"
on public.calendar_items for insert to authenticated
with check (
  owner_id = (select auth.uid())
  and (
    visibility = 'private'
    or (
      visibility = 'shared'
      and household_id is not null
      and (select private.is_household_member(household_id))
    )
  )
);

create policy "calendar_item_update_owner_only"
on public.calendar_items for update to authenticated
using (owner_id = (select auth.uid()))
with check (
  owner_id = (select auth.uid())
  and (
    visibility = 'private'
    or (
      visibility = 'shared'
      and household_id is not null
      and (select private.is_household_member(household_id))
    )
  )
);

create policy "calendar_item_delete_owner_only"
on public.calendar_items for delete to authenticated
using (owner_id = (select auth.uid()));

-- Conseil familial : lecture identique pour tous les membres du foyer.
-- Écriture volontairement non accordée au client : la génération synchronisée sera
-- faite plus tard via une fonction serveur/Edge Function afin d'éviter les divergences.
create policy "family_advice_select_household"
on public.family_advice for select to authenticated
using ((select private.is_household_member(household_id)));

-- À activer lors de la phase Realtime, après création du projet Supabase :
-- alter publication supabase_realtime add table public.calendar_items;
-- alter publication supabase_realtime add table public.family_advice;
