use pubs2
go
if exists ( select 1 from sysobjects where name = 'publishers2' and type = 'U' )
	drop table publishers2
go
select * into publishers2 from publishers
go
create unique index pubind on publishers2(pub_id)
go


