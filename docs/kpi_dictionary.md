# KPI Dictionary

## Lead-to-survey conversion

Share of leads that reached a booked survey.

```sql
surveys / leads
```

Used to understand whether lead sources are producing qualified demand.

## Survey-to-completed conversion

Share of surveyed leads that became completed installations.

```sql
completed_installations / surveys
```

Useful for comparing product fit and operational performance across regions.

## Median installation lead time

Median number of days between survey and scheduled or completed installation.

```sql
median(date_diff('day', survey_at, coalesce(completed_at, scheduled_at)))
```

Used to spot regions or products where customers wait too long.

## Open backlog

Count of installations with status `scheduled` or `delayed`.

Used by operations teams to understand capacity pressure.

## Estimated annual CO2 reduction

Sum of estimated annual CO2 reduction for completed installations.

This is a directional metric based on product assumptions, not a measured
emissions report.

## Customer satisfaction score

Average feedback score from completed installations.

```sql
avg(score)
```

Used together with lead time and backlog to separate growth from service quality.
