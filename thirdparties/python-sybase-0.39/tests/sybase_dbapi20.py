#!/usr/bin/env python
import dbapi20
import Sybase
import popen2
try:
    import nose
except ImportError:
    pass


class TestSybase(dbapi20.DatabaseAPI20Test):

    driver = Sybase    
    driver._ctx.debug = 1
    driver.set_debug(open('sybase_debug.log', 'w'))

    connect_args = ()
    lower_func = 'lower' # For stored procedure test

    force_commit = 0

    def commit(self,con):
        if not self.connect_kw_args.get("auto_commit", 0) or self.force_commit:
            con.commit()        

    def executeDDL1(self,con,cursor):
        # Sybase needs NULL to be specified in order to allow NULL values

        self.ddl1 = 'create table %sbooze (name varchar(20) NULL)' % self.table_prefix
        cursor.execute(self.ddl1)
        self.commit(con)

    def executeDDL2(self,con,cursor):
        cursor.execute(self.ddl2)
        self.commit(con)

    def setUp(self):
        # Call superclass setUp In case this does something in the
        # future
        dbapi20.DatabaseAPI20Test.setUp(self) 

        try:
            con = self._connect()
            con.close()
        except:
            # cmd = "psql -c 'create database dbapi20_test'"
            # cout,cin = popen2.popen2(cmd)
            # cin.close()
            # cout.read()
            raise

    def tearDown(self):
        dbapi20.DatabaseAPI20Test.tearDown(self)

    def _paraminsert(self,con,cur):
        # Overridden: Sybase does not handle named parameters like
        # dbapi20 expects

        # dbapi20:  c.execute("insert into foo values (:beer)", {"beer": "whatever"})
        # Sybase:   c.execute("insert into foo values (@beer)", {"@beer": "whatever"})

        self.executeDDL1(con,cur)
        cur.execute("insert into %sbooze values ('Victoria Bitter')" % (
            self.table_prefix
            ))
        self.failUnless(cur.rowcount in (-1,1))

        cur.execute(
            'insert into %sbooze values (@beer)' % self.table_prefix, 
            {'@beer':"Cooper's"}
            )
        self.failUnless(cur.rowcount in (-1,1))

        cur.execute('select name from %sbooze' % self.table_prefix)
        res = cur.fetchall()
        self.assertEqual(len(res),2,'cursor.fetchall returned too few rows')
        beers = [res[0][0],res[1][0]]
        beers.sort()
        self.assertEqual(beers[0],"Cooper's",
            'cursor.fetchall retrieved incorrect data, or data inserted '
            'incorrectly'
            )
        self.assertEqual(beers[1],"Victoria Bitter",
            'cursor.fetchall retrieved incorrect data, or data inserted '
            'incorrectly'
            )

    def test_executemany(self):
        # Overridden: same reason as _paraminsert

        con = self._connect()
        try:
            cur = con.cursor()
            self.executeDDL1(con,cur)
            largs = [ ("Cooper's",) , ("Boag's",) ]
            margs = [ {'@beer': "Cooper's"}, {'@beer': "Boag's"} ]
            cur.executemany(
                'insert into %sbooze values (@beer)' % self.table_prefix,
                margs
                )
            self.failUnless(cur.rowcount in (-1,2),
                'insert using cursor.executemany set cursor.rowcount to '
                'incorrect value %r' % cur.rowcount
                )
            cur.execute('select name from %sbooze' % self.table_prefix)
            res = cur.fetchall()
            self.assertEqual(len(res),2,
                'cursor.fetchall retrieved incorrect number of rows'
                )
            beers = [res[0][0],res[1][0]]
            beers.sort()
            self.assertEqual(beers[0],"Boag's",'incorrect data retrieved')
            self.assertEqual(beers[1],"Cooper's",'incorrect data retrieved')
        finally:
            con.close()

    def test_drop_non_existing(self):
        con = self._connect()
        cur = con.cursor()
        try:
            self.assertRaises(self.driver.DatabaseError, cur.execute, 'drop table %sdummy' % self.table_prefix)
        finally:
            con.close()

    def test_select_non_existing(self):
        con = self._connect()
        cur = con.cursor()
        try:
            self.assertRaises(self.driver.DatabaseError, cur.execute, 'select * from %sdummy' % self.table_prefix)
        finally:
            con.close()

    def test_bug_result_pending(self):
        # unitary test for a bug reported by Ralph Heinkel
        # http://www.object-craft.com.au/pipermail/python-sybase/2002-May/000034.html

        con = self._connect()
        try:
            cur = con.cursor()
            try:
                cur.execute('select * from %sdummy' % self.table_prefix)
            except self.driver.ProgrammingError:
                pass
            cur.execute('create table %sbooze (name varchar(20))' % self.table_prefix)
            con.commit()
        finally:
            con.close()

    def test_bug_result_pending2(self):
        con = self._connect()
        try:
            cur = con.cursor()
            try:
                cur.execute('drop table %sdummy' % self.table_prefix)
            except:
                pass
            cur.execute('create table %sbooze (name varchar(20))' % self.table_prefix)
            con.commit()
        finally:
            con.close()

    def test_bug_result_pending3_fetchall(self):
        # When not in auto_commit mode, it was not possible to commit after a fetchall because of results pending
        con = self._connect()
        try:
            cur = con.cursor()
            cur.execute('create table %sbooze (name varchar(20))' % self.table_prefix)
            con.commit()
            cur.execute('select name from %sbooze' % self.table_prefix)
            cur.fetchall()
            self.commit(con)
        finally:
            con.close()

    def test_duplicate_error(self):
        con = self._connect()
        try:
            cur = con.cursor()
            try:
                cur.execute('drop table %sbooze' % self.table_prefix)
            except self.driver.DatabaseError:
                pass
            cur.execute('create table %sbooze (name varchar(20) PRIMARY KEY)' % self.table_prefix)
            cur.execute("insert into %sbooze values ('Victoria Bitter')" % self.table_prefix)
            self.assertRaises(self.driver.IntegrityError, cur.execute, "insert into %sbooze values ('Victoria Bitter')" % self.table_prefix)
        finally:
            con.close()

    def test_callproc(self):
        con = self._connect()
        try:
            # create procedure lower
            cur = con.cursor()
            try:
                cur.execute("drop procedure lower")
                self.commit(con)
            except con.DatabaseError:
                pass
            cur.execute("create procedure lower(@name varchar(256)) as select lower(@name) commit transaction")
            self.commit(con)
        finally:
            con.close()
        dbapi20.DatabaseAPI20Test.test_callproc(self)

    def test_non_existing_proc(self):
        con = self._connect()
        try:
            # create procedure lower
            cur = con.cursor()
            try:
                cur.execute("drop procedure lower")
                self.commit(con)
            except con.DatabaseError:
                pass
            self.assertRaises(self.driver.StoredProcedureError,cur.callproc,self.lower_func,('FOO',))
        finally:
            con.close()

    def test_python_datetime(self):
        con = self._connect()
        con.outputmap = self.driver.DateTimeAsPython
        try:
            import datetime
            cur = con.cursor()
            cur.execute('create table %sbooze (day date)' % self.table_prefix)
            self.commit(con)
            cur.execute("insert into %sbooze values ('20061124')" % self.table_prefix)
            self.commit(con)
            cur.execute("insert into %sbooze values (@beer)" % self.table_prefix, {'@beer': datetime.date(2006,11,24)})
            self.commit(con)
            cur.execute("insert into %sbooze values (@beer)" % self.table_prefix, {'@beer': self.driver.Date(2006,11,24)})
            self.commit(con)
            cur.execute("select * from %sbooze" % self.table_prefix)
            res = cur.fetchall()
            date = res[0][0]
            self.assert_(isinstance(date, datetime.datetime))
            self.assertEquals(cur.description[0][1], self.driver.DATETIME)
            # self.assertEquals(cur.description[0][1], datetime.datetime)
            self.assertEquals(date.year, 2006)
            self.assertEquals(date.month, 11)
            self.assertEquals(date.day, 24)
            self.assertEquals(type(date), self.driver.DATETIME)
            self.assert_(isinstance(self.driver.Date(2006,12,24), datetime.date))
            self.assert_(isinstance(self.driver.Time(23,30,00), datetime.time))
            self.assert_(isinstance(self.driver.Date(2006,12,24), datetime.date))
        finally:
            con.close()

    def test_mx_datetime(self):
        try:
            import mx.DateTime
        except ImportError:
            raise nose.SkipTest
        con = self._connect()
        con.outputmap = self.driver.DateTimeAsMx
        try:
            cur = con.cursor()
            cur.execute('create table %sbooze (day date)' % self.table_prefix)
            self.commit(con)
            cur.execute("insert into %sbooze values ('20061124')" % self.table_prefix)
            self.commit(con)
            cur.execute("insert into %sbooze values (@beer)" % self.table_prefix, {'@beer': self.driver.Date(2006,11,24)})
            self.commit(con)
            cur.execute("select * from %sbooze" % self.table_prefix)
            res = cur.fetchall()
            date = res[0][0]
            import mx.DateTime
            self.assert_(isinstance(date, mx.DateTime.DateTimeType))
            self.assertEquals(cur.description[0][1], self.driver.DATETIME)
            # self.assertEquals(cur.description[0][1], mx.DateTime.DateTimeType)
            self.assertEquals(date.year, 2006)
            self.assertEquals(date.month, 11)
            self.assertEquals(date.day, 24)
            self.assertEquals(type(date), self.driver.DATETIME)
            # self.assert_(isinstance(self.driver.Date(2006,12,24), self.driver.DateTimeType))
            # self.assert_(isinstance(self.driver.Time(23,30,00), self.driver.DateTimeType))
            # self.assert_(isinstance(self.driver.Date(2006,12,24), self.driver.DateTimeType))
        finally:
            con.close()

    def test_sybase_datetime(self):
        con = self._connect()
        con.outputmap = self.driver.DateTimeAsSybase
        try:
            cur = con.cursor()
            cur.execute('create table %sbooze (day date)' % self.table_prefix)
            self.commit(con)
            cur.execute("insert into %sbooze values ('20061124')" % self.table_prefix)
            self.commit(con)
            cur.execute("insert into %sbooze values (@beer)" % self.table_prefix, {'@beer': self.driver.Date(2006,11,24)})
            self.commit(con)
            cur.execute("select * from %sbooze" % self.table_prefix)
            res = cur.fetchall()
            date = res[0][0]
            self.assertEquals(cur.description[0][1], self.driver.DATETIME)
            self.assert_(isinstance(date, self.driver.DateTimeType))
            self.assertEquals(date.year, 2006)
            self.assertEquals(date.month, 10)
            self.assertEquals(date.day, 24)
            self.assertEquals(type(date), self.driver.DATETIME)
            # self.assert_(type(date) >= self.driver.DATETIME)
            # self.assert_(isinstance(self.driver.Date(2006,11,24), self.driver.DateTimeType))
            # self.assert_(isinstance(self.driver.Time(23,30,00), self.driver.DateTimeType))
            # self.assert_(isinstance(self.driver.Date(2006,12,24), self.driver.DateTimeType))
        finally:
            con.close()

    def test_bulkcopy(self):
        kw_args = dict(self.connect_kw_args)
        kw_args.update({'bulkcopy': 1})
        con = self.driver.connect(*self.connect_args, **kw_args)
        try:
            if not con.auto_commit:
                self.assertRaises(self.driver.ProgrammingError, con.bulkcopy, "%sbooze" % self.table_prefix)
                return

            cur = con.cursor()
            self.executeDDL1(con,cur)

            b = con.bulkcopy("%sbooze" % self.table_prefix)
            largs = [ ("Cooper's",) , ("Boag's",) ]

            for r in largs:
                b.rowxfer(r)
            ret = b.done()
            self.assertEqual(ret, 2,
                'Bulkcopy.done retrieved incorrect number of rows'
                )

            self.assertEqual(b.totalcount, 2,
                'insert using bulkcopy set bulkcopy.totalcount to '
                'incorrect value %r' % b.totalcount
                )
            cur.execute('select name from %sbooze' % self.table_prefix)
            res = cur.fetchall()
            self.assertEqual(len(res),2,
                'cursor.fetchall retrieved incorrect number of rows'
                )
            beers = [res[0][0],res[1][0]]
            beers.sort()
            self.assertEqual(beers[0],"Boag's",'incorrect data retrieved')
            self.assertEqual(beers[1],"Cooper's",'incorrect data retrieved')

            bulk = con.bulkcopy("%sbooze" % self.table_prefix, out=1)
            beers = [b[0] for b in bulk]
            beers.sort()
            print beers[0], beers[1]
            self.assertEqual(beers[0],"Boag's",'incorrect data retrieved')
            self.assertEqual(beers[1],"Cooper's",'incorrect data retrieved')

        finally:
            con.close()

    def test_bulkcopy2(self):
        kw_args = dict(self.connect_kw_args)
        kw_args.update({'bulkcopy': 1})
        con = self.driver.connect(*self.connect_args, **kw_args)
        con.outputmap = self.driver.DateTimeAsPython
        try:
            if not con.auto_commit:
                self.assertRaises(self.driver.ProgrammingError, con.bulkcopy, "%sbooze" % self.table_prefix)
                return

            cur = con.cursor()
            cur.execute('create table %sbooze (name varchar(20) NULL, day date)' % self.table_prefix)
            self.commit(con)

            import datetime
            b = con.bulkcopy("%sbooze" % self.table_prefix)
            largs = [ ("Cooper's", datetime.date(2006,11,24)) , ("Boag's", datetime.date(2006,11,25)) ]

            for r in largs:
                b.rowxfer(r)
            ret = b.done()
            self.assertEqual(ret, 2,
                'Bulkcopy.done retrieved incorrect number of rows'
                )

            self.assertEqual(b.totalcount, 2,
                'insert using bulkcopy set bulkcopy.totalcount to '
                'incorrect value %r' % b.totalcount
                )
            cur.execute('select name from %sbooze' % self.table_prefix)
            res = cur.fetchall()
            self.assertEqual(len(res),2,
                'cursor.fetchall retrieved incorrect number of rows'
                )
            beers = [res[0][0],res[1][0]]
            beers.sort()
            self.assertEqual(beers[0], "Boag's", 'incorrect data retrieved')
            self.assertEqual(beers[1], "Cooper's", 'incorrect data retrieved')

            bulk = con.bulkcopy("%sbooze" % self.table_prefix, out=1)
            beers = [b[0] for b in bulk]
            beers.sort()
            print beers[0], beers[1]
            self.assertEqual(beers[0], "Boag's", 'incorrect data retrieved')
            self.assertEqual(beers[1], "Cooper's", 'incorrect data retrieved')

        finally:
            con.close()

    def test_datatypes(self):
        from Sybase import numeric
        from decimal import Decimal

        num = numeric(Decimal("100.5"))
        self.assertEquals("%r" % num, "100.5")
        num = numeric(Decimal("0.000001"))
        self.assertEquals("%r" % num, "0.000001")
        num = numeric(Decimal("-1e-23"))
        self.assertEquals("%r" % num, "-0.00000000000000000000001")
        num = numeric("-1111111111111111111111111111111111111111111111111111111111111111111111111111.1")
        self.assertEquals("%r" % num, "-1111111111111111111111111111111111111111111111111111111111111111111111111111.1")
        num = numeric(50000000000L)
        self.assertEquals("%r" % num, "50000000000")        

    def test_DataBuf(self):
        from Sybase import *
        import datetime
        
        b = DataBuf('hello')
        self.assertEquals((b.datatype, b.format), (CS_CHAR_TYPE, CS_FMT_NULLTERM))

        b = DataBuf(123)
        self.assertEquals((b.datatype, b.format), (CS_INT_TYPE, CS_FMT_UNUSED))
        b[0] = 100
        self.assertEquals(b[0], 100)
        b[0] = '100'
        self.assertEquals(b[0], 100)
        
        b = DataBuf(long(123))
        self.assertEquals((b.datatype, b.format), (CS_NUMERIC_TYPE, CS_FMT_UNUSED))
        # self.assertEquals((b.precision, b.scale), (3, 0))
        
        d = datetime.datetime(2007, 02, 16, 12, 25, 0)
        b = DataBuf(d)
        self.assertEquals((b.datatype, b.format), (CS_DATETIME_TYPE, CS_FMT_UNUSED))
        self.assertEquals(str(b[0]), 'Feb 16 2007 12:25PM')
        
        d = datetime.date(2007, 02, 16)
        b = DataBuf(d)
        self.assertEquals((b.datatype, b.format), (CS_DATE_TYPE, CS_FMT_UNUSED))
        self.assertEquals(str(b[0]), 'Feb 16 2007')
        
        b = DataBuf(1.0)
        self.assertEquals(b[0], 1.0)
        
        b = DataBuf(Sybase.numeric(100))
        self.assertEquals(b[0], 100)
        
        b = DataBuf(Sybase.numeric(100.0))
        self.assertEquals(b[0], 100.0)
        
        b = DataBuf(Sybase.numeric(100.0))
        b[0] = Sybase.numeric(100.0)
        self.assertEquals(b[0], 100.0)

        b = DataBuf(100.0)
        self.assertEquals(b[0], 100.0)
        self.assertEquals((b.datatype, b.format), (CS_FLOAT_TYPE, CS_FMT_UNUSED))
        b[0] = 110.0
        self.assertEquals(b[0], 110.0)

        fmt = CS_DATAFMT()
        fmt.datatype = CS_FLOAT_TYPE
        buf = DataBuf(fmt)
        buf[0] = 100.5
        self.assertEquals(buf[0], 100.5)
        # buf[0] = '101.5'
        # self.assertEquals(buf[0], 101.5) 

        fmt = CS_DATAFMT()
        fmt.datatype = CS_NUMERIC_TYPE
        buf = DataBuf(fmt)
        buf[0] = 100.5
        self.assertEquals(buf[0], 100.5)
        buf[0] = '101.5'
        self.assertEquals(buf[0], 101.5)
        from decimal import Decimal
        buf[0] = Decimal('100.5')
        self.assertEquals(buf[0], 100.5)

        fmt = CS_DATAFMT()
        fmt.datatype = CS_NUMERIC_TYPE
        fmt.count = 10
        buf = DataBuf(fmt)
        buf[0] = 100.0
        buf[1] = 101.0
        buf[2] = 102.0
        buf[3] = 103.0
        buf[4] = 104.0
        buf[5] = 105.0
        buf[6] = 106.0
        buf[7] = 107.0
        buf[8] = 108.0
        buf[9] = 109.0
        self.assertEquals(buf[0], 100.0)
        self.assertEquals(buf[1], 101.0)
        self.assertEquals(buf[2], 102.0)
        self.assertEquals(buf[3], 103.0)
        self.assertEquals(buf[4], 104.0)
        self.assertEquals(buf[5], 105.0)
        self.assertEquals(buf[6], 106.0)
        self.assertEquals(buf[7], 107.0)
        self.assertEquals(buf[8], 108.0)
        self.assertEquals(buf[9], 109.0)

        fmt = CS_DATAFMT()
        fmt.datatype = CS_NUMERIC_TYPE
        buf = DataBuf(fmt)
        buf[0] = Decimal('0.00000000001')
        self.assertEquals("%r" % buf[0], '0.00000000001')
        buf[0] = Decimal('1E-8')
        self.assertEquals("%r" % buf[0], '0.00000001')

        b = DataBuf(50000000000L)
        self.assertEquals(b[0], 50000000000)
        self.assertEquals((b.datatype, b.format), (CS_NUMERIC_TYPE, CS_FMT_UNUSED))
        # self.assertEquals((b.precision, b.scale), (11, 0))
        b[0] = 110.1
        self.assertEquals(b[0], 110.1)
        # self.assertEquals((b.precision, b.scale), (3, 1))

#     def testThreadLocking(self):
#         con = self._connect()
#         try:
#             query = "select t1=object_name(instrig), t2=object_name(updtrig), " + \
#                     "t3=object_name(deltrig) from sysobjects where " + \
#                     "id=object_id('Account')"
#             cursor = con.cursor()
#             cursor.execute(query)
#             print "1"
#             triggers = cursor.fetchall()
#             print "2"
#             while cursor.nextset():
#                 print "3"
#                 dummy = cursor.fetchall()
#         finally:
#             con.close()

# TODO: the following tests must be overridden

    def test_setoutputsize(self):
        pass

    def help_nextset_setUp(self,cur):
        ''' Should create a procedure called deleteme
            that returns two result sets, first the 
	    number of rows in booze then "name from booze"
        '''
        if not self.connect_kw_args.get("auto_commit", 0) or self.force_commit:
            sql="""
                create procedure deleteme as
                begin
                    begin transaction
                    select count(*) from %sbooze
                    select name from %sbooze
                    commit transaction
                end
            """ % (self.table_prefix, self.table_prefix)
        else:
            sql="""
                create procedure deleteme as
                begin
                    select count(*) from %sbooze
                    select name from %sbooze
                end
            """ % (self.table_prefix, self.table_prefix)
        cur.execute(sql)

    def help_nextset_tearDown(self,cur):
        'If cleaning up is needed after nextSetTest'
        try:
            cur.execute("drop procedure deleteme")
        except:
            pass

    def test_bugtracker_1719789(self):

        class MyConnection(Sybase.Connection):
            pass

        conn = MyConnection(*self.connect_args,**self.connect_kw_args)
        conn.close()
            
### ct_cursor

    def test_ct_cursor_parameter(self):
        # test for parameter pb which happened with ct_cursor
        con = self._connect()
        try:
            cur = con.cursor()
            cur.execute('create table %sbooze (value int)' % self.table_prefix)
            self.commit(con)
            for i in xrange(25):
                cur.execute("insert into %sbooze values (%d)" % (self.table_prefix, i))
            self.commit(con)
            cur.arraysize = 10
            cur.execute("select * from %sbooze where value > @0" % self.table_prefix, {"@0": 10}, select=True)
            res = cur.fetchone()
            self.assertEquals(res[0], 11)
            while res:
                last = res[0]
                res = cur.fetchone()
            self.assertEquals(last, 24)
        finally:
            con.close()

### arraysize

    def test_ct_cursor_arraysize(self):
        # test for some locking which happened with arraysize
        con = self._connect()
        try:
            cur = con.cursor()
            cur.execute('create table %sbooze (name varchar(2) NULL)' % self.table_prefix)
            self.commit(con)
            for i in xrange(25):
                cur.execute("insert into %sbooze values ('%d')" % (self.table_prefix, i))
            self.commit(con)
            cur.arraysize = 10
            cur.execute("select * from %sbooze" % self.table_prefix, select=True)
            res = cur.fetchone()
            while res:
                last = res[0]
                res = cur.fetchone()
            self.assertEquals(last, '24')
        finally:
            con.close()

### inputmap / outputmap

    def test_in_out_map(self):
        con = self._connect()
        try:
            import datetime

            ALTER_DATE_ORIGIN = datetime.date(1752, 9, 14)
            ALTER_DATETIME_ORIGIN = datetime.datetime(1752, 9, 14, 0, 0)
            SYBASE_DATE_ORIGIN = datetime.date(1753, 1, 1)
            SYBASE_DATETIME_ORIGIN = datetime.datetime(1753, 1, 1, 0, 0)
    
            outputmap = self.driver.DateTimeAsPython
            def change_outdatetime_origin(val):
                d = datetime.datetime(val.year, val.month + 1, val.day,
                                      val.hour, val.minute,
                                      val.second, val.msecond * 1000)
                if d.date() == SYBASE_DATE_ORIGIN:
                    d = ALTER_DATETIME_ORIGIN
                return d
            outputmap.update({
                self.driver.CS_DATETIME_TYPE: change_outdatetime_origin,
                self.driver.CS_DATETIME4_TYPE: change_outdatetime_origin })
    
            if self.driver._have_cs_date_type:
                def change_outdate_origin(val):
                    d = datetime.date(val.year, val.month + 1, val.day)
                    if d == SYBASE_DATE_ORIGIN:
                        d = ALTER_DATE_ORIGIN
                    return d
                outputmap.update({
                    self.driver.CS_DATE_TYPE: change_outdate_origin })
            con.outputmap = outputmap

            def change_indate_origin(val):
                if val < SYBASE_DATE_ORIGIN:
                    val = SYBASE_DATE_ORIGIN
                return val
            def change_indatetime_origin(val):
                if val < SYBASE_DATETIME_ORIGIN:
                    val = SYBASE_DATETIME_ORIGIN
                return val
            inputmap = { datetime.datetime: change_indatetime_origin,
                         datetime.date: change_indate_origin }
            con.inputmap = inputmap

            cur = con.cursor()
            cur.execute('create table %sbooze (day date)' % self.table_prefix)
            self.commit(con)
            cur.execute("insert into %sbooze values (@origin)" % self.table_prefix,
                        {'@origin': datetime.date(1752, 11, 15)})
            self.commit(con)
            cur.execute("select * from %sbooze" % self.table_prefix)
            res = cur.fetchall()
            date = res[0][0]
            self.assert_(isinstance(date, datetime.datetime))
            self.assertEquals(cur.description[0][1], self.driver.DATETIME)
            self.assertEquals(date.year, 1752)
            self.assertEquals(date.month, 9)
            self.assertEquals(date.day, 14)
            self.assertEquals(type(date), self.driver.DATETIME)
            self.assert_(isinstance(self.driver.Date(1752,9,14), datetime.date))
        finally:
            con.close()

    def test_insert_out_of_bound(self):
        con = self._connect()
        try:
            cur = con.cursor()
            cur.execute('create table %sbooze (num numeric(12,0) NULL)' % self.table_prefix)
            self.commit(con)
            cur.execute("insert into %sbooze values (@beer)" % self.table_prefix, {'@beer': 50000000000})
            self.failUnless(cur.rowcount in (-1,1))
        finally:
            con.close()

### Multi threads
#
#     def test_multi_threads(self):
#         con = self._connect()
#         try:
#             cur1 = con.cursor()
#             cur2 = con.cursor()
#             self.executeDDL1(con,cur1)
#             
#             for i in xrange(10):
#                 cur1.execute("insert into %sbooze values (@0)" % (self.table_prefix), {"@0": "%d" % i})
#             con.commit()
# 
#             from threading import Thread
#             
#             def select_loop(cursor, start, table_prefix):
#                 cursor.execute("select * from %sbooze" % (table_prefix))
#                 oldrow = None
#                 while 1:
#                     row = cursor.fetchone()
#                     if row is None:
#                         break
#                     oldrow = row
#                     print "thread%d: %s" % (start, row)
# 
#                 if oldrow[0] != "9":
#                     raise ValueError, "row '%s' %s is not 9" % (oldrow[0], type(oldrow[0]))
# 
#             thread1 = Thread(target=select_loop, args=(cur1, 0, self.table_prefix))
#             thread2 = Thread(target=select_loop, args=(cur2, 1, self.table_prefix))
#             
#             thread1.start()
#             thread2.start()
#             thread1.join(10)
#             thread2.join(5)
#         finally:
#             con.close()
