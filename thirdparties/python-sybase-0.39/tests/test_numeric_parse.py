import unittest

CS_MAX_PREC = 77
CS_MAX_SCALE = 77

class NumericParser(unittest.TestCase):
    def parseNum(self, num, precision=-1, scale=-1):
        length = len(num)
        if scale < 0 or precision < 0:
            integers = length
            decimals = 0
            exponent = 0

            if num[0] == '-':
                integers -= 1
            
            dp = num.find('.')
            if dp >= 0:
                decimals = length - dp - 1
                integers -= decimals + 1
            ep = num.find('e')
            if ep < 0: ep = num.find('E')
            if ep >= 0:
                if decimals == 0:
                    integers -= length - ep
                else:
                    decimals -= length - ep
                exponent = int(num[ep + 1:])
                integers += exponent
                if integers < 0:
                    integers = 0
                decimals -= exponent
                if decimals < 0:
                    decimals = 0

            if precision < 0:
                precision = integers + decimals
                if precision > CS_MAX_PREC:
                    precision = CS_MAX_PREC

            if integers > precision:
                raise ValueError, "number too big"

            if integers + decimals > precision:
                print "Warning truncating decimals"
                decimals = precision - integers

            if scale < 0:
                if decimals > CS_MAX_SCALE:
                    decimals = CS_MAX_SCALE
                scale = decimals

        if scale > precision:
            raise ValueError, "scale > precision"
        if scale > CS_MAX_SCALE:
            raise ValueError, "scale > CS_MAX_SCALE"
        if precision > CS_MAX_PREC:
            raise ValueError, "precision > CS_MAX_PREC"

        return precision, scale
            
    def test_num_parsing(self):
        self.assertEquals(self.parseNum("1"), (1,0))
        self.assertEquals(self.parseNum("-1"), (1,0))
        self.assertEquals(self.parseNum("1.0"), (2,1))
        self.assertEquals(self.parseNum("1.003"), (4,3))
        self.assertEquals(self.parseNum("3e5"), (6,0))
        self.assertEquals(self.parseNum("1.01e12"), (13,0))
        self.assertEquals(self.parseNum("1.456e-5"), (8,8))
        self.assertEquals(self.parseNum("-1.456e-5"), (8,8))

    def test_sybase_num_parsing(self):
        import Sybase
        from Sybase import numeric
        Sybase._ctx.debug = 1
        Sybase.set_debug(open('sybase_debug.log', 'w'))

        num = numeric("1")
        self.assertEquals((num.precision, num.scale), (1,0))
        num = numeric("-1")
        self.assertEquals((num.precision, num.scale), (1,0))
        num = numeric("1.0")
        self.assertEquals((num.precision, num.scale), (2,1))
        num = numeric("1.003")
        self.assertEquals((num.precision, num.scale), (4,3))
        num = numeric("3e5")
        self.assertEquals((num.precision, num.scale), (6,0))
        num = numeric("1.01e12")
        self.assertEquals((num.precision, num.scale), (13,0))
        num = numeric("1.456e-5")
        self.assertEquals((num.precision, num.scale), (8,8))
        num = numeric("-1.456e-5")
        self.assertEquals((num.precision, num.scale), (8,8))


if __name__ == '__main__':
    unittest.main()
