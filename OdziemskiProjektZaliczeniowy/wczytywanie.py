import argparse
from wyjątki import BłądNazwyPliku
import pandas as pd
import numpy as np


def daj_listę_plików():
    '''
    Zwraca listę plików zadanych w wierszu poleceń
    '''
    parser = argparse.ArgumentParser() # Pliki Excela są wczytywane w dowolnej kolejności (dla wygody użytkownika)
    parser.add_argument('arg1', type=str)
    parser.add_argument('arg2', type=str)
    parser.add_argument('arg3', type=str)
    parser.add_argument('arg4', type=str)
    parser.add_argument('arg5', type=str)
    parser.add_argument('arg6', type=str)
    parser.add_argument('arg7', type=str)
    parser.add_argument('arg8', type=str)
    parser.add_argument('arg9', type=str)
    parser.add_argument('arg10', type=str)
    parser.add_argument('arg11', type=str)
    args = parser.parse_args()
    return list(vars(args).values())


def uporządkuj_listę_plików(lista, rok_poprz, rok_akt):
    '''
    Tworzy listę używanych plików w kolejności właściwej dla dalszego użycia
    :param lista: Lista nazw wszystkich używanych plików (w dowolnej kolejności)
    :param rok_poprz: Poprzedni rok (lub wcześniejszy spośród porównywanych)
    :param rok_akt: Aktualny rok (lub późniejszy spośród porównywanych)
    :return: Lista nazw wszystkich używanych plików we właściwej kolejności
    '''

    # Wartości początkowe
    gminy_poprz = gminy_akt = powiaty_poprz = powiaty_akt = wojew_poprz = wojew_akt = miasta_poprz = miasta_akt = lud_gminy = lud_powiaty = lud_wojew = None

    for e in lista:
        if "Gminy" in e and rok_poprz == e[-9:-5]:
            gminy_poprz = e
        if "Gminy" in e and rok_akt == e[-9:-5]:
            gminy_akt = e
        if "Powiaty" in e and rok_poprz == e[-9:-5]:
            powiaty_poprz = e
        if "Powiaty" in e and rok_akt == e[-9:-5]:
            powiaty_akt = e
        if "Wojew" in e and rok_poprz == e[-9:-5]:
            wojew_poprz = e
        if "Wojew" in e and rok_akt == e[-9:-5]:
            wojew_akt = e
        if "Miasta" in e and rok_poprz == e[-9:-5]:
            miasta_poprz = e
        if "Miasta" in e and rok_akt == e[-9:-5]:
            miasta_akt = e
        if "Tabela_II" in e and "Tabela_III" not in e:
            lud_wojew = e
        if "Tabela_III" in e:
            lud_powiaty = e
        if "Tabela_IV" in e:
            lud_gminy = e
    pliki = [gminy_poprz, gminy_akt, powiaty_poprz, powiaty_akt, wojew_poprz, wojew_akt, miasta_poprz, miasta_akt, lud_gminy, lud_powiaty, lud_wojew]
    # Jeżeli nazwa któregoś pliku będzie niepoprawna, program zwróci błąd z informacją, jak powinny wyglądać nazwy
    if None in pliki: raise BłądNazwyPliku("Niepoprawna nazwa przynajmniej jednego pliku \nNazwy plików z danymi o dochodach z PIT powinny zawierać odpowiednio frazę \"Wojew\", \"Powiaty\", \"Gminy\" lub \"Miasta\" oraz kończyć się odpowiednią nazwą roku i rozszerzeniem .xlsx \nNazwy plików z danymi o liczbie ludności powinny zawierać frazę \"Tabela_II\" dla danych dotyczących województw, \"Tabela_III\" dla powiatów oraz \"Tabela_IV\" dla gmin")
    return pliki

def wczytaj_plik(dane, liczba_przeskakiwanych_wierszy=3):
    '''
    Wczytuje plik .xlsx lub .xls o odpowiedniej nazwie
    :param dane: Nazwa pliku
    :param liczba_przeskakiwanych_wierszy: Liczba wierszy początkowych, które zostaną pominięte
    :return: Ramka danych na podstawie pliku
    '''
    dane = pd.read_excel(dane, skiprows=3)
    # Z tym arkuszem trzeba dopracować, żeby był opcjonalny
    dane = dane.drop(range(liczba_przeskakiwanych_wierszy)) # Wyrzucenie wierszy poprzedzających właściwe dane
    wynik = dane.reset_index()
    return wynik

def zestringuj_kolumny(dane, kolumny, do_tych_dopisz_zero=[], docelowa_dł_zaw_kom = 2):
    '''
    Zmienia typ wybranych kolumn na string. Ma na celu zachowanie pełnego kodu tam, gdzie zaczyna się on od "0"
    :param dane: Wybrana ramka danych
    :param kolumny: Kolumny, których typ ma zostać zmieniony na string. Należy podać listę
    :param do_tych_dopisz_zero: Kolumny, w których wartości mają (przynajmniej w niektórych przypadkach) zaczynać się od "0". Należy podać listę lub wpisać 'wszystkie'
    :param docelowa_dł_zaw_kom: Długość zawartości komórki w wybranych kolumnach
    :return:
    '''
    if do_tych_dopisz_zero == 'wszystkie':
        do_tych_dopisz_zero = kolumny
    dane = dane.fillna(0)
    for kolumna in kolumny:
        dane = dane.astype({kolumna: int}) # Najpierw int, żeby str złapało samo np. "32", a nie "32.0"
        dane = dane.astype({kolumna: str})
        if kolumna in do_tych_dopisz_zero:
            for i in range(len(dane[kolumna])):
                if len(dane[kolumna][i]) < docelowa_dł_zaw_kom:
                    dane[kolumna][i] = '0'+dane[kolumna][i]
    return dane

def wyrzuć_zbędne_kol(dane):
    '''
    Usuwa automatycznie tworzone, zbędne kolumny z indeksami
    '''
    dane.drop(["index"], axis=1, inplace=True)
    if "levels_0" in dane.columns: dane.drop(["levels_0"], axis=1, inplace=True)
    return dane

def daj_df(dane, jst, rodzaj="pit"):
    '''
    Tworzy ramkę danych, która dla każdej jednostki zawiera jej nazwę, kod oraz dochody.
    :param dane: Dame, na podstawie których powstaje ramka
    :param jst: Jednostka samorządu terytorialnego: województwa ("wojew"), powiaty ("powiaty") lub gminy ("gminy")
    :param rodzaj: Rodzaj danych wejściowych: dotyczące dochodu z PIT ("pit") lub dotyczące liczby ludności ("lud")
    '''
    wynik = pd.DataFrame()
    if rodzaj=="pit":
        wynik["JST"] = dane["Nazwa JST"]
        wynik['IT'] = dane['WK']
        wynik["DOCHODY"] = dane["Dochody wykonane\n(wpłaty minus zwroty)"]
        if jst == "gminy":
            wynik['IT'] += dane['PK'] + dane['GK'] + dane['GT']
        if jst == "powiaty":
            wynik['IT'] += dane['PK']
    if rodzaj=="lud":
        wynik = pd.DataFrame()
        if jst == "wojew":
            wynik["JST"] = dane["Województwa\nVoivodships"]
            wynik = wynik[:][:16]
        if jst == "powiaty":
            wynik["JST"] = dane["Województwa \nVoivodships\nPowiaty\nPowiats"]
            wynik["IT"] = dane["Identyfikator terytorialny\nCode"]
        if jst == "gminy":
            wynik["JST"] = dane["Województwa\nVoivodships\nGminy\nGminas"]
            wynik["IT"] = dane["Identyfikator terytorialny\nCode"]
        wynik["LUD"] = dane["Ludność\n(stan w dniu 31.12)\nPopulation\n(as of \nDecember 31)"]
    wynik = wynik.reset_index()
    wynik = wyrzuć_zbędne_kol(wynik)
    return wynik

def wyczyść_z_woj(dane, początek_wyrzucanych):
    '''
    Usuwa z ramki danych wiersze dotyczące całych województw, a nie powiatów lub gmin
    :param początek_wyrzucanych: Pierwsze cztery znaki w kolumnie "JST" wierszy, które należy wyrzucić (np. "WOJ.")
    '''
    do_wyrzucenia = []
    for i in range(dane.shape[0]):
        if dane["JST"][i][0:4] == początek_wyrzucanych:
            do_wyrzucenia.append(i)
    wynik = dane.drop(do_wyrzucenia)
    wynik = wynik.reset_index()
    wynik = wyrzuć_zbędne_kol(wynik)
    return wynik

def wyczyść_dochody_dla_miast(dane):
    '''
    Usuwa z ramki danych dla miast niepotrzebne wiersze
    '''
    długość = dane.shape[0]
    for i in range(1, długość, 2):
        dane = dane.drop(labels=i-1, axis=0)
    wynik = dane.reset_index()
    wynik = wyrzuć_zbędne_kol(wynik)
    return wynik

def scal_dane(dane_pit, dane_lud, jst):
    '''
    Łączy dane dotyczące dochodów z PIT z tymi dotyczącymi liczby ludności w jedną ramkę
    :param dane_pit: Dane dotyczące dochodów z PIT
    :param dane_lud: Dane dotyczące liczby ludności
    :param jst: Jednostka samorządu terytorialnego: województwa ("wojew"), powiaty ("powiaty") lub gminy ("gminy")
    '''
    dane_pit["LUD"] = np.nan
    dane_pit = dane_pit.reset_index()
    dane_lud = dane_lud.reset_index()
    for i in range(dane_pit.shape[0]):
        for j in range(dane_lud.shape[0]):
            if jst == "wojew":
                if str(dane_pit["JST"][i])[1:] == str(dane_lud["JST"][j])[1:]: # Bez pierwszej litery, bo dla różnych danych
                    dane_pit["LUD"][i] = dane_lud["LUD"][j]         # ma ona różną wielkość
                    break   # W przypadku województw łączymy po nazwach, nie IT, bo w pliku z liczbą ludności woj. nie było IT
            if jst == "powiaty":
                if dane_pit["IT"][i] == dane_lud["IT"][j]:
                    dane_pit["LUD"][i] = dane_lud["LUD"][j]
                    break
            if jst == "gminy":
                if str(dane_pit["IT"][i])[:-1] == str(dane_lud["IT"][j])[:-1]: # Bez ostatniej cyfry, bo jest ona różna dla plików
                    dane_pit["LUD"][i] = dane_lud["LUD"][j] # (oznacza miejskość/wiejskość, a niektóre wsie stały się miastami)
                    break # Pierwsze sześć cyfr pozwala jednoznacznie zidentyfikować gminę
    wynik = wyrzuć_zbędne_kol(dane_pit)
    return wynik