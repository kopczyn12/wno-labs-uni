
# Chess WNO

  
  

## Spis treści

  

- [Ile rzeczy zawiera program](#ile-rzeczy-zawiera-program)

- [Jak odpalać oraz mechanika gry](#jak-odpalać-oraz-mechanika-gry)

  

## Ile rzeczy zawiera program
-   **QGraphicsScene** (1 pkt)
-   Dziedziczenie po **QGraphicsItem** (1 pkt)
-   Każda bierka musi być kilkalna i przeciągalna, menue na rpm zmieniające grafikę (3 pkt)
-   Sterowanie z klawiatury za pomocą notacji szachowej w polu tekstowym (2 pkt)
- Analogowy, klikalny zegar szachowy ze wskazówką milisekundnika (2 pkt)
- Zaznaczanie możliwych ruchów (2 pkt)
- Grafiki załączane z qrc
Suma = 12 pkt / 15 pkt

## Jak odpalać oraz mechanika gry
**Po prostu python3 main.py**
*Zainstalowany powinien być PyQt5.*
**Grę rozpoczynają szachy białe.** **Aby skorzystać z notacji szachowej, wpisujemy w polu tekstowym indeks figury (nazwę, czyli np. K - king) oraz pole, na które chcemy ruszyć. Jeżeli ruch jest dozwolony, program wykona polecenie. Uwaga - przy sterowaniu pionkami notacją szachową wystarczy wpisywać indeks pola, na które chcemy się udać czyli np. c3.**

**Zegar klika się przyciskiem po zakończeniu tury (tzn. jak użytkownik skończy ruch) - odlicza milisekundy.
Aby zmienić skin planszy, prawy przycisk i wybieramy z menu.
Sterowanie przeciąganiem i zaznaczenie ruchów działa tak jak powinno według polecenia**

**Wymagane dziedziczenia zostały użyte.**

***Uwaga - kod mało okomentowany, ze względu na późne rozpoczęcie prac, fory w highlight bardzo ułatwiają implemenetację i nie spowolniają programu, mozna powiedziec, ze zoptymalizowane ***

