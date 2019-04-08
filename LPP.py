#!/usr/bin/python
# coding = utf8
import matplotlib.pyplot as plt
from dateutil import parser;
import numpy as np
import requests as r;
import json
import time;

#-----------------------------------------------------------------------------------------------------------------  

def risanjeSlike(datotekapostajaKoordinate):
    """nariše graf 'Gostota LPP povezav glede na postaje' """

    mesta = {'Žiri':{46.05107, 14.110623}, 'Logatec': {45.91774, 14.229943}, 'Brezovica':{46.0242,  14.4174}, 'Medvode':{46.140248, 14.413671}, 'Vrhnika':{45.96425, 14.296305}, "Grosuplje":{45.957141, 14.65593}, 'Ig':{45.959241, 14.527601}}
    podatki = []
    with open(datotekapostajaKoordinate, 'r') as file:
        for vrstica in file:
            podatki.append(vrstica.rstrip().split('\t'))


    postaja = [ele[0] for ele in podatki]
    stBusev = [float(ele[1]) for ele in podatki]
    koordinate = [ele[2] for ele in podatki]
    fig = plt.figure()
    
    for i, ele in enumerate(koordinate):
        razdeljen = ele.split(', ')
        dolzina, sirina = razdeljen[0][1:], razdeljen[1][:-1]
        paint = plt.scatter([float(dolzina)], [float(sirina)], marker = 'o', s = stBusev[i], cmap= 'Paired')

    for mesto, place in mesta.items():
        dolzina, sirina = list(place)[0], list(place)[1]
        plt.annotate(mesto, (dolzina, sirina))

    plt.xlabel('Dolžina')
    plt.ylabel('Širina')
    plt.title('Gostota LPP povezav glede na postaje', fontweight = 'bold')
    plt.show()
#-----------------------------------------------------------------------------------------------------------------  
 
def naloziPodatke2(datotekaGetRoutes, datotekaOdhodiIzPostaj, datotekaRoutDeparts): 
    rr="";
    with open(datotekaGetRoutes, "r", encoding="UTF-8") as file:
        rr = str("".join(file.readlines())); 
    routes = json.loads(rr)["data"];

    with open(datotekaOdhodiIzPostaj, "r", encoding="UTF-8") as file:
        rr = str("".join(file.readlines())); 
    routeDeparts = json.loads(rr);

    with open(datotekaRoutDeparts, "r", encoding="UTF-8") as file:
        rr = str("".join(file.readlines())); 
    odhodiKoncne = json.loads(rr);
    
    return (routes, routeDeparts, odhodiKoncne);
    
def risanjeSlike2(routeDeparts, odhodiKoncne):
    '''uredimo podatke tako, da za vsako minuto vemo koliko avtobusov je na cesti'''
    prihodiNaPostaje = dict();#slovar s ključi id_odhoda bo vseboval tabelo postaj, ki jih vsak avtobus po odhodu obišče
    for ID, tab in routeDeparts.items():#id postaje in tab prihodov na to postajo;
        for y in tab:#na vsaki postaji imamo več prihodov različnih avtobsov
            depId = y["route_departure_int_id"];
            if(prihodiNaPostaje.get(depId, -1) == -1):#če ključa še ni v slovarju
                prihodiNaPostaje[depId] = list();
            prihodiNaPostaje[depId].append(y);

    minute = [[0 for y in range(60)] for x in range(24)];#2D tabela ur in minut v dnevu
    for ID, tab in prihodiNaPostaje.items():#v tabeli tab imamo vse postaje in prihode nanje (za vse avtobuse in vse linije)
        tab.sort(key = lambda x:(x["arrival_time"]));#uredimo, od najprej do najkasnejšega časa
        #časi so oblike 2019-03-26T06:00:00.000Z zato jih parsamo
        start = parser.parse(tab[0]["arrival_time"]);#kdaj je avtobus speljal iz prvega postajališča
        end = parser.parse(tab[-1]["arrival_time"]);#čas na zadnjem postajališču
        minute[start.hour][start.minute] += 1; #zabeležimo en avtobus več na cesti
        minute[end.hour][end.minute] -= 1; #zabeležimo en avtobus več na cesti

    mins = [0 for x in range(1440)]; #minute dneva
    skp = 0;#koliko jih je trenutno na cesti
    for i,x in enumerate(minute):
        for j,y in enumerate(x):
            skp += y;
            mins[i*60 + j] = skp;
            

    #začnemo risanje
    fig, ax = plt.subplots();#dobimo okolico grafa in osi posebej
    plt.xticks([x for x in range(0,1441,60)], (str(x)+":00" for x in range(0,25)));#označevanje x osi na 60 minut zapišemo ura:00
    plt.plot(mins);#vrednosti, ki jih rišemo
    plt.grid(True);#dodamo mrežo
    ax.set_xlim(0, 1440);#meji grafa
    fig.autofmt_xdate();#zasukamo oznake na x osi
    plt.show();

def razlikeDolzin(routes):
    '''funkcija izračuna razlike dolžin med linijo in njeno nasprotno linijo in izpiše top 5'''
    routeById = dict();#poti si bomo shranili po IDjih
    for x in routes:
        routeById[x["int_id"]] = x;

    razlikeDolzin = list();
    for ID, pot in routeById.items():#v tabelo dodamo podatke o razliki dolžine avtobusne linije in njene nasprotne linije
        if(pot["opposite_route_int_id"]!=None):
            razlikeDolzin.append( (abs(pot["length"]-routeById[pot["opposite_route_int_id"]]["length"]), pot["group_name"]+" "+pot["parent_name"]) );

    razlikeDolzin = sorted(razlikeDolzin, reverse=True)[::2];#ker se linije podvajajo lahko vzamemo le vsako drugo
    print("\n5 linij z največjo razliko v razdalji s svojo nasprotno linijo");
    for i in range(5):
        dol = razlikeDolzin[i];
        print(str(int(dol[0])) + "m: " + dol[1]);
        
    return routeById;


def dolzineLinij(routes):
    '''funkcija primerja dolžine linij in izpiše top 5'''
    dolzinePoti = [];
    for x in routes:#v tabelo dodamo pare s podatki (group name je številka avtobusa)
        dolzinePoti.append( (x["length"], x["group_name"]+" "+x["parent_name"], x["route_name"]) );

    dolzinePoti.sort(reverse=True);
    print("\n5 najdaljših avtobusnih linij");
    for i in range(5):
        dol = dolzinePoti[i];
        print(str(int(dol[0])) + "m: " + dol[1]);

    print("\n5 najkrajših avtobusnih linij");
    for i in range(5):
        dol = dolzinePoti[-1-i];
        print(str(int(dol[0])) + "m: " + dol[1]);


#----------------------------------------------------------------------------------------------------------------- 

risanjeSlike("LPP_postaja_avtobusi_koordinate.txt")

routes, routeDeparts, odhodiKoncne = naloziPodatke2("getRoutes.json", "odhodiIzPostaj.json", "routDeparts.json");
dolzineLinij(routes);
razlikeDolzin(routes);
risanjeSlike2(routeDeparts, odhodiKoncne);

