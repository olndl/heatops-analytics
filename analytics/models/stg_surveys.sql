create or replace view stg_surveys as
select
  survey_id,
  lead_id,
  cast(survey_at as date) as survey_at,
  cast(technical_fit as boolean) as technical_fit,
  cast(estimated_project_value_eur as integer) as estimated_project_value_eur
from raw_surveys;
