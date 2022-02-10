from wczytywanie import *
from  obliczanie import *
from wyjątki import NiewłaściwaLiczbaNazw
from statistics import variance
import pandas as pd
import sys
import cProfile

def main():
    rok_poprz = '2019'
    rok_akt = '2020'
    odsetek_dla_gmin_poprz = .3808
    odsetek_dla_gmin_akt = .3816            # Te wartości można łatwo zmienić, jeśli będziemy chcieli robić analizę dla innych lat

    # Jeżeli nie wszystkie nazwy plików zostaną podane w wierszu poleceń lub zostanie podane za dużo, program zwróci błąd

    if len(sys.argv) != 12: raise NiewłaściwaLiczbaNazw("Należy podać w wierszu poleceń dokładnie 11 nazw plików")

    pliki = uporządkuj_listę_plików(daj_listę_plików(), rok_poprz, rok_akt)

    # Przygotowanie danych

    gminy_poprz = daj_df(zestringuj_kolumny(wczytaj_plik(pliki[0]), ['WK', 'PK', 'GK', 'GT'], ['WK', 'PK', 'GK']), "gminy")
    gminy_akt = daj_df(zestringuj_kolumny(wczytaj_plik(pliki[1]), ['WK', 'PK', 'GK', 'GT'], ['WK', 'PK', 'GK']), "gminy")
    powiaty_poprz = daj_df(zestringuj_kolumny(wczytaj_plik(pliki[2]), ['WK', 'PK'], 'wszystkie'), "powiaty")
    powiaty_akt = daj_df(zestringuj_kolumny(wczytaj_plik(pliki[3]), ['WK', 'PK'], 'wszystkie'), "powiaty")
    wojew_poprz = daj_df(zestringuj_kolumny(wczytaj_plik(pliki[4]), ['WK'], 'wszystkie'), "wojew")
    wojew_akt = daj_df(zestringuj_kolumny(wczytaj_plik(pliki[5]), ['WK'], 'wszystkie'), "wojew")
    miasta_poprz = wyczyść_dochody_dla_miast(daj_df(zestringuj_kolumny(wczytaj_plik(pliki[6]), ['WK', 'PK'], ['WK']), "powiaty"))
    miasta_akt = wyczyść_dochody_dla_miast(daj_df(zestringuj_kolumny(wczytaj_plik(pliki[7]), ['WK', 'PK'], ['WK']), "powiaty"))
    lud_gminy = wyczyść_z_woj(daj_df(zestringuj_kolumny(wczytaj_plik(pliki[8], 4), ["Identyfikator terytorialny\nCode"], 'wszystkie', 7), "gminy", "lud"), "WOJ.")
    lud_powiaty = wyczyść_z_woj(daj_df(zestringuj_kolumny(wczytaj_plik(pliki[9], 4), ["Identyfikator terytorialny\nCode"], 'wszystkie', 4), "powiaty", "lud"), "Woj.")
    lud_wojew = daj_df(wczytaj_plik(pliki[10], 4), "wojew", "lud")

    powiaty_poprz = pd.concat([powiaty_poprz, miasta_poprz])
    powiaty_akt = pd.concat([powiaty_akt, miasta_akt])      # Włączenie danych o miastach npp do danych o powiatach

    # Porównania między dochodami w różnych latach

    gminy = oblicz_różnicę_lat(gminy_poprz, gminy_akt)
    powiaty = oblicz_różnicę_lat(powiaty_poprz, powiaty_akt)
    wojew = oblicz_różnicę_lat(wojew_poprz, wojew_akt)

    # Scalenie danych dotyczących dochodów z tymi dotyczącymi liczby ludności

    gminy = scal_dane(gminy, lud_gminy, "gminy")
    powiaty = scal_dane(powiaty, lud_powiaty, "powiaty")
    wojew = scal_dane(wojew, lud_wojew, "wojew")

    # Obliczenie średniego dochodu opodatkowanego

    gminy = oblicz_śdo(gminy, "poprz", odsetek_dla_gmin_poprz)
    powiaty = oblicz_śdo(powiaty, "poprz", .1025)
    wojew = oblicz_śdo(wojew, "poprz", .016)

    gminy = oblicz_śdo(gminy, "akt", odsetek_dla_gmin_akt)
    powiaty = oblicz_śdo(powiaty, "akt", .1025)
    wojew = oblicz_śdo(wojew, "akt", .016)

    # Obliczanie wariancji dochodów w jednostkach podrzędnych

    powiaty = oblicz_x_dla_podjednostek(powiaty, gminy, "powiaty", "poprz", variance)
    wojew = oblicz_x_dla_podjednostek(wojew, powiaty, "wojew", "poprz", variance)

    powiaty = oblicz_x_dla_podjednostek(powiaty, gminy, "powiaty", "akt", variance)
    wojew = oblicz_x_dla_podjednostek(wojew, powiaty, "wojew", "akt", variance)

    # Obliczanie średniej ważonej jednostek podrzędnych dla jednostek nadrzędnych

    powiaty = oblicz_x_dla_podjednostek(powiaty, gminy, "powiaty", "poprz", sum)
    wojew = oblicz_x_dla_podjednostek(wojew, powiaty, "wojew", "poprz", sum)

    powiaty = oblicz_x_dla_podjednostek(powiaty, gminy, "powiaty", "akt", sum)
    wojew = oblicz_x_dla_podjednostek(wojew, powiaty, "wojew", "akt", sum)

    # Obliczanie różnicy między średnich dochodem dla jednostki nadrzędnej a średnią średnich dochodów jednostek podrzędnych

    powiaty = oblicz_różnicę_średnich(powiaty, "poprz")
    wojew = oblicz_różnicę_średnich(wojew, "poprz")

    powiaty = oblicz_różnicę_średnich(powiaty, "akt")
    wojew = oblicz_różnicę_średnich(wojew, "akt")

    # Dostosowanie nazw kolumn

    gminy.columns = ["Nazwa JST", "Identyfikator terytorialny", "Dochody w "+rok_akt, "Dochody w "+rok_poprz, "Różnica między "+rok_akt+" a "+rok_poprz, "Liczba ludności w JST", "Średni dochód opodatkowany w "+rok_poprz, "Średni dochód opodatkowany w "+rok_akt]
    powiaty.columns = ["Nazwa JST", "Identyfikator terytorialny", "Dochody w "+rok_akt, "Dochody w "+rok_poprz, "Różnica między "+rok_akt+" a "+rok_poprz, "Liczba ludności w JST", "Średni dochód opodatkowany (ŚDO) w "+rok_poprz, "Średni dochód opodatkowany (ŚDO) w "+rok_akt, "Wariancja ŚDO w podjednostkach JST w "+rok_poprz, "Wariancja ŚDO w podjednostkach JST w "+rok_akt, "Średnia ważona ŚDO w podjednostkach JST w "+rok_poprz, "Średnia ważona ŚDO w podjednostkach JST w "+rok_akt, "Różnica między ŚDO dla JST a średnią ważoną dla podjednostek w "+rok_poprz, "Różnica między ŚDO dla JST a średnią ważoną dla podjednostek w "+rok_akt]
    wojew.columns = ["Nazwa JST", "Identyfikator terytorialny", "Dochody w "+rok_akt, "Dochody w "+rok_poprz, "Różnica między "+rok_akt+" a "+rok_poprz, "Liczba ludności w JST", "Średni dochód opodatkowany (ŚDO) w "+rok_poprz, "Średni dochód opodatkowany (ŚDO) w "+rok_akt, "Wariancja ŚDO w podjednostkach JST w "+rok_poprz, "Wariancja ŚDO w podjednostkach JST w "+rok_akt, "Średnia ważona ŚDO w podjednostkach JST w "+rok_poprz, "Średnia ważona ŚDO w podjednostkach JST w "+rok_akt, "Różnica między ŚDO dla JST a średnią ważoną dla podjednostek w "+rok_poprz, "Różnica między ŚDO dla JST a średnią ważoną dla podjednostek w "+rok_akt]

    # Zwrot wyniku

    writer = pd.ExcelWriter('OdziemskiZadanieZaliczeniowe.xlsx', engine='xlsxwriter')
    gminy.to_excel(writer, sheet_name='Gminy', index=False)
    powiaty.to_excel(writer, sheet_name='Powiaty (i miasta NPP)', index=False)
    wojew.to_excel(writer, sheet_name='Województwa', index=False)
    writer.save()
main()
#cProfile.run("main()")