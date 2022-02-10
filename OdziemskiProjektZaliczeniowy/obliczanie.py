import numpy as np

def oblicz_różnicę_lat(rok_poprz, rok_akt):
    '''
    Oblicza różnicę pomiędzy dochodami w roku poprzednim a tymi w aktualnym
    :param rok_poprz: Dane dotyczące roku poprzedniego
    :param rok_akt: Dane dotyczące roku aktualnego
    :return: Wejściowa ramka danych poszerzona o kolumnę z różnicą w dochodach między latami
    '''
    wynik = rok_akt
    wynik.rename(columns={'DOCHODY': 'DOCHODY_akt'}, inplace=True)
    wynik['DOCHODY_poprz'] = rok_poprz['DOCHODY']
    wynik["RÓŻNICA"] = round(wynik['DOCHODY_akt'] - wynik["DOCHODY_poprz"], 2)
    return wynik

def oblicz_śdo(dane, rok, procent_dla_jst, próg=.17, odsetek_pracujących=.6):
    '''
    Oblicza średni dochód opodatkowany na pracującego obywatela dla jednostki
    :param dane: Scalone dane dotyczące dochodów z PIT i liczby ludności
    :param rok: Rok, dla którego jest liczony ŚDO: aktualny ("akt") lub poprzedni ("poprz")
    :param procent_dla_jst: Odsetek z podatków, jaki przysługuje jednostce (np. .1025)
    :param próg: Próg podatkowy od zarobków (np. .17)
    :param odsetek_pracujących: Odsetek pracujących (np. .6)
    :return: Ramka danych uzupełniona o średni dochód opodatkowany
    '''
    dane["ŚDO_"+rok] = round(((dane["DOCHODY_"+rok]/procent_dla_jst)/(dane["LUD"]*odsetek_pracujących)/(próg))*(1-próg), 2)
    return dane

def oblicz_x_dla_podjednostek(dane_nad, dane_pod, jst_nad, rok, operacja):
    '''
    Wykonuje zadaną operację dla wybranej jednostki oraz jej jednostek podrzędnych
    :param dane_nad: Dane dotyczące jednostek nadrzędnych: województw lub powiatów
    :param dane_pod: Dane dotyczące jednostek nadrzędnych: powiatów lub gmin
    :param jst_nad: Jednostka nadrzędna: województwa ("wojew") lub powiaty ("powiaty")
    :param rok: Rok, dla którego jest liczony ŚDO: aktualny ("akt") lub poprzedni ("poprz")
    :param operacja: Operacją może być obliczenie wariancji (variance) lub średniej ważonej (sum)
    :return: Wejściowa ramka danych uzupełniona o wyniki wybranej operacji
    '''
    dane_nad[operacja.__name__+"_"+rok] = np.nan
    granica = 4     # Granicą jest tu nazywana pozycja cyfry, przed którą IT określa jednostkę nadrzędną
    if jst_nad == "wojew": granica = 2
    for i in range(dane_nad.shape[0]):
        elts = []
        for j in range(dane_pod.shape[0]):
            if dane_nad["IT"][i][:granica] == dane_pod["IT"][j][:granica]:
                elt = dane_pod["ŚDO_"+rok][j]
                if operacja == sum:
                    elt = (dane_pod["LUD"][j]/dane_nad["LUD"][i]) * elt
                elts.append(elt)
        if elts != []: dane_nad[operacja.__name__+"_"+rok][i] = round(operacja(elts), 2)
    return dane_nad

def oblicz_różnicę_średnich(dane, rok):
    '''
    Oblicza różnicę między średnim dochodem opodatkowanym jednostki a średnią ważoną średnich dochodów opodatkowanych jej podjednostek
    :param rok: Rok, dla którego jest liczony ŚDO: aktualny ("akt") lub poprzedni ("poprz")
    :return: ejściowa ramka danych uzupełniona o porównanie ŚDO ze średnią ważoną
    '''
    dane["RÓŻNICA_ŚR_DOCHODÓW_"+rok] = round(dane["ŚDO_"+rok] - dane["sum"+"_"+rok], 2)
    return dane