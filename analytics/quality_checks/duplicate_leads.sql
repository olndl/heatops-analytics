select lead_id, count(*) as row_count
from raw_leads
group by lead_id
having count(*) > 1;
