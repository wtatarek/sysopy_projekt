import unittest
from unittest.mock import Mock, patch
from queue import Queue
import threading
from dziala import *
class TestMain(unittest.TestCase):

    def setUp(self):
   
        self.num_students = 4
        self.k_fields = 3
        self.students = generate_students(self.num_students, self.k_fields)
        self.evacuation_event = threading.Event()
        self.ending_event = threading.Event()
        self.before_building_queue = Queue()
        self.practical_queue = Queue()
        self.dean_queue = Queue()
        self.choosed_field = Queue()
        self.student_grades = {i: {'teoretyczna': None, 'praktyczna': None} for i in range(1, self.num_students + 1)}
        self.k = self.k_fields

# Weryfikuje, jak funkcja generate_students radzi sobie z sytuacją, gdy liczba studentów wynosi zero
    def test_generate_students(self):
        
        students = generate_students(10, 3)
        self.assertEqual(len(students), 10)
        for student in students:
            self.assertIn(student.field, range(1, 4)) 
# Sprawdza zachowanie StudentManager przy jednej osobie.
    def test_student_manager(self):
   
        manager = StudentManager(self.students, self.before_building_queue, self.evacuation_event, self.ending_event)
        manager.start()
        manager.join()

        self.assertEqual(self.before_building_queue.qsize(), len(self.students))
        while not self.before_building_queue.empty():
            msg = self.before_building_queue.get()
            self.assertIsInstance(msg, Msg)
            self.assertEqual(msg.type, MessageTypes.STUDENT)
# Testuje zachowanie StudyFieldFilter z różnymi kierunkami wyboru, aby sprawdzić, czy filtr odpowiednio klasyfikuje studentów
    def test_study_field_filter(self):
 
        self.choosed_field.put(1)

        filter_thread = StudyFieldFilter(self.before_building_queue, self.practical_queue, self.choosed_field,
                                         self.evacuation_event, self.ending_event)
        for student in self.students:
            self.before_building_queue.put(Msg(MessageTypes.STUDENT, StudentData(student)))
        
        filter_thread.start()
        filter_thread.join(timeout=1)

        while not self.practical_queue.empty():
            msg = self.practical_queue.get()
            self.assertIsInstance(msg, Msg)
            self.assertEqual(msg.data.student.field, 1)
# Weryfikuje jak Commission radzi sobie w sytuacji, gdy lista studentów jest pusta.
    def test_commission(self):
       
        semaphore = threading.Semaphore(3)
        input_queue = Queue()
        output_queue = Queue()

        for student in self.students:
            input_queue.put(Msg(MessageTypes.STUDENT, StudentData(student)))

        commission = Commission(semaphore, input_queue, output_queue, self.dean_queue,
                                self.evacuation_event, self.ending_event, theoretical=False)
        commission.start()
        commission.join(timeout=2)

        self.assertTrue(self.dean_queue.qsize() > 0)
# Weryfikuje jak Dean przetwarza oceny, gdy liczba studentów zmienia się po rozpoczęciu jego pracy.
    def test_dean(self):
        """Test działania dziekana."""
        dean = Dean(self.students, self.dean_queue, self.evacuation_event, self.ending_event, self.num_students,
                    self.student_grades, self.choosed_field, self.k)  # Pass 'k' here
        dean.start()
        dean.join(timeout=2)

        for student_id, grades in self.student_grades.items():
            self.assertIn('teoretyczna', grades)
            self.assertIn('praktyczna', grades)
# Testuje ThinkingSpace przy wielu studentach, sprawdzając, czy wszyscy studenci przechodzą do stanu odpowiadania
    def test_thinking_space(self):
        """Test ThinkingSpace behavior."""
        shared_queue = Queue()
        output_queue = Queue()
        thinking_space = ThinkingSpace(shared_queue, output_queue, self.evacuation_event, self.ending_event, thread_id=0)

        student = self.students[0]
        shared_queue.put(Msg(MessageTypes.STUDENT, StudentData(student)))

        thinking_space.start()
        thinking_space.join(timeout=2)

        self.assertEqual(output_queue.qsize(), 1)
        msg = output_queue.get()
        self.assertIsInstance(msg, Msg)
        self.assertEqual(msg.type, MessageTypes.STUDENT_ANSWERING)
        self.assertEqual(msg.data.student.student_id, student.student_id)


# Testuje, czy dwie komisje działające równolegle przetwarzają wszystkich studentów bez opóźnień, używając tego samego semaforu i kolejki wejściowej.
    def test_commission_with_multiple_threads(self):
 
        semaphore = threading.Semaphore(3)
        input_queue = Queue()
        output_queue = Queue()

        for student in self.students:
            input_queue.put(Msg(MessageTypes.STUDENT, StudentData(student)))

        commission1 = Commission(semaphore, input_queue, output_queue, self.dean_queue,
                                 self.evacuation_event, self.ending_event, theoretical=False)
        commission2 = Commission(semaphore, input_queue, output_queue, self.dean_queue,
                                 self.evacuation_event, self.ending_event, theoretical=False)

        commission1.start()
        commission2.start()
        commission1.join(timeout=2)
        commission2.join(timeout=2)

        self.assertTrue(output_queue.qsize() >= self.num_students)

    
#Weryfikuje, czy wątek ThinkingSpace pomyślnie przenosi wszystkich studentów z kolejki wspólnej do kolejki wyjściowej i oznacza ich jako STUDENT_ANSWERING.
    def test_thinking_space_with_multiple_students(self):

        shared_queue = Queue()
        output_queue = Queue()
        thinking_space = ThinkingSpace(shared_queue, output_queue, self.evacuation_event, self.ending_event, thread_id=0)

        for student in self.students:
            shared_queue.put(Msg(MessageTypes.STUDENT, StudentData(student)))

        thinking_space.start()
        thinking_space.join(timeout=2)

        self.assertEqual(output_queue.qsize(), len(self.students))
        while not output_queue.empty():

            msg = output_queue.get()
            self.assertIsInstance(msg, Msg)
            self.assertEqual(msg.type, MessageTypes.STUDENT_ANSWERING)

if __name__ == '__main__':
    unittest.main()
