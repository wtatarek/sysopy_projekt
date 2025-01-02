import unittest
from unittest.mock import MagicMock, patch
import random
import time
from queue import Queue
from threading import Event
from main import (
    MessageTypes, Msg, Student, StudentData, StudentGrade, CommisionMember,
    ThinkingSpace, Dean, Commission, StudentRunner, broadcast_to_all_students, generate_students
)

class TestStudent(unittest.TestCase):

    def test_student_creation(self):
        student = Student(student_id=1, passed_practical=True, field=2)
        self.assertEqual(student.student_id, 1)
        self.assertTrue(student.passed_practical)
        self.assertEqual(student.field, 2)

    def test_student_data_creation(self):
        student = Student(student_id=1, passed_practical=True, field=2)
        student_data = StudentData(student=student)
        self.assertEqual(student_data.student.student_id, 1)
        self.assertEqual(student_data.questions, tuple())
        self.assertEqual(student_data.grades, tuple())

class TestMessageHandling(unittest.TestCase):

    def test_message_creation(self):
        msg = Msg(type=MessageTypes.STUDENT_GETTING_QUESTIONS, data=StudentData(Student(1, True, 2)))
        self.assertEqual(msg.type, MessageTypes.STUDENT_GETTING_QUESTIONS)
        self.assertIsInstance(msg.data, StudentData)

    def test_broadcast_to_all_students(self):
        student_id_to_queue = {1: Queue(), 2: Queue()}
        msg = Msg(type=MessageTypes.FIELD, data=1)
        with patch('main.student_id_to_queue', student_id_to_queue):
            broadcast_to_all_students(msg)
            self.assertEqual(student_id_to_queue[1].get().data, 1)
            self.assertEqual(student_id_to_queue[2].get().data, 1)

class TestCommission(unittest.TestCase):

    @patch('main.CommisionMember')
    @patch('main.ThinkingSpace')
    def test_commission_initialization(self, mock_thinking_space, mock_commission_member):
        mock_thinking_space.return_value = MagicMock()
        mock_commission_member.return_value = MagicMock()

        semaphore = MagicMock()
        input_queue = Queue()
        output_queue = Queue()
        dean_queue = Queue()
        evacuation_event = Event()
        ending_event = Event()

        commission = Commission(semaphore, input_queue, output_queue, dean_queue, evacuation_event, ending_event, theoretical=True)

        self.assertIsInstance(commission, Commission)
        self.assertEqual(len(commission.members), 3)
        self.assertEqual(len(commission.thinking_spaces), 3)


class TestDean(unittest.TestCase):

    @patch('main.broadcast_to_all_students')
    def test_dean_initialization(self, mock_broadcast):
        students = [Student(student_id=i, passed_practical=False, field=1) for i in range(1, 6)]
        dean_queue = Queue()
        evacuation_event = Event()
        ending_event = Event()
        student_number = 5
        student_grades = {}
        choosed_field = Queue()
        dean = Dean(students, dean_queue, evacuation_event, ending_event, student_number, student_grades, choosed_field, 1)
        self.assertIsInstance(dean, Dean)

    @patch('main.Dean.send_ending_signal')
    def test_send_ending_signal(self, mock_send_ending_signal):
        students = [Student(student_id=i, passed_practical=False, field=1) for i in range(1, 6)]
        dean_queue = Queue()
        evacuation_event = Event()
        ending_event = Event()
        student_number = 5
        student_grades = {}
        choosed_field = Queue()

        dean = Dean(students, dean_queue, evacuation_event, ending_event, student_number, student_grades, choosed_field, 1)
        dean.send_ending_signal()
        mock_send_ending_signal.assert_called_once()

class TestThinkingSpace(unittest.TestCase):

    def test_thinking_space_initialization(self):
        shared_queue = Queue()
        output_queue = Queue()
        evacuation_event = Event()
        ending_event = Event()
        thinking_space = ThinkingSpace(shared_queue, output_queue, evacuation_event, ending_event, thread_id=1)

        self.assertIsInstance(thinking_space, ThinkingSpace)


class TestStudentGrade(unittest.TestCase):

    def test_student_grade_creation(self):
        student = Student(student_id=1, passed_practical=True, field=2)
        student_grade = StudentGrade(student=student, grade=4.5, is_theory=True)
        self.assertEqual(student_grade.student.student_id, 1)
        self.assertEqual(student_grade.grade, 4.5)
        self.assertTrue(student_grade.is_theory)

class TestGenerateStudents(unittest.TestCase):

    @patch('main.random.randint', return_value=1)
    @patch('main.random.random', return_value=0.01)
    def test_generate_students(self, mock_random, mock_randint):
        students = generate_students(5, 2)
        self.assertEqual(len(students), 5)
        self.assertEqual(students[0].student_id, 1)

if __name__ == '__main__':
    unittest.main()
