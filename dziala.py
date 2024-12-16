import copy
import threading
import random
import time
from dataclasses import dataclass
from enum import Enum
from queue import Queue
from typing import List, Any

choose_waiting_time = 0.0000000001
 
class MessageTypes(Enum):
    END = 0,
    STUDENT = 1,
    STUDENT_GETTING_QUESTIONS = 2,
    STUDENT_ANSWERING = 3,
    STUDENT_GRADE = 4,
    EWAKUACJA = 5



@dataclass
class Msg:
    type: MessageTypes
    data: Any = None


GETTING_QUESTIONS = 'getting_questions'
ANSWERING = "answering"


class StudyField:
    def __init__(self, k):
        self.k = k


@dataclass
class Student:
    student_id: int
    passed_practical: bool
    field: int


@dataclass
class StudentData:
    student: Student
    questions: tuple = tuple()
    grades: tuple = tuple()


@dataclass
class StudentGrade:
    student: Student
    grade: float
    is_theory: bool


def generate_students(num,k):
    students = []
    for student_id in range(1, num + 1):
        passed_practical = bool(random.random() < 0.05)
        field = random.randint(1,k)
        student = Student(student_id, passed_practical, field)
        students.append(student)
    return students


class StudentManager(threading.Thread):
    def __init__(self, students, before_building_queue, evacuation_event, ending_event):
        super().__init__()
        self.students = list(students)
        random.shuffle(self.students)
        self.before_building_queue = before_building_queue
        self.evacuation_event =evacuation_event
        self.ending_event=ending_event
        self._stop_event = threading.Event()


    def run(self):

       # print(f"Student manager - running")
        for student in self.students:
            self.before_building_queue.put(Msg(MessageTypes.STUDENT, StudentData(student)))
            print(f"Student {student.student_id} comes to exam (is waiting before building) ")
            time.sleep(random.uniform(0, choose_waiting_time))
            if self.evacuation_event.is_set() :
                print(f"student manager received evacuation signal.")
                self._stop_event.set()
                break
            if self.ending_event.is_set():
                print(f"student manager received ending signal.")
                self._stop_event.set()
                break
 




class CommisionMember(threading.Thread):
    def __init__(self, input_queue, handler, evacuation_event, ending_event):
        super().__init__()

        self.input_queue = input_queue
        self.handler = handler
        self.evacuation_event =evacuation_event
        self.ending_event=ending_event
        self._stop_event = threading.Event()



    def run(self):
        #print(f"Comission member - running")
        while True:
            
            if self.evacuation_event.is_set() :
                print(f"comission member received evacuation signal.")
                self._stop_event.set()
                break
            if self.ending_event.is_set():
                print(f"comission member received ending signal.")
                self._stop_event.set()
                break
            try:
                msg = self.input_queue.get(timeout=1)

            except Exception:
                continue
            self.handler(msg)


class ThinkingSpace(threading.Thread):
    def __init__(self, shared_queue, output_queue,evacuation_event, ending_event, thread_id, name=None):
        super().__init__()
        self.shared_queue = shared_queue
        self.output_queue = output_queue
        self.thread_id = thread_id
        self.name = name
        self.evacuation_event=evacuation_event
        self.ending_event=ending_event
        self._stop_event = threading.Event()

    def run(self):
        #print(f"ThinkingSpace - running")
        while True:
            #print(f"ThinkingSpace - running")
            if self.evacuation_event.is_set() :
                print(f"Thinking space received evacuation signal.")
                self._stop_event.set()
                break
            if self.ending_event.is_set():
                print(f"Thinking space received ending signal.")
                self._stop_event.set()
                break
            try:
                msg = self.shared_queue.get(timeout=1)

                print(f"[ThinkingSpace {self.name}] Student '{msg.data.student.student_id}' myśli nad odpowiedziami.")
                time.sleep(choose_waiting_time)  
                self.output_queue.put(
                    Msg(
                        MessageTypes.STUDENT_ANSWERING,
                        msg.data
                    )
                )
            except Exception:
                continue


class Commission(threading.Thread):
    def __init__(self, semaphore, input_queue, output_queue, dean_queue, evacuation_event,ending_event, theoretical):
        super().__init__()

        self.semaphore = semaphore
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.dean_queue = dean_queue
        self.thinking_queue = Queue()
        self.evacuation_event = evacuation_event
        self.ending_event=ending_event
        self.theoretical = theoretical
        self._stop_event = threading.Event()

        self.member_queues = [Queue() for _ in range(3)]
        self.thinking_spaces = [
            ThinkingSpace(self.thinking_queue, self.member_queues[0],self.evacuation_event,self.ending_event, thread_id=i, name=str(theoretical) + str(i)) for i
            in range(3)
        ]

        def handle_questions_answers(msg: Msg) -> StudentData:
            if msg is None or msg.data is None:
                return None
            if msg.type == MessageTypes.STUDENT_GETTING_QUESTIONS:
                data = msg.data
                time.sleep(choose_waiting_time)
                questions = data.questions + (random.randint(0, 999),)
                data = copy.copy(data)
                data.questions = questions
                return data
            elif msg.type == MessageTypes.STUDENT_ANSWERING:
                data = msg.data
                time.sleep(choose_waiting_time)
                grade = random.choice([2.0, 3.0, 3.5, 4.0, 4.5, 5.0])
                grades = data.grades + (grade,)
                data = copy.copy(data)
                data.grades = grades
                return data
            else:
                return None

        def handle1(msg: Msg):
            new_data = handle_questions_answers(msg)
            msg.data = new_data
            self.member_queues[1].put(msg)

        def handle2(msg: Msg):
            new_data = handle_questions_answers(msg)
            msg.data = new_data
            self.member_queues[2].put(msg)

        def handle_last(msg: Msg):
            new_data = handle_questions_answers(msg)
            if msg.type == MessageTypes.STUDENT_GETTING_QUESTIONS:
                self.thinking_queue.put(
                    Msg(
                        MessageTypes.STUDENT,
                        new_data
                    )
                )
            elif msg.type == MessageTypes.STUDENT_ANSWERING:
                student = msg.data.student
                avg = sum(new_data.grades) / 3
                final_grade = (
                    2.0 if avg < 2.5 else
                    3.0 if avg < 3.25 else
                    3.5 if avg < 3.75 else
                    4.0 if avg < 4.25 else
                    4.5 if avg < 4.75 else
                    5.0
                )
                print(f"Student '{student.student_id}' final grade: {final_grade} from exam : {'Theoretical' if self.theoretical else 'Practical'}")

                self.dean_queue.put(
                    Msg(
                        MessageTypes.STUDENT_GRADE,
                        StudentGrade(student, final_grade, self.theoretical)
                    )
                )
                if final_grade != 2.0:
                    self.output_queue.put(
                        Msg(
                            MessageTypes.STUDENT,
                            StudentData(student)
                        )
                    )
                self.semaphore.release()

        # Tworzenie członków komisji
        self.members = [
            CommisionMember(self.member_queues[0], handle1,self.evacuation_event,self.ending_event),
            CommisionMember(self.member_queues[1], handle2,self.evacuation_event,self.ending_event),
            CommisionMember(self.member_queues[2], handle_last,self.evacuation_event,self.ending_event),
        ]



    def run(self):
        print(f"{'Theoretical' if self.theoretical else 'Practical'} commission -running")
        for member in self.members:
            member.start()
        for space in self.thinking_spaces:
            space.start()
        print(f"{'Theoretical' if self.theoretical else 'Practical'} commission -running")
        msg = None
        while True:
            #print(f" Komisja - running")
            if self.evacuation_event.is_set():
                print(f"{'Theoretical' if self.theoretical else 'Practical'} commission received evacuation signal.")
                break
            if self.ending_event.is_set():
                print(f"{'Theoretical' if self.theoretical else 'Practical'} commission received ending signal.")
                break

        
            if not msg:
                try:
                    msg = self.input_queue.get(timeout=1)
                except:
                    continue

            if not self.semaphore.acquire(timeout=1):
                continue

            self.member_queues[0].put(
                Msg(
                    MessageTypes.STUDENT_GETTING_QUESTIONS,
                    msg.data
                )
            )
            msg = None

        for member in self.members:
            member.join()
        for space in self.thinking_spaces:
            space.join()
        print(f"{'Theoretical' if self.theoretical else 'Practical'} commission finished.")




def print_dean_results(student_grades):
    print("=== Final Results ===")
    for student_id, grades in student_grades.items():
        # Access individual grades based on the type
        practical_grade = grades['praktyczna']
        theoretical_grade = grades['teoretyczna']
        # Print each student's grades
        if practical_grade is not None or theoretical_grade is not None:
            print(f"Student ID: {student_id}, Practical Grade: {practical_grade}, Theoretical Grade: {theoretical_grade}")
    print("=====================")

def count_students_with_field(students, k):
    count = 0
    for student in students:
        if student.field == k:
            count += 1
    return count


class Dean(threading.Thread):
    def __init__(self, students,dean_queue, evacuation_event, ending_event, student_number,student_grades,choosed_field,k):
        super().__init__()
        self.dean_queue = dean_queue
        self.evacuation_event = evacuation_event
        self.ending_event = ending_event
        self.student_number = student_number
        self.received_grades = 0
        self.choosed_field = choosed_field
        #self.student_grades ={}
        self.student_grades=student_grades
        self.k=k
        self.students = students
        self.field = None
        self.evacuation_thread = threading.Thread(target=self.send_evacuation_signal)
        self.ending_thread = threading.Thread(target=self.send_ending_signal)

    def run(self):
        #print(f"Dean - running")
        
        self.evacuation_thread.start()
        self.ending_thread.start()

        self.evacuation_thread.join()
        self.ending_thread.join()

    def send_evacuation_signal(self):
        evacuation_time = 200
        for _ in range(evacuation_time):
            if self.ending_event.is_set():
                break
            time.sleep(choose_waiting_time)
        if not self.ending_event.is_set():
            print("Dean: Sending evacuation signal.")
            self.evacuation_event.set()

    def send_ending_signal(self):

        time.sleep(random.uniform(0, choose_waiting_time))
        self.field = random.randint(1,self.k)
        print(f"Dean sending signal which field has test : {self.field}")
        self.choosed_field.put(self.field)
        

        count=count_students_with_field(self.students, self.field)
        print("Exam takes "+ str(count) + " students")

        
        print("Dean: Starting to process grades.")
        #print("...................................................")
        processed_ids = set() 
        while len(processed_ids) < count:
            if self.evacuation_event.is_set():
                break
            # print("len processed ids " +str( len(processed_ids)))
            # print(" student nb to process : "+str( count))
            try:
                msg = self.dean_queue.get(timeout=1)
                if msg.type == MessageTypes.STUDENT_GRADE:
                    # print(" msg.type == MessageTypes.STUDENT_GRADE")
                    student_grade = msg.data
                    student_id = student_grade.student.student_id
                    is_theory = student_grade.is_theory
                    passed_practical = student_grade.student.passed_practical
                    if passed_practical :
                        self.student_grades[student_id]['praktyczna']="passed earlier"
                        # print("passed practical")
                        print(f"Dean: Student {student_grade.student.student_id } passed practical exam last time.")

                    if is_theory :
                            self.student_grades[student_id]['teoretyczna']=student_grade.grade
                            processed_ids.add(student_id)
                            # print("ocena teoretyczna")
                            print(f"Dean: Processed theoretical grade for Student {student_grade.student.student_id}.")
                    else :
                            self.student_grades[student_id]['praktyczna']=student_grade.grade
                            if student_grade.grade == 2.0:
                                processed_ids.add(student_id)
                                # print("ocena praktyczna 2.0")
                                # print(" ocena praktyczna")
                            print(f"Dean: Processed practical grade for Student {student_grade.student.student_id}.")
            except :
                continue
        # print("koniec procesowania ocen")
       # print(f"GRADES FINISHED {self.student_grades}")
        if not self.evacuation_event.is_set():
            print("Dean: Received all grades. Sending ending signal.")
            self.ending_event.set()
            
 
class StudyFieldFilter(threading.Thread):
    def __init__(self, before_building_queue ,practical_queue,choosed_field_queue,evacuation_event,ending_event):
        super().__init__()
        self.before_building_queue = before_building_queue
  
        self.practical_queue=practical_queue
        self.choosed_field=choosed_field_queue
        self.field =None
        self.evacuation_event=evacuation_event
        self.ending_event=ending_event
        self._stop_event = threading.Event()
    def run(self):
        #print("Study field filter - running")
        while True:
            #print("study field filter - running")
            if self.evacuation_event.is_set():
                print(f"Student manager received evacuation signal.")
                break
            if self.ending_event.is_set():
                print(f"Student manager received ending signal.")
                break


            if self.field == None:
                try:
                    
                    self.field = self.choosed_field.get(timeout=1)
                    print(f"Study field filter : test has field : {self.field}")
                    #print(self.field)
                except:
                    continue
            if self.field == None:
                continue
            else :
                try :  
                    # print("before building queue size : ")
                    # print(self.before_building_queue.qsize())
                    msg = self.before_building_queue.get(timeout=1)
                  
                    if msg.type == MessageTypes.STUDENT and msg.data.student.field == self.field:
                        self.practical_queue.put(Msg(MessageTypes.STUDENT, msg.data))
                        print(f"Student  {msg.data.student.student_id } added to queue for exam")
                    else :
                        if msg.type == MessageTypes.STUDENT and msg.data.student.field != self.field:
                            print(f"Student  {msg.data.student.student_id } is sended home")


                except:
                    continue    
      

        
def main():
    #student_number = random.randint(80, 160)
    student_number = 15
    k = 5
    StudyField(k)
 
    students = generate_students(student_number,k)


    #print(students)

    evacuation_event = threading.Event()
    ending_event = threading.Event()
    choosing_field_event = threading.Event()

    practical_queue = Queue()
    theoretical_queue = Queue()
    dean_queue = Queue()
    result_queue = Queue()
   
    student_grades = {i: {'teoretyczna': None, 'praktyczna': None} for i in range(1, student_number + 1)}
    semaphore_practical = threading.Semaphore(3)
    semaphore_theoretical = threading.Semaphore(3)

    before_building_queue =Queue()
    choosed_field=Queue()


    student_manager = StudentManager(students, before_building_queue,evacuation_event,ending_event)
    study_field_filter = StudyFieldFilter(before_building_queue,practical_queue,choosed_field,evacuation_event,ending_event)
    practical_commision = Commission(semaphore_practical, practical_queue, theoretical_queue, dean_queue,
                                     evacuation_event,ending_event, theoretical=False)
    theoretical_commision = Commission(semaphore_theoretical, theoretical_queue, result_queue, dean_queue,
                                       evacuation_event,ending_event, theoretical=True)
    dean = Dean(students,dean_queue, evacuation_event,ending_event,student_number,student_grades,choosed_field,k)


    student_manager.start()
    practical_commision.start()
    theoretical_commision.start()
    dean.start()
    study_field_filter.start()

    

    student_manager.join()
    practical_commision.join()
    theoretical_commision.join()
    dean.join()
    study_field_filter.join()


    print("chosen field", dean.field)
    print("ALL STUDENTS")
    print("=========================================================")
    print("\n".join([str(s) for s in students]))
    print("=========================================================")

    print("STUDENTS WHO TOOK EXAM")
    print("=========================================================")
    print("\n".join([str(s) for s in students if s.field == dean.field]))
    print("=========================================================")

    print_dean_results(student_grades)

    print("koniec")


if __name__ == "__main__":
    main()