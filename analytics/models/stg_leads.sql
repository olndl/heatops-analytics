create or replace view stg_leads as
select
  lead_id,
  home_id,
  cast(created_at as date) as created_at,
  source,
  status,
  nullif(cancel_reason, '') as cancel_reason
from raw_leads;
