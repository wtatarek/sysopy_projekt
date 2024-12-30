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
threading.Thread: Użycie w klasach takich jak StudentRunner, Commission, ThinkingSpace.