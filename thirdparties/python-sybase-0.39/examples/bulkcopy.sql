use pubs2
go
if exists ( select 1 from sysobjects where name = 'test_pubs')
	drop table test_pubs
go
create table test_pubs( pub_id		int,
			pub_name	varchar(40) null,
			city		varchar(20) null,
			state		char(2)     null,
			notes		varchar(255) null)
go

