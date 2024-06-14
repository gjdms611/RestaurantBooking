import io
import sys
import unittest
from datetime import datetime

from booking_scheduler import BookingScheduler
from schedule import Customer, Schedule

EMAIL = "test@test.com"
PHONE_NUMBER = "010-9999-9999"
NAME = "Name"


class BookingSchedulerTest(unittest.TestCase):
    def test_예약은_정시에만_가능하다_정시가_아닌경우_예약불가(self):
        customer = Customer(NAME, PHONE_NUMBER, EMAIL)
        date_object = self.make_date_object("2024-06-14 11:45:00")
        schedule = Schedule(date_object, 3, customer)
        scheduler = BookingScheduler(10)
        with self.assertRaises(ValueError):
            scheduler.add_schedule(schedule)

    def test_예약은_정시에만_가능하다_정시인_경우_예약가능(self):
        customer = Customer(NAME, PHONE_NUMBER, EMAIL)
        date_object = self.make_date_object("2024-06-14 11:00:00")
        schedule = Schedule(date_object, 3, customer)
        scheduler = BookingScheduler(10)
        try:
            scheduler.add_schedule(schedule)
            self.assertTrue(scheduler.has_schedule(schedule))
        except ValueError as e:
            self.fail()

    def test_시간대별_인원제한이_있다_같은_시간대에_Capacity_초과할_경우_예외발생(self):
        customer = Customer(NAME, PHONE_NUMBER, EMAIL)
        date_object = self.make_date_object("2024-06-14 11:00:00")
        schedule = Schedule(date_object, 11, customer)
        scheduler = BookingScheduler(10)
        with self.assertRaises(ValueError):
            scheduler.add_schedule(schedule)

    def test_시간대별_인원제한이_있다_같은_시간대가_다르면_Capacity_차있어도_스케쥴_추가_성공(self):
        customer = Customer(NAME, PHONE_NUMBER, EMAIL)
        date_object = self.make_date_object("2024-06-14 11:00:00")
        scheduler = BookingScheduler(4)
        schedule1 = Schedule(date_object, 3, customer)
        date_object = self.make_date_object("2024-06-14 12:00:00")
        schedule2 = Schedule(date_object, 3, customer)
        try:
            scheduler.add_schedule(schedule1)
            scheduler.add_schedule(schedule2)
            self.assertTrue(scheduler.has_schedule(schedule1))
            self.assertTrue(scheduler.has_schedule(schedule2))
        except ValueError as e:
            self.fail()

    def test_예약완료시_SMS는_무조건_발송(self):
        output = io.StringIO()
        original_stdout = sys.stdout
        sys.stdout = output
        try:
            customer = Customer(NAME, PHONE_NUMBER, EMAIL)
            date_object = self.make_date_object("2024-06-14 11:00:00")
            schedule = Schedule(date_object, 3, customer)
            scheduler = BookingScheduler(10)
            scheduler.add_schedule(schedule)
        finally:
            sys.stdout = original_stdout
        self.assertIn("Sending SMS to 010-9999-9999 for schedule at 2024-06-14 11:00:00\n", output.getvalue())

    def test_이메일이_없는_경우에는_이메일_미발송(self):
        output = io.StringIO()
        original_stdout = sys.stdout
        sys.stdout = output
        try:
            customer = Customer(NAME, PHONE_NUMBER)
            date_object = self.make_date_object("2024-06-14 11:00:00")
            schedule = Schedule(date_object, 3, customer)
            scheduler = BookingScheduler(10)
            scheduler.add_schedule(schedule)
        finally:
            sys.stdout = original_stdout
        self.assertNotIn("Sending email", output.getvalue())

    def test_이메일이_있는_경우에는_이메일_발송(self):
        output = io.StringIO()
        original_stdout = sys.stdout
        sys.stdout = output
        try:
            customer = Customer(NAME, PHONE_NUMBER, EMAIL)
            date_object = self.make_date_object("2024-06-14 11:00:00")
            schedule = Schedule(date_object, 3, customer)
            scheduler = BookingScheduler(10)
            scheduler.add_schedule(schedule)
        finally:
            sys.stdout = original_stdout
        self.assertIn("Sending SMS to 010-9999-9999 for schedule at 2024-06-14 11:00:00\n", output.getvalue())

    def test_현재날짜가_일요일인_경우_예약불가_예외처리(self):
        pass

    def test_현재날짜가_일요일이_아닌경우_예약가능(self):
        pass

    def make_date_object(self, date_string):
        date_format = "%Y-%m-%d %H:%M:%S"
        date_object = datetime.strptime(date_string, date_format)
        return date_object


if __name__ == '__main__':
    unittest.main()
