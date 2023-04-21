// Boldeanu Ana-Maria
// ASC - Tema 1 - Marketplace

========================== Descrierea soluției alese ==========================

    Rezolvarea temei este destul de straight-forward. Am folosit un dicționar,
carts, pentru a reține o perechile de tipul <id_consumer, cart>, unde cart este
lista de produse rezervate de consumatorul respectiv. Produsele din lista cart
sunt salvate sub forma de tuplu (buffer_idx, product) pentru a reține indexul
bufferului din care a provenit produsul, pentru eventualitatea în care acesta
este șters din coș și trebuie returnat în stocul producătorului.

    Pentru bufferele producătorilor, am folosit dicționarul producers_buffers,
cu perechi de tipul <id_producer, buffer>, buffer fiind o listă de produse.
Am preferat structura de date listă deoarece era nevoie să pot elimina elemente
de la orice poziție din listă. Pentru limitarea dimensiunii bufferelor, am
folosit len(<list>).

    Pentru a adăuga un produs în coș, consumatorul va parcurge pe rând bufferele
producătorilor și își va păstra prima instanță găsită a produsului dorit.

    Drept elemente de sincronizare, am folosit Lock(), câte unul pentru fiecare
din următoarele situații:
1. producers_id_lock - pentru contorizarea numărului de producători înregistrați
                și acordarea lor de ID-uri unice (variabilă atomică)
2. consumers_id_lock - la fel, pentru consumatori.
3. buffer_removal_lock - la nivelul funcției add_to_cart, folosit pentru eliminarea
                produsului din stocul producătorilor (astfel, el nu mai e valabil
                pentru alți consumatori). Era necesar deoarece nu vrem ca 2
                Consumer threads să găsească produsul în același timp și să și-l
                rezerve fiecare, în plus încercând apoi să îl șteargă de 2 ori.
4. print_lock - un mutex folosit pentru apelurile funcției print(), care nu este
                thread-safe, de către consumatori.

    Implementarea pare eficientă, cu excepția unui caz special care ține de
decizia folosirii remove() pentru a rezerva produse. Exista posibilitatea ca un
consumator să rezerve un produs, iar apoi producătorul să-și reumple bufferul.
Dar când consumatorul șterge produsul din coș, acesta se va întoarce în buffer,
indiferent dacă e plin. Am considerat totuși că nu e o problemă, având în vedere
că, din punctul de vedere al producătorului, acesta rămâne limitat la a avea
maxim queue_size_per_producer produse publicate la un moment dat.


================================ Implementare =================================

    Sunt implementate toate cerințele temei, toate testele trec.

    Am implementat atât partea de unit testing, cât și cea de logging.

    Am folosit versionarea cu ajutorul git.


============================== Resurse utilizate ==============================

Foarte util --- https://ocw.cs.pub.ro/courses/asc/laboratoare/02
Liste in python --- https://docs.python.org/3/tutorial/datastructures.html
Unit testing --- https://docs.python.org/3/library/unittest.html#assert-methods
Un răspuns salvator pentru modul de în care se face setup la logger ---
https://stackoverflow.com/questions/3220284/how-to-customize-the-time-format-for-python-logging


===================================== Git =====================================

https://github.com/ana-boldeanu/ASC_Tema_1

===============================================================================