import unittest
from sms.views import _parser_sms


class TestSms(unittest.TestCase):

    def test_should_accept_incomplete_year(self):
        message = u"AGF0687#GAGW .p 02/11 .d 12 .o 3 .r 4 .k 9 .f 1 .t 14 .a 230000 .s 0.233 .g 0 .m 1#mon commentaire"
        type_sms, reponse, data, texte = _parser_sms(message)
        self.assertEqual(1, type_sms)

    def test_should_accept_incomplete_month(self):
        message = u"AGF0687#GAGW .p 2/2011 .d 12 .o 3 .r 4 .k 9 .f 1 .t 14 .a 230000 .s 0.233 .g 0 .m 1#mon commentaire"
        type_sms, reponse, data, texte = _parser_sms(message)
        self.assertEqual(1, type_sms)

    def test_shoul_not_accept_date_equal_or_higher_than_now(self):
        message = u"AGF0687#GAGW .p 12/2011 .d 12 .o 3 .r 4 .c 9 .f 1 .t 14 .a 230000 .s 0.233 .g 0 .m 1#mon commentaire"
        type_sms, reponse, data, texte = _parser_sms(message)
        self.assertEqual(2, type_sms)
