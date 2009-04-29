use tempdb
go
if exists ( select 1 from sysobjects where name = 'test' and type = 'U' )
        drop table test
go
create table test(col1 int null, 
		  col2 char(25) null)
go

