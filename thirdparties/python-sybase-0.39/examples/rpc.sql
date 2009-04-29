use tempdb
go
if exists ( select 1 from sysobjects where name = 'test_proc' )
	drop proc test_proc
go
create proc test_proc ( @type char(15), @tot_sales int, @num_books int output)
as
select @num_books = count( title_id ) 
   from pubs2.dbo.titles
	where
	   type = @type and total_sales > = @tot_sales
return
go 

