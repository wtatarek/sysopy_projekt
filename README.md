Temat 13 – Egzamin - opis projektu

Zrobiłam dwie wersje projektu : 
1. wersja gdzie studenci są zwykłą klasą znajdujące się w pliku rozwiązanie2.py do którego testy są w pliku test_rozwiązanie2.py
2. wersja bardziej zgodna z wymogami zadania gdzie studenci są wątkami znajdująca się w pliku main.py

Poniżej znajduje się opis rozwiązania znajdującego się w main.py :

Założenia projektowe
Projekt symuluje egzaminowanie studentów przez komisję, uwzględniając egzaminy praktyczne i teoretyczne, synchronizację z użyciem wątków i procesów oraz obsługę zdarzeń ewakuacyjnych i zakończenia.


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

4. Łącza nazwane i nienazwane

    queue.Queue: Przykłady: 
    practical_queue = Queue()
    theoretical_queue = Queue()
    dean_queue = Queue()
    result_queue = Queue()

    [Linie 604-607 w main.py](https://github.com/wtatarek/sysopy_projekt/blob/main/main.py#L411-L440)

5. Kolejki komunikatów
    queue.Queue: Użyte w komunikacji między studentami a komisjami.
    Przykłady: 
    practical_queue = Queue()
    theoretical_queue = Queue()
    dean_queue = Queue()
    result_queue = Queue()

    [Linie 604-607 w main.py](https://github.com/wtatarek/sysopy_projekt/blob/main/main.py#L411-L440)



