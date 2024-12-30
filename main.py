import copy
import threading
import random
import time
from dataclasses import dataclass
from enum import Enum
from queue import Queue
from typing import List, Any
import os

choose_waiting_time = 0.0001

choose_evacuation_time = 10

class MessageTypes(Enum):
    END = 0,
    STUDENT = 1,
    STUDENT_GETTING_QUESTIONS = 2,
    STUDENT_ANSWERING = 3,
    STUDENT_GRADE = 4,
    EWAKUACJA = 5,
    FIELD = 6,
    STUDENT_ALL_QUESTIONS = 7


@dataclass
class Msg:
    type: MessageTypes
    data: Any = None


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


student_id_to_queue = {}

def broadcast_to_all_students(msg):
    for q in student_id_to_queue.values():
        q.put(msg)

def generate_students(num,k):
    students = []
    for student_id in range(1, num + 1):
        queue = Queue()
        passed_practical = bool(random.random() < 0.05)
        field = random.randint(1,k)
        student = Student(student_id, passed_practical, field)
        students.append(student)
        student_id_to_queue[student_id] = queue
        
    return students


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
        
                grades_list = [2.0, 3.0, 3.5, 4.0, 4.5, 5.0]
                weights = [0.05, 0.19, 0.19, 0.19, 0.19, 0.19]

                grade = random.choices(grades_list, weights=weights, k=1)[0]
                grades = data.grades + (grade,)
                data = copy.copy(data)
                data.grades = grades
                return data
            else:
                return None

        def handle_student(msg: Msg):
            new_data = handle_questions_answers(msg)
            msg.data = new_data
            key = new_data.student.student_id
            student_id_to_queue[key].put(msg)

        
        def handle_last(msg: Msg):
            new_data = handle_questions_answers(msg)
            if msg.type == MessageTypes.STUDENT_GETTING_QUESTIONS:
                key = new_data.student.student_id
                student_id_to_queue[key].put(
                    Msg(
                        MessageTypes.STUDENT_ALL_QUESTIONS,
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
                    key = new_data.student.student_id
                    student_id_to_queue[key].put(
                        Msg(
                            MessageTypes.STUDENT_GRADE,
                            StudentGrade(student, final_grade, self.theoretical)
                        )
                    )
                    
                self.semaphore.release()

        # Tworzenie członków komisji
        self.members = [
            CommisionMember(self.member_queues[0], handle_student,self.evacuation_event,self.ending_event),
            CommisionMember(self.member_queues[1], handle_student,self.evacuation_event,self.ending_event),
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



class StudentRunner(threading.Thread):

    def __init__(self, student: Student, practical_commission: Commission, theoretical_commission: Commission, evacuation_event: threading.Event):
        super().__init__()
        self.student = student
        self.practical_commission = practical_commission
        self.evacuation_event = evacuation_event
        self.queue = student_id_to_queue[student.student_id]
        assert self.queue is not None
        self. theoretical_commission= theoretical_commission

    def run(self):
        # po losowym czasie idzie na egzamin

        #   time.sleep(random.uniform(0, 5 * choose_waiting_time))
            time.sleep(0.000000001)

            field = None

            def _await_msg_type(type: MessageTypes):
                while True:                   
                    msg: Msg = self.queue.get()
                    if msg.type == type:
                        return msg
                    
            if self.evacuation_event.is_set():
                print(f" Student {self.student.student_id} ewakuuje się")
                return
            
            msg = _await_msg_type(MessageTypes.FIELD)
            field = msg.data

            if self.student.field != field:
                print(f"Student {self.student.student_id}: Ide do domu, nie moj kierunek")
                return
            
            print(f"Student {self.student.student_id}: Ide do komisji praktzycznej")
            

            while True:
    
                if self.evacuation_event.is_set():
                    return
                  
                if not self.practical_commission.semaphore.acquire(timeout=1):
                    continue
                else:
                    break
                
            
            self.practical_commission.member_queues[0].put(
                Msg(
                    MessageTypes.STUDENT_GETTING_QUESTIONS,
                    data=StudentData(self.student, tuple(), tuple())
                )
            )
            
            msg = _await_msg_type(MessageTypes.STUDENT_GETTING_QUESTIONS)
            print(msg)

            self.practical_commission.member_queues[1].put(msg)
            msg = _await_msg_type(MessageTypes.STUDENT_GETTING_QUESTIONS)
            print(msg)


            self.practical_commission.member_queues[2].put(msg)
            msg = _await_msg_type(MessageTypes.STUDENT_ALL_QUESTIONS)
            print(msg)

            print(f"Studnet mysli nad odpowiedziami {self.student.student_id}")
            time.sleep(3)

            self.practical_commission.member_queues[0].put(
                Msg(
                    MessageTypes.STUDENT_ANSWERING,
                    msg.data
                )
            )
            msg = _await_msg_type(MessageTypes.STUDENT_ANSWERING)
            print(msg)

            self.practical_commission.member_queues[1].put(
                Msg(
                    MessageTypes.STUDENT_ANSWERING,
                    msg.data
                )
            )
            msg = _await_msg_type(MessageTypes.STUDENT_ANSWERING)
            print(msg)

            self.practical_commission.member_queues[2].put(
                Msg(
                    MessageTypes.STUDENT_ANSWERING,
                    msg.data
                )
            )
            msg = _await_msg_type(MessageTypes.STUDENT_GRADE)

            print(msg)


            self.practical_commission.semaphore.release()

            if msg.data.grade > 2.0 or msg.data.student.passed_practical:
                print("zdałem")
                while True:
                    #if self.evacuation_event.is_set(timeout=1):
                    if self.evacuation_event.wait(timeout=1):
                       
                        return
                    if not self.theoretical_commission.semaphore.acquire(timeout=1):
                        continue
                    else:
                        break
                





                self.theoretical_commission.member_queues[0].put(
                Msg(
                    MessageTypes.STUDENT_GETTING_QUESTIONS,
                    data=StudentData(self.student, tuple(), tuple())
                )
                )
            
                msg = _await_msg_type(MessageTypes.STUDENT_GETTING_QUESTIONS)
                print(msg)

                self.theoretical_commission.member_queues[1].put(msg)
                msg = _await_msg_type(MessageTypes.STUDENT_GETTING_QUESTIONS)
                print(msg)


                self.theoretical_commission.member_queues[2].put(msg)
                msg = _await_msg_type(MessageTypes.STUDENT_ALL_QUESTIONS)
                print(msg)

                print(f"Studnet mysli nad odpowiedziami {self.student.student_id}")
                time.sleep(3)

                self.theoretical_commission.member_queues[0].put(
                    Msg(
                        MessageTypes.STUDENT_ANSWERING,
                        msg.data
                    )
                )
                msg = _await_msg_type(MessageTypes.STUDENT_ANSWERING)
                print(msg)

                self.theoretical_commission.member_queues[1].put(
                    Msg(
                        MessageTypes.STUDENT_ANSWERING,
                        msg.data
                    )
                )
                msg = _await_msg_type(MessageTypes.STUDENT_ANSWERING)
                print(msg)

                self.theoretical_commission.member_queues[2].put(
                    Msg(
                        MessageTypes.STUDENT_ANSWERING,
                        msg.data
                    )
                )
                msg = _await_msg_type(MessageTypes.STUDENT_GRADE)

            




 




class CommisionMember(threading.Thread):
    def __init__(self, input_queue, handler, evacuation_event, ending_event):
        super().__init__()

        self.input_queue = input_queue
        self.handler = handler
        self.evacuation_event =evacuation_event
        self.ending_event=ending_event
        self._stop_event = threading.Event()



    def run(self):
       
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
       
        while True:
            
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




def print_dean_results(student_grades):
    print("=== Final Results ===")
    for student_id, grades in student_grades.items():
     
        practical_grade = grades['praktyczna']
        theoretical_grade = grades['teoretyczna']
     
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
   
        self.student_grades=student_grades
        self.k=k
        self.students = students
        self.field = None
        self.evacuation_thread = threading.Thread(target=self.send_evacuation_signal)
        self.ending_thread = threading.Thread(target=self.send_ending_signal)

    def run(self):
        
        
        
        
        self.evacuation_thread.start()
        self.ending_thread.start()
        

        self.evacuation_thread.join()
        self.ending_thread.join()

    def send_evacuation_signal(self):
        evacuation_time = int(choose_evacuation_time)
        print(f"czas ewakuacji {evacuation_time}")
        for _ in range(evacuation_time):
            if self.ending_event.is_set():
                break
            time.sleep(10)
           
        if not self.ending_event.is_set():
            print("Dean: Sending evacuation signal.")
            self.evacuation_event.set()

      
    def send_ending_signal(self):

        time.sleep(random.uniform(0, choose_waiting_time))
        self.field = random.randint(1,self.k)
        print(f"Dean sending signal which field has test : {self.field}")
        # self.choosed_field.put(self.field)
        broadcast_to_all_students(Msg(MessageTypes.FIELD, self.field))
        

        count=count_students_with_field(self.students, self.field)
        print("Exam takes "+ str(count) + " students")

        
        print("Dean: Starting to process grades.")

        processed_ids = set() 
        while len(processed_ids) < count:
            if self.evacuation_event.is_set():
                break
            
            try:
                msg = self.dean_queue.get(timeout=1)
                if msg.type == MessageTypes.STUDENT_GRADE:
               
                    student_grade = msg.data
                    student_id = student_grade.student.student_id
                    is_theory = student_grade.is_theory
                    passed_practical = student_grade.student.passed_practical
                    if passed_practical :
                        self.student_grades[student_id]['praktyczna']="passed earlier"
                        
                        print(f"Dean: Student {student_grade.student.student_id } passed practical exam last time.")

                    if is_theory :
                            self.student_grades[student_id]['teoretyczna']=student_grade.grade
                            processed_ids.add(student_id)
                      
                            print(f"Dean: Processed theoretical grade for Student {student_grade.student.student_id}.")
                    else :
                            self.student_grades[student_id]['praktyczna']=student_grade.grade
                            
                            if student_grade.grade == 2.0:
                                processed_ids.add(student_id)
                                print("--------------------------------------------------------------------------------------------------------")
                            print(f"Dean: Processed practical grade for Student {student_grade.student.student_id}.")
            except :
                continue

        if not self.evacuation_event.is_set():
            print("Dean: Received all grades. Sending ending signal.")
            self.ending_event.set()
            
 


        
def main():
    #student_number = random.randint(80, 160)
    student_number = 100
    k = 5
    StudyField(k)
 
    students = generate_students(student_number,k)



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

 
    practical_commision = Commission(semaphore_practical, practical_queue, theoretical_queue, dean_queue,
                                     evacuation_event,ending_event, theoretical=False)
    theoretical_commision = Commission(semaphore_theoretical, theoretical_queue, result_queue, dean_queue,
                                       evacuation_event,ending_event, theoretical=True)
    dean = Dean(students,dean_queue, evacuation_event,ending_event,student_number,student_grades,choosed_field,k)
    student_threads = [StudentRunner(student, practical_commision, theoretical_commision, evacuation_event) for student in students]


    # student_manager.start()
    for st in student_threads:
        time.sleep(random.uniform(0, choose_waiting_time))
        st.start()

    practical_commision.start()
    theoretical_commision.start()
    dean.start()

    practical_commision.join()
    theoretical_commision.join()
    dean.join()
    for st in student_threads:
        st.join()
   


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


    output = []
    output.append(f"chosen field: {dean.field}")
    output.append("ALL STUDENTS")
    output.append("=========================================================")
    output.extend([str(s) for s in students])
    output.append("=========================================================")
    output.append("STUDENTS WHO TOOK EXAM")
    output.append("=========================================================")
    output.extend([str(s) for s in students if s.field == dean.field])
    output.append("=========================================================")
    output.append("=== Final Results ===")
    for student_id, grades in student_grades.items():
        practical_grade = grades['praktyczna']
        theoretical_grade = grades['teoretyczna']
        if practical_grade is not None or theoretical_grade is not None:
            output.append(f"Student ID: {student_id}, Practical Grade: {practical_grade}, Theoretical Grade: {theoretical_grade}")
    output.append("=====================")

    # Write results to a file
    file_name = "wyniki.txt"
    with open(file_name, 'w') as f:
        f.write("\n".join(output))
    
    print(f"Results have been written to {file_name}")
    print("koniec")


if __name__ == "__main__":
    main()