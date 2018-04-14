select time_track, track
from eco.tracks
order by
    case when time_track > '2016-12-01 21:00' then time_track - '2016-12-01 21:00' 
    else '2016-12-01 21:00' - time_track end
limit 1;


with abc as 
(
 select *
 from eco.tracks
)
select pg_size_pretty(sum(pg_column_size(abc.*))) from abc