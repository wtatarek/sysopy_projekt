Temat 13 – Egzamin - opis projektu

Zrobiłam dwie wersje projektu : 
1. wersja gdzie pula wątków wykonuje kod studenta, a student to "dane" znajdująca się w pliku rozwiązanie2.py do którego testy są w pliku test_rozwiązanie2.py 
2. wersja bardziej zgodna z wymogami zadania gdzie wątek studenta robi wszystko po kolei znajdująca się w pliku main.py do którego testy są w pliku test_main.py

Poniżej znajduje się opis rozwiązania znajdującego się w main.py która jest wersją bardziej zgodną z wymogami:

Założenia projektowe
Projekt symuluje egzaminowanie studentów przez komisję, uwzględniając egzaminy praktyczne i teoretyczne oraz obsługę zdarzeń ewakuacyjnych i zakończenia.

Ogólny opis kodu
Kod tworzy strukturę symulacji, w której:
Studenci są przypisani do losowych kierunków studiów
Komisje (praktyczna i teoretyczna) obsługują studentów, oceniając ich odpowiedzi na pytania.
Dziekan koordynuje procesy, w tym wybór kierunku który ma egzamin oraz zarządzanie wynikami.
Synchronizacja odbywa się przy użyciu wątków i kolejek (Queue), a także za pomocą semaforów.
Obsługiwane są zdarzenia ewakuacji i zakończenia symulacji.

Co udało się zrobić

Zaimplementowano wielowątkowość i synchronizację za pomocą semaforów oraz kolejek.
Dodano obsługę losowego przypisywania studentów do kierunków oraz losowego zdawania egzaminów.
Zaimplementowano mechanizm oceny egzaminów z różnymi wagami i przedziałami ocen.
Problemy napotkane podczas pracy
Synchronizacja procesów wymagała szczególnej uwagi, aby uniknąć sytuacji deadlocków.
Implementacja obsługi zdarzeń ewakuacji wymagała dopracowania, aby zapewnić poprawne zakończenie wszystkich wątków.
Dodatkowe elementy specjalne
Wagi dla ocen egzaminacyjnych uwzględniają większe prawdopodobieństwo zdania.
Mechanizm dziekana zapewnia dynamiczną zmianę kierunku egzaminowanego w trakcie symulacji.

Odnośniki do kodu na GitHub

1. Tworzenie i obsługa wątków
    threading.Thread: Użycie w klasach takich jak StudentRunner
    [Linie 227-399 w main.py](https://github.com/wtatarek/sysopy_projekt/blob/main/main.py#L227-L399)

    Commission
    [Linie 76-223 w main.py](https://github.com/wtatarek/sysopy_projekt/blob/main/main.py#L76-L223)

    ThinkingSpace
    [Linie 443-478 w main.py](https://github.com/wtatarek/sysopy_projekt/blob/main/main.py#L443-L478)

    Dean
    [Linie 503-594 w main.py](https://github.com/wtatarek/sysopy_projekt/blob/main/main.py#L503-L594)

    CommisionMember
    [Linie 411-440 w main.py](https://github.com/wtatarek/sysopy_projekt/blob/main/main.py#L411-L440)



2. Tworzenie i obsługa plików
    użycie modułu os

    [Linie 657-678 w main.py](https://github.com/wtatarek/sysopy_projekt/blob/main/main.py#L657-L678)




3. Synchronizacja procesów/wątków
    threading.Semaphore:

    Linia: semaphore_practical = threading.Semaphore(3).
    [Linia 610 w main.py](https://github.com/wtatarek/sysopy_projekt/blob/main/main.py#L610)

    Linia: semaphore_theoretical = threading.Semaphore(3)
    [Linia 611 w main.py](https://github.com/wtatarek/sysopy_projekt/blob/main/main.py#L611)


    threading.Event:

    Linia: evacuation_event = threading.Event().
    [Linia 600 w main.py](https://github.com/wtatarek/sysopy_projekt/blob/main/main.py#L600)

    Linia: ending_event = threading.Event().
    [Linia 600 w main.py](https://github.com/wtatarek/sysopy_projekt/blob/main/main.py#L601)

    Linia: choosing_field_event = threading.Event().
    [Linia 600 w main.py](https://github.com/wtatarek/sysopy_projekt/blob/main/main.py#L602)


Główne elementy programu
    1.Klasy i struktury danych
        MessageTypes: Enum definiujący różne typy wiadomości przesyłanych między wątkami.
        Msg: Klasa przechowująca typ wiadomości oraz dane.
        StudyField: Klasa reprezentująca kierunki studiów, które mogą być wybierane przez studentów.
        Student: Klasa reprezentująca studenta, który ma ID, informację, czy zaliczył egzamin praktyczny, oraz kierunek studiów.
        Klasa reprezentuje tylko dane studenta a za faktyczne zachowanie każdego studenta odpowiada StudentRunner
        StudentData: Klasa przechowująca dane studenta, pytania egzaminacyjne oraz oceny.
        StudentGrade: Klasa przechowująca oceny studenta i informację, czy egzamin był teoretyczny.

    2.Generowanie studentów
        Funkcja generate_students generuje listę studentów, przypisuje im losowe ID, kierunek studiów oraz informację, czy zaliczyli wcześniej egzamin praktyczny.

    3.Działanie komisji egzaminacyjnej
        Klasa Commission reprezentuje komisję egzaminacyjną (praktyczną lub teoretyczną).
        Każda komisja składa się z trzech członków (CommisionMember). ComissionMember działa podobnie do modelu aktora - przyjmuje wiadomości z kolejki i je obsługuje a potem odsyła dalej
        Każda komisja (praktyczna i teoretyczna) jest odpalana w osobnym wątku. Wewnątrz komisji każdy członek komisji (3) jest odpalany w osobnym wątku.
        

    4.Zachowanie studentów
        Klasa StudentRunner reprezentuje zachowanie studenta.
        Student sprawdza, czy jego kierunek ma egzamin (sygnał od dziekana).
        Przechodzi proces egzaminu praktycznego i, jeśli zdał, egzamin teoretyczny.
        Żeby na raz w pokoju komisji nie było więcej niż 3 osoby mam dwa semafory o          pojemności 3 jeden do komisji praktycznej i jeden do teoretycznej .Zanim w klasie StudentRunner student zostanie dodany do kolejki pierwszego egzaminatora danej komisji używam acquire dla odpowiedniego semfora komisji . Semafor zwalniam za pomocą release gdy student odpowie na ostatnie pytanie
        Gdy student odpowie na wszystkie pytania - wysyła swoje odpowiedzi i czeka na ocenę.
        W przypadku ewakuacji (sygnał od dziekana) student opuszcza egzamin.

    5.Koordynacja przez dziekana
        Klasa Dean:
        Losuje kierunek, który przystąpi do egzaminu.
        Monitoruje oceny studentów, zbiera wyniki z komisji, i decyduje o zakończeniu egzaminu.
        Może wysłać sygnał ewakuacji, jeśli czas egzaminu przekroczy ustalony limit.
        Wyniki wszystkich studentów (zarówno tych, którzy zdali, jak i tych, którzy nie podeszli do egzaminu) są zapisywane w strukturze danych.

    6.Zapis wyników do pliku
        Na koniec programu, wyniki są zapisywane do pliku tekstowego (wyniki.txt). Zawartość pliku obejmuje:
        Wylosowany kierunek (pole "chosen field").
        Listę wszystkich studentów.
        Listę studentów, którzy podeszli do egzaminu.
        Finalne wyniki egzaminów teoretycznych i praktycznych.

    7. Funkcje dodatkowe
        broadcast_to_all_students: Rozsyła wiadomości do wszystkich studentów.
        print_dean_results: Wyświetla finalne wyniki studentów.
        count_students_with_field: Zlicza studentów przypisanych do danego kierunku.


 ---------------------------------------------------------------------------------------------------------------------------


Jeżeli chodzi o rozwiązanie znajdujące się w pliku rozwiazanie2.py to jest ono podobne z tym że pula wątków" wykonuje kod studenta, a student to "dane" 

Wizualny opis działania komisji w tym rozwiązaniu znajduje się w pliku schemat_komisji.jpg
Klasa Commission reprezentuje komisję egzaminacyjną (praktyczną lub teoretyczną).
Każda komisja składa się z trzech członków (CommisionMember) oraz trzech "miejsc do myślenia" (ThinkingSpace), które symulują proces odpowiadania na pytania przez studentów.
Każda komisja (praktyczna i teoretyczna) jest odpalana w osobnym wątku. Wewnątrz komisji każdy członek komisji (3) jest odpalany w osobnym wątku a także każda strefa myślenia (3) jest odpalana w osobnym wątku.

Rozwiązanie zawiera dodatkowe klasy:

    StudentManager - tworzy studentów na bierząco i dodaje ich do kolejki przed bydynkiem

    StudyFieldFilter - sprawdza czy studenci którzy ustawiają się w kolowym czasie przed budynkiem mogą być dodani do kolejki na egzamin praktyczny (są właściwego kierunku)

To rozwiązanie działa tak że “pula wątków” wykonuje kod studenta a student to “dane”

