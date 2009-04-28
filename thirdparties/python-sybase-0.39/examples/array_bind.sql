
use tempdb
go
if exists ( select 1 from sysobjects where name = 'test_bcp' and type = 'U')
	drop table test_bcp
go
create table test_bcp
( id 		int		not null,
  name		varchar(20) 	null)
go

