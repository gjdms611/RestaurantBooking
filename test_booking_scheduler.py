import io
import sys
import unittest
from datetime import datetime, timedelta

from booking_scheduler import BookingScheduler
from schedule import Customer, Schedule

NUMBER_OF_PEOPLE = 3
DATE_STRING = "2024-06-14 11:00:00"
EMAIL = "test@test.com"
PHONE_NUMBER = "010-9999-9999"
NAME = "Name"


class BookingSchedulerTest(unittest.TestCase):
    def setUp(self):
        self.scheduler = BookingScheduler(10)

    def test_예약은_정시에만_가능하다_정시가_아닌경우_예약불가(self):
        date_object = self.make_date_object(DATE_STRING) + timedelta(minutes=3)
        schedule = self.make_schedule(date_object=date_object)
        with self.assertRaises(ValueError):
            self.scheduler.add_schedule(schedule)

    def test_예약은_정시에만_가능하다_정시인_경우_예약가능(self):
        schedule = self.make_schedule()
        try:
            self.scheduler.add_schedule(schedule)
            self.assertTrue(self.scheduler.has_schedule(schedule))
        except ValueError as e:
            self.fail()

    def test_시간대별_인원제한이_있다_같은_시간대에_Capacity_초과할_경우_예외발생(self):
        schedule = self.make_schedule(number_of_people=11)
        with self.assertRaises(ValueError):
            self.scheduler.add_schedule(schedule)

    def test_시간대별_인원제한이_있다_같은_시간대가_다르면_Capacity_차있어도_스케쥴_추가_성공(self):
        schedule1 = self.make_schedule()
        date_object = self.make_date_object(DATE_STRING) + timedelta(hours=1)
        schedule2 = self.make_schedule(date_object=date_object)
        try:
            self.scheduler.add_schedule(schedule1)
            self.scheduler.add_schedule(schedule2)
            self.assertTrue(self.scheduler.has_schedule(schedule1))
            self.assertTrue(self.scheduler.has_schedule(schedule2))
        except ValueError as e:
            self.fail()

    def test_예약완료시_SMS는_무조건_발송(self):
        output = io.StringIO()
        original_stdout = sys.stdout
        sys.stdout = output
        try:
            schedule = self.make_schedule()
            self.scheduler.add_schedule(schedule)
        finally:
            sys.stdout = original_stdout
        self.assertIn("Sending SMS to 010-9999-9999 for schedule at 2024-06-14 11:00:00\n", output.getvalue())

    def test_이메일이_없는_경우에는_이메일_미발송(self):
        output = io.StringIO()
        original_stdout = sys.stdout
        sys.stdout = output
        try:
            date_object = self.make_date_object(DATE_STRING)
            customer = Customer(NAME, PHONE_NUMBER)
            schedule = Schedule(date_object, NUMBER_OF_PEOPLE, customer)
            self.scheduler.add_schedule(schedule)
        finally:
            sys.stdout = original_stdout
        self.assertNotIn("Sending email", output.getvalue())

    def test_이메일이_있는_경우에는_이메일_발송(self):
        output = io.StringIO()
        original_stdout = sys.stdout
        sys.stdout = output
        try:
            schedule = self.make_schedule()
            self.scheduler.add_schedule(schedule)
        finally:
            sys.stdout = original_stdout
        self.assertIn("Sending email", output.getvalue())

    def test_현재날짜가_일요일인_경우_예약불가_예외처리(self):
        schedule = self.make_schedule()
        with self.assertRaises(ValueError):
            self.scheduler.add_schedule(schedule)

    def test_현재날짜가_일요일이_아닌경우_예약가능(self):
        schedule = self.make_schedule()
        try:
            self.scheduler.add_schedule(schedule)
            self.assertTrue(self.scheduler.has_schedule(schedule))
        except ValueError as e:
            self.fail()

    def make_schedule(self, number_of_people=NUMBER_OF_PEOPLE, date_object=None):
        if date_object is None:
            date_object = self.make_date_object(DATE_STRING)
        customer = Customer(NAME, PHONE_NUMBER, EMAIL)
        return Schedule(date_object, number_of_people, customer)

    def make_date_object(self, date_string):
        date_format = "%Y-%m-%d %H:%M:%S"
        date_object = datetime.strptime(date_string, date_format)
        return date_object


if __name__ == '__main__':
    unittest.main()
