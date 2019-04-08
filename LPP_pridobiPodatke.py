import requests as r;
import json
import time;

def zapisPodatkovGetRoutes(datotekaGetRoutes):
    """zapiše podatke pridobljene z getRoutes v datoteko"""
    LPP = 'http://data.lpp.si/routes/getRoutes';

    resp = r.get(LPP);
    txt = resp.text;
    with open(datotekaGetRoutes, "w", encoding="UTF-8") as file:
        file.write(txt)


def zapisVsePostaje(datotekaVsePostaje):
    '''zapiše podatke pridobljene z getAllStations v datoteko'''
    postaje =j son.loads(r.get("http://data.lpp.si/stations/getAllStations").text)["data"];
    jjjj = json.dumps(postaje)
    f = open(datoteka,"w")
    f.write(jjjj)
    f.close()
    
def zapisPodatkovOLinijah(datotekaGetRoutes, datotekaRoutPostaje):
    """ pridobi podatke o posamezni avtobusni liniji, jih zapiše na datoteko"""
    
    routes="";
    with open(datotekaGetRoutes, "r", encoding="UTF-8") as file:
        routes = str("".join(file.readlines()));
    y = json.loads(routes)
    tabR = y["data"]
    params = None
    routPostaje = dict();
    c = len(tabR)
    for relacija in tabR:
        print("poslati moram še: "+str(c))
        c-=1
        params = {"route_id": relacija["id"], 
        "route_int_id": relacija["int_id"]}#pravzaprav potrebujemo le enega od teh dveh parametrov
        routPostaje[relacija["id"]] = json.loads(r.get("http://data.lpp.si/routes/getStationsOnRoute", params).text)["data"];
    jjjj = json.dumps(routPostaje)
    f = open(datotekaRoutPostaje,"w")
    f.write(jjjj)
    f.close()
    
def zapisPostajaKoordinate(datotekaGetRoutes, datotekaRoutPostaje, datotekapostajaKoordinate):
    """uredi podatke kot postaja, koordinate ter to zapiše na datoteko"""
    routes="";
    with open(datotekaGetRoutes, "r", encoding="UTF-8") as file:
        routes = str("".join(file.readlines()));

    routs = json.loads(routes)["data"];
    tmp="";
    with open(datotekaRoutPostaje, "r", encoding="UTF-8") as file:
        tmp = str("".join(file.readlines()));
    rPostaje = json.loads(tmp)
    idSt = dict();
    for x in routs:
        idSt[x["id"]] = x["group_name"] + " " + x["parent_name"];
    post = dict();
    for (ID,postaje) in rPostaje.items():
        for postaja in postaje:
            ime = postaja["name"];
            if not ime in post.keys():
                post[ime]={"set":set(),
                           "koords":postaja["geometry"]["coordinates"]};
            post[ime]["set"].add(idSt[ID]);
            
    with open(datotekapostajaKoordinate, "w", encoding="UTF-8") as file:
        for x,y in post.items():
            txt = x +'\t'+ str(len(y["set"])) +'\t'+ str(y["koords"])+ "\n"
            file.write(txt)
            

def zapisLinijaOdhodi(datotekaGetRoutes, datotekaRoutDeparts):
    '''pridobi podatke za vsako linijo kdaj odpelje iz končnega postajališča'''
    routes="";
    with open(datoteka, "r", encoding="UTF-8") as file:
        routes = str("".join(file.readlines()));

    routs = json.loads(routes)["data"];
    departs = dict()
    i = len(routs);
    print("loop")
    for x in routs:
        departs[x["id"]] = json.loads(r.get("http://data.lpp.si/timetables/getRouteDepartures", {"route_id": x["id"]}).text);
        print("še" + str(i))
        i-=1;

    jjjj = json.dumps(departs)
    f = open(datotekaRoutDeparts,"w")
    f.write(jjjj)
    f.close()


def zapisPostajaVsiOdhodi(datotekaVsePostaje, datotekaOdhodiIzPostaj):
    '''za vsako postajo pridobi odhode vseh avtobusov in jih zapiše v datoteko'''
    tmp="";
    with open(datotekaVsePostaje, "r", encoding="UTF-8") as file:
        tmp = str("".join(file.readlines()));

    postaje = json.loads(tmp)
    arrs = dict()
    i = len(postaje);
    print("loop")
    for x in postaje:
        arrs[x["int_id"]] = json.loads(r.get("http://data.lpp.si/timetables/getArrivalsOnStation", {"station_int_id": x["int_id"]}).text)["data"];
        print("pridobivam" + str(i))
        i-=1;

    jjjj = json.dumps(arrs)
    f = open(datotekaOdhodiIzPostaj, "w")
    f.write(jjjj)
    f.close()


zapisVsePostaje("vsePostaje.json"):
zapisPodatkovGetRoutes("getRoutes.json")
zapisPodatkovOLinijah("getRoutes.json", "routPostaje.json")
zapisLinijaOdhodi("getRoutes.json", "routDeparts.json")
zapisPostajaKoordinate("getRoutes.json", "routPostaje.json", "LPP_postaja_avtobusi_koordinate.txt")
zapisPostajaVsiOdhodi("vsePostaje.json", "odhodiIzPostaj.json"):