
use tempdb
go
if exists ( select 1 from sysobjects where name = 'test' )
	drop table test
go
create table test(col1 int, col2 text, col3 text)
go

