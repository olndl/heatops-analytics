select
  installation_id,
  scheduled_at,
  completed_at
from stg_installations
where completed_at is not null
  and completed_at < scheduled_at;
