# -*- coding: utf-8 -*-
"""Turismo Internacional v16 - Terminal Python organizada por etapas."""
import json, os, re
from pathlib import Path
from datetime import datetime

BASE=Path(__file__).resolve().parent
DATA=json.loads((BASE/'catalogo.json').read_text(encoding='utf-8'))
STATE_FILE=BASE/'datos_locales.json'
RESET='\033[0m'; BOLD='\033[1m'; CYAN='\033[96m'; GREEN='\033[92m'; YELLOW='\033[93m'; RED='\033[91m'; MAGENTA='\033[95m'; WHITE='\033[97m'; BLUE='\033[94m'

def color(t,c): return f'{c}{t}{RESET}'
def money(n): return '$'+f'{int(round(float(n or 0))):,}'.replace(',','.')+' COP'
def pause(): input('\nPresiona ENTER para continuar...')
def clear(): os.system('cls' if os.name=='nt' else 'clear')
def box(title, lines=None, width=74, accent=CYAN):
    lines=lines or []; width=max(width, max([len(str(x)) for x in lines]+[len(title)])+4)
    print(color('╔'+'═'*(width-2)+'╗',accent)); print(color('║',accent)+color(' '+title.center(width-4)+' ',BOLD+WHITE)+color('║',accent))
    print(color('╠'+'═'*(width-2)+'╣',accent))
    for line in lines:
        line=str(line)
        while len(line)>width-4:
            print(color('║ ',accent)+line[:width-4]+color(' ║',accent)); line=line[width-4:]
        print(color('║ ',accent)+line.ljust(width-4)+color(' ║',accent))
    print(color('╚'+'═'*(width-2)+'╝',accent))
def header(title, subtitle=''):
    clear(); box('TURISMO INTERNACIONAL · PYTHON', [title, subtitle] if subtitle else [title], 74, CYAN)
def ask_int(prompt, low, high):
    while True:
        try:
            n=int(input(prompt).strip())
            if low<=n<=high:return n
        except (ValueError,EOFError): pass
        print(color(f'Ingresa un número entre {low} y {high}.',RED))
def ask_qty(prompt='Cantidad de viajeros: '): return ask_int(prompt,1,100)
def initial_accounts():
    """Devuelve saldos iniciales desde el catálogo, evitando valores duplicados."""
    return {'cash':int(DATA.get('demoCash',{}).get('balance',5000000)),
            'card':int(DATA['demoCard']['limit']),
            'card2':int(DATA['demoCard2']['limit']),
            'debit':int(DATA['demoDebitCard']['balance'])}

def load_state():
    try:s=json.loads(STATE_FILE.read_text(encoding='utf-8'))
    except (OSError,ValueError):s={}
    # Conserva datos que pudieran existir en la primera versión de terminal.
    s.setdefault('customer',{'first':'','last':'','id':''}); s.setdefault('history',[])
    s.setdefault('accounts',{})
    defaults=initial_accounts()
    for k,v in defaults.items():s['accounts'].setdefault(k,v)
    s.setdefault('national_routes',s.pop('routes',[])); s.setdefault('national_services',[])
    s.setdefault('international_routes',[]); s.setdefault('international_services',[])
    s.setdefault('national_paid',False); s.setdefault('international_paid',False)
    s.setdefault('national_payment',None); s.setdefault('international_payment',None)
    # Los registros viejos de servicios se mantienen en el presupuesto nacional.
    if not s['national_services'] and s.get('services'):
        s['national_services']=s.pop('services')
    return s
def save():
    # Escritura atómica para evitar perder facturas si la terminal se cierra durante el guardado.
    tmp=STATE_FILE.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(S,ensure_ascii=False,indent=2),encoding='utf-8')
    tmp.replace(STATE_FILE)
S=load_state()

def latest_national(): return S['national_routes'][-1]['to'] if S['national_routes'] else 'Bucaramanga'
def latest_international(): return S['international_routes'][-1]['to'] if S['international_routes'] else ''
def latest_destination(): return latest_international() or (S['national_routes'][-1]['to'] if S['national_routes'] else 'Bucaramanga')
def country_for(city):
    for x in DATA['routeLegs']:
        if x.get('to')==city:return x.get('toCountry','Colombia')
        if x.get('from')==city:return x.get('fromCountry','Colombia')
    countries={
      'Cancún':'México','Ciudad de México':'México','Guadalajara':'México','Oaxaca':'México',
      'Miami':'Estados Unidos','Orlando':'Estados Unidos','Nueva York':'Estados Unidos','Los Ángeles':'Estados Unidos',
      'Toronto':'Canadá','Vancouver':'Canadá','Madrid':'España','Barcelona':'España','Sevilla':'España',
      'París':'Francia','Niza':'Francia','Roma':'Italia','Venecia':'Italia','Lisboa':'Portugal','Londres':'Reino Unido',
      'Ámsterdam':'Países Bajos','Berlín':'Alemania','Zúrich':'Suiza','Lima':'Perú','Cusco':'Perú',
      'Buenos Aires':'Argentina','Mendoza':'Argentina','Santiago':'Chile','Valparaíso':'Chile','Panamá':'Panamá',
      'Punta Cana':'República Dominicana','Santo Domingo':'República Dominicana','São Paulo':'Brasil','Río de Janeiro':'Brasil',
      'San José':'Costa Rica','Quito':'Ecuador','Montevideo':'Uruguay','La Paz':'Bolivia','Tokio':'Japón','Osaka':'Japón',
      'Seúl':'Corea del Sur','Busan':'Corea del Sur','Bangkok':'Tailandia','Chiang Mai':'Tailandia','Estambul':'Turquía','Capadocia':'Turquía','Sídney':'Australia','Melbourne':'Australia',
      'Monterrey':'México','Mérida':'México','Puebla':'México','Chicago':'Estados Unidos','San Francisco':'Estados Unidos','Boston':'Estados Unidos','Montreal':'Canadá','Valencia':'España','Málaga':'España','Lyon':'Francia','Florencia':'Italia','Milán':'Italia','Oporto':'Portugal','Edimburgo':'Reino Unido','Róterdam':'Países Bajos','Múnich':'Alemania','Ginebra':'Suiza','Arequipa':'Perú','Córdoba':'Argentina','Puerto Montt':'Chile','Kioto':'Japón','Sapporo':'Japón'}
    return countries.get(city,'Colombia')
def parse_pair(name):
    m=re.match(r'^(.+?) → (.+?)(?: \(|,|$)',name)
    return (m.group(1).strip(),m.group(2).strip()) if m else ('','')
def total_rows(rows): return sum(int(x.get('total',x.get('price',0))) for x in rows)
def national_total():return total_rows(S['national_routes'])+total_rows(S['national_services'])
def international_total():return total_rows(S['international_routes'])+total_rows(S['international_services'])
def print_table(title, rows):
    box(title, [f'{i:02}. {r.get("name",r.get("to","Servicio"))[:43]} | {r.get("qty",1)} x | {money(r.get("total",r.get("price",0)))}' for i,r in enumerate(rows,1)] or ['Aún no hay elementos agregados.'],74,BLUE)
def cards_panel():
    a=S['accounts']; c=DATA['demoCard']; c2=DATA['demoCard2']; d=DATA['demoDebitCard']
    lines=[f'Titular de demostración: {S["customer"].get("first") or "Edwin"} {S["customer"].get("last") or "Ocampo"}',
      f'CRÉDITO TI · usuario: {c["username"]} · cupo disponible: {money(a["card"])}',
      f'CRÉDITO PLUS TI · usuario: {c2["username"]} · cupo disponible: {money(a["card2"])}',
      f'DÉBITO TI · usuario: {d["username"]} · saldo disponible: {money(a["debit"])}',
      f'CAJA / EFECTIVO · saldo disponible: {money(a["cash"])}',
      'Credencial de demostración para tarjetas: usuario y clave configurados en catalogo.json.',
      'Simulación local: no conecta con bancos ni procesa dinero real.']
    box('01 · INFORMACIÓN DE TARJETAS Y MEDIOS DE PAGO',lines,82,MAGENTA)
    if input('¿Deseas registrar o actualizar los datos del viajero ahora? (s/n): ').strip().lower()=='s':
        customer()
    else:
        pause()

def customer():
    header('DATOS DEL VIAJERO','Se conservan localmente para las facturas.')
    c=S['customer']
    c['first']=input(f'Nombre [{c.get("first","")}]: ').strip() or c.get('first','')
    c['last']=input(f'Apellido [{c.get("last","")}]: ').strip() or c.get('last','')
    c['id']=input(f'Últimos 4 dígitos de identificación [{c.get("id","")}]: ').strip() or c.get('id','')
    save(); print(color('Datos guardados.',GREEN)); pause()

def add_route(national=True):
    key='national_routes' if national else 'international_routes'
    if national and S['national_paid']:
        print(color('El pago nacional ya fue confirmado. Inicia una nueva cotización para modificar esa etapa.',YELLOW));pause();return
    if not national and not S['national_paid']:
        print(color('Primero completa y paga la etapa nacional.',YELLOW));pause();return
    if not national and S['international_paid']:
        print(color('El pago internacional ya fue confirmado. Inicia una nueva cotización para modificar esa etapa.',YELLOW));pause();return
    origin=(S['national_routes'][-1]['to'] if national and S['national_routes'] else 'Bucaramanga') if national else (S['international_routes'][-1]['to'] if S['international_routes'] else latest_national())
    header('02 · RUTAS NACIONALES' if national else '05 · VUELOS INTERNACIONALES',f'Origen automático: {origin} · no editable')
    if national:
        print('┌──────────────────────────────┐\n│ TRANSPORTE NACIONAL          │\n└──────────────────────────────┘\n1. Avión\n2. Bus\n0. Volver')
        t=ask_int('Transporte: ',0,2)
        if t==0:return
        catalog=DATA['localFlights'] if t==1 else DATA['nationalBuses']; options=[]
        for item in catalog:
            a,b=parse_pair(item['name'])
            if a==origin and b and not (t==2 and (origin=='San Andrés' or b=='San Andrés')): options.append((item,b))
        typ='Avión nacional' if t==1 else 'Bus nacional'
    else:
        options=[]
        for item in DATA['routeLegs']:
            if item.get('from')==origin and item.get('mode')!='return':
                # Desde Colombia solo se muestran salidas internacionales; ya en el extranjero
                # se permiten conexiones a otros destinos internacionales, incluso del mismo país.
                if country_for(origin)=='Colombia' and item.get('toCountry')=='Colombia':
                    continue
                options.append(({'id':item['id'],'name':f"{item['from']} → {item['to']}, {item.get('toCountry','')}",'price':item['price']},item['to']))
        # Si la ciudad colombiana no tiene tarifa directa específica en routeLegs, se conservan
        # los destinos/precios internacionales del catálogo web y se traza el origen real del viajero.
        if not options and country_for(origin)=='Colombia':
            for item in DATA['packageOptions'].get('flight',[]):
                a,b=parse_pair(item['name'])
                if b:
                    dest=b.split(',')[0].strip()
                    if not any(existing_dest==dest for _,existing_dest in options):
                        options.append(({'id':item['id'],'name':f'{origin} → {dest}','price':item['price']},dest))
        typ='Vuelo internacional'
    if not national:
        # Catálogo ampliado: siempre se combina con las rutas directas del catálogo original.
        # Tarifas orientativas por tramo, en COP.
        extra=[
          ('Cancún','México',1250000),('Ciudad de México','México',1450000),('Guadalajara','México',1580000),('Oaxaca','México',1690000),('Monterrey','México',1620000),('Mérida','México',1510000),('Puebla','México',1490000),
          ('Miami','Estados Unidos',1880000),('Orlando','Estados Unidos',2050000),('Nueva York','Estados Unidos',2450000),('Los Ángeles','Estados Unidos',2800000),('Chicago','Estados Unidos',2550000),('San Francisco','Estados Unidos',2950000),('Boston','Estados Unidos',2650000),
          ('Toronto','Canadá',2900000),('Vancouver','Canadá',3350000),('Montreal','Canadá',3050000),('Madrid','España',3200000),('Barcelona','España',3350000),('Sevilla','España',3450000),('Valencia','España',3290000),('Málaga','España',3390000),
          ('París','Francia',3650000),('Niza','Francia',3800000),('Lyon','Francia',3720000),('Roma','Italia',3400000),('Venecia','Italia',3500000),('Florencia','Italia',3450000),('Milán','Italia',3380000),('Lisboa','Portugal',3150000),('Oporto','Portugal',3190000),
          ('Londres','Reino Unido',3900000),('Edimburgo','Reino Unido',4050000),('Ámsterdam','Países Bajos',3700000),('Róterdam','Países Bajos',3790000),('Berlín','Alemania',3850000),('Múnich','Alemania',3970000),('Zúrich','Suiza',4100000),('Ginebra','Suiza',4150000),
          ('Lima','Perú',980000),('Cusco','Perú',1150000),('Arequipa','Perú',1080000),('Buenos Aires','Argentina',1750000),('Mendoza','Argentina',1850000),('Córdoba','Argentina',1690000),('Santiago','Chile',1450000),('Valparaíso','Chile',1550000),('Puerto Montt','Chile',1620000),
          ('Panamá','Panamá',780000),('Punta Cana','República Dominicana',1650000),('Santo Domingo','República Dominicana',1580000),('São Paulo','Brasil',1550000),('Río de Janeiro','Brasil',1650000),
          ('San José','Costa Rica',1100000),('Quito','Ecuador',850000),('Montevideo','Uruguay',1900000),('La Paz','Bolivia',1250000),
          ('Tokio','Japón',5200000),('Osaka','Japón',5350000),('Kioto','Japón',5300000),('Sapporo','Japón',5450000),('Seúl','Corea del Sur',5100000),('Busan','Corea del Sur',5150000),('Bangkok','Tailandia',5600000),('Chiang Mai','Tailandia',5700000),('Estambul','Turquía',4300000),('Capadocia','Turquía',4450000),('Sídney','Australia',6100000),('Melbourne','Australia',6250000)
        ]
        present={d.casefold() for _,d in options}
        for dest,country,price in extra:
            if dest.casefold()!=origin.casefold() and dest.casefold() not in present:
                options.append(({'id':'extra-'+re.sub(r'[^a-z]','',dest.lower()),'name':f'{origin} → {dest}, {country}','price':price},dest))
                present.add(dest.casefold())
    if not options:
        print(color('No hay rutas directas en el catálogo desde esta llegada.',YELLOW));pause();return
    if not national:
        # Primero se elige el país; luego se muestran únicamente sus ciudades.
        country_options=[]
        for item,dest in options:
            country=(item.get('name','').rsplit(',',1)[-1].strip() if ',' in item.get('name','') else country_for(dest))
            if country and country not in country_options and dest.casefold()!=origin.casefold():
                country_options.append(country)
        country_options=sorted(country_options, key=str.casefold)
        print('\n┌─ PAÍSES DISPONIBLES ─────────────────────────────────────────┐')
        for i,country in enumerate(country_options,1): print(f'│ {i:>2}. {country[:45]:45} │')
        print('│  0. Volver'.ljust(62)+'│\n└'+'─'*60+'┘')
        ci=ask_int('Selecciona país: ',0,len(country_options))
        if ci==0:return
        chosen_country=country_options[ci-1]
        options=[(item,dest) for item,dest in options if (item.get('name','').rsplit(',',1)[-1].strip() if ',' in item.get('name','') else country_for(dest))==chosen_country]
        if not options:
            print(color('No hay ciudades disponibles para ese país.',YELLOW));pause();return
        print(color(f'PAÍS: {chosen_country} · Puedes volver a esta opción para elegir otro país.',CYAN))
    print('\n┌─ DESTINOS DISPONIBLES '+('NACIONALES' if national else 'CIUDADES DEL PAÍS SELECCIONADO')+' ─────────────────────────────┐')
    for i,(item,dest) in enumerate(options,1): print(f'│ {i:>2}. {dest[:35]:35} {money(item["price"]):>22} │')
    print('│  0. Volver'.ljust(74)+'│\n└'+'─'*72+'┘')
    n=ask_int('Selecciona destino: ',0,len(options))
    if n==0:return
    qty=ask_qty(); item,dest=options[n-1]; price=int(item['price'])*qty
    S[key].append({'from':origin,'to':dest,'name':f'{origin} → {dest}','type':'Nacional' if national else 'Internacional','transport':typ,'qty':qty,'price':int(item['price']),'total':price,'date':datetime.now().isoformat(timespec='minutes')})
    save();
    if national:
        route_label=f'{origin} (Colombia) → {dest} (Colombia)'
    else:
        route_label=f'{origin} ({country_for(origin)}) → {dest} ({country_for(dest)})'
    print(color(f'Tramo agregado: {route_label} · {qty} viajero(s) · {money(price)}',GREEN));pause()

# Servicios con precios orientativos y recomendaciones nombradas según el destino.
EXPERIENCES={
'Bogotá':{'lodging':[('Hotel cerca de La Candelaria · noche',285000)],'food':[('Ajiaco santafereño',42000),('Ruta de café de especialidad',65000)],'activity':[('Tour Monserrate y centro histórico',115000),('Museo del Oro y recorrido cultural',70000)]},
'Medellín':{'lodging':[('Hotel en El Poblado · noche',335000)],'food':[('Bandeja paisa tradicional',48000),('Tour de cafés antioqueños',85000)],'activity':[('Tour Comuna 13 y arte urbano',95000),('Guatapé y Piedra del Peñol',235000)]},
'Cartagena':{'lodging':[('Hotel boutique en ciudad amurallada · noche',420000)],'food':[('Cazuela de mariscos caribeña',85000),('Cena frente al mar',185000)],'activity':[('Paseo en lancha por islas del Rosario',260000),('Recorrido por ciudad amurallada',95000)]},
'San Andrés':{'lodging':[('Posada isleña · noche',295000)],'food':[('Pescado isleño con coco',62000)],'activity':[('Vuelta a la isla y miradores',95000),('Johnny Cay y acuario',185000)]},
'Bucaramanga':{'lodging':[('Hotel en Cabecera · noche',230000)],'food':[('Cabrito santandereano con pepitoria',52000)],'activity':[('Parque nacional del Chicamocha',195000),('Ruta de pueblos de Santander',165000)]},
'Santa Marta':{'lodging':[('Eco-lodge cerca del Tayrona · noche',310000)],'food':[('Pescado caribeño con patacón',58000)],'activity':[('Excursión al parque Tayrona',185000),('Snorkel en Taganga',150000)]},
'Cali':{'lodging':[('Hotel en zona gastronómica · noche',245000)],'food':[('Experiencia de cocina valluna',55000)],'activity':[('Clase de salsa caleña',85000),('Miradores y barrio San Antonio',70000)]},
'Ciudad de México':{'lodging':[('Hotel boutique en Roma-Condesa · noche',590000)],'food':[('Ruta de tacos tradicionales',95000)],'activity':[('Tour de Teotihuacán',290000),('Recorrido por el Zócalo',110000)]},
'Cancún':{'lodging':[('Resort en zona hotelera · noche',1150000)],'food':[('Experiencia de cocina yucateca',145000)],'activity':[('Excursión a Chichén Itzá',390000),('Snorkel en arrecife',280000)]},
'Miami':{'lodging':[('Hotel en Miami Beach · noche',1050000)],'food':[('Experiencia gastronómica local',145000)],'activity':[('Tour urbano y playas',230000),('Excursión de día completo',350000)]},
'Madrid':{'lodging':[('Hotel céntrico · noche',650000)],'food':[('Ruta de tapas españolas',125000)],'activity':[('Tour por el centro histórico',185000),('Museos y paseo cultural',210000)]},
'Lima':{'lodging':[('Hotel en Miraflores · noche',420000)],'food':[('Experiencia de cocina peruana',115000)],'activity':[('Centro histórico de Lima',125000),('Tour gastronómico',190000)]},
'Orlando':{'lodging':[('Hotel cerca de parques · noche',780000),('Hotel familiar con transporte · noche',650000)],'food':[('Experiencia gastronómica familiar',150000),('Ruta de restaurantes internacionales',125000)],'activity':[('Parque temático · entrada',550000),('Tour de la ciudad',180000),('Centro espacial Kennedy · excursión',420000)]},
'Madrid':{'lodging':[('Hotel céntrico · noche',650000),('Hostal boutique en zona histórica · noche',390000),('Apartamento turístico · noche',520000)],'food':[('Ruta de tapas españolas',125000),('Mercado de San Miguel y degustación',110000),('Churros con chocolate',35000)],'activity':[('Tour por el centro histórico',185000),('Museos y paseo cultural',210000),('Excursión a Toledo',260000),('Parque del Retiro y paseo guiado',80000)]},
'Barcelona':{'lodging':[('Hotel cerca de Eixample · noche',690000),('Hostal céntrico · noche',410000)],'food':[('Tapas catalanas',120000),('Ruta de mercados y bocados locales',95000)],'activity':[('Sagrada Familia y modernismo',230000),('Paseo por el Barrio Gótico',95000),('Montjuïc y miradores',110000)]},
'París':{'lodging':[('Hotel céntrico · noche',850000),('Hotel boutique · noche',1050000)],'food':[('Bistró francés tradicional',145000),('Panadería y degustación local',55000)],'activity':[('Recorrido por Montmartre',140000),('Crucero por el Sena',185000),('Museo del Louvre · visita',230000)]},
'Roma':{'lodging':[('Hotel cerca del centro histórico · noche',760000),('Pensión familiar · noche',440000)],'food':[('Pasta romana tradicional',110000),('Ruta de helados artesanales',45000)],'activity':[('Coliseo y Foro Romano',250000),('Ruta de plazas y fuentes',105000),('Ciudad del Vaticano · recorrido',230000)]},
'Lima':{'lodging':[('Hotel en Miraflores · noche',420000),('Hotel con vista al Pacífico · noche',570000)],'food':[('Experiencia de cocina peruana',115000),('Cevichería tradicional',85000),('Ruta de postres limeños',50000)],'activity':[('Centro histórico de Lima',125000),('Tour gastronómico',190000),('Circuito Mágico del Agua',70000)]},
'Buenos Aires':{'lodging':[('Hotel en Palermo · noche',510000),('Hotel céntrico · noche',390000)],'food':[('Parrilla argentina tradicional',135000),('Café histórico y pastelería',50000)],'activity':[('Tango y cena',280000),('Recorrido por San Telmo y La Boca',125000),('Tour de arquitectura porteña',95000)]},
'Tokio':{'lodging':[('Hotel compacto cerca del metro · noche',620000),('Ryokan tradicional · noche',950000)],'food':[('Ruta de ramen',95000),('Experiencia de sushi',180000),('Mercado y comida callejera',75000)],'activity':[('Asakusa y templo Sensō-ji',110000),('Cruce de Shibuya y miradores',125000),('Excursión a Kamakura',280000)]}}
# Ampliación de recomendaciones por ciudad. Precios orientativos por persona o noche en COP.
EXPERIENCES.update({
 'Guadalajara':{'lodging':[('Hotel en zona Centro · noche',320000),('Hotel boutique en Americana · noche',470000),('Apartamento turístico · noche',350000)],'food':[('Birria tradicional tapatía',55000),('Torta ahogada y bebida',38000),('Ruta de tequila y gastronomía',165000)],'activity':[('Centro histórico y catedral',75000),('Tlaquepaque y talleres artesanales',125000),('Excursión a Tequila',260000)]},
 'Oaxaca':{'lodging':[('Posada en centro histórico · noche',280000),('Hotel boutique · noche',460000),('Hotel con desayuno · noche',350000)],'food':[('Tlayudas oaxaqueñas',42000),('Degustación de moles',85000),('Mercado y chocolate artesanal',65000)],'activity':[('Monte Albán con guía',185000),('Ruta de mezcal',175000),('Taller de alebrijes',95000)]},
 'Monterrey':{'lodging':[('Hotel zona centro · noche',390000),('Hotel ejecutivo · noche',520000)],'food':[('Cabrito al horno',78000),('Cortes norteños',145000),('Desayuno regional',38000)],'activity':[('Paseo Santa Lucía y Fundidora',95000),('Excursión a la Cola de Caballo',190000),('Mirador del Obispado',55000)]},
 'Mérida':{'lodging':[('Hotel centro histórico · noche',310000),('Hacienda boutique · noche',620000)],'food':[('Cochinita pibil',45000),('Sopa de lima yucateca',38000),('Ruta de marquesitas yucatecas',35000)],'activity':[('Uxmal con guía',240000),('Cenotes de la región',195000),('Paseo guiado por Paseo de Montejo',70000)]},
 'Valencia':{'lodging':[('Hotel céntrico · noche',520000),('Hostal moderno · noche',330000)],'food':[('Paella valenciana',125000),('Horchata y fartons',42000),('Ruta de tapas locales',115000)],'activity':[('Ciudad de las Artes y las Ciencias',195000),('Casco antiguo y mercado central',85000),('Paseo por la Albufera',155000)]},
 'Málaga':{'lodging':[('Hotel cerca del centro · noche',510000),('Hostal junto a la playa · noche',340000)],'food':[('Espetos de sardinas',85000),('Tapas andaluzas',105000),('Desayuno con mollete',35000)],'activity':[('Alcazaba y teatro romano',105000),('Excursión a Caminito del Rey',240000),('Museo Picasso',95000)]},
 'Florencia':{'lodging':[('Hotel céntrico · noche',690000),('Pensión familiar · noche',460000)],'food':[('Bistecca alla fiorentina',190000),('Pasta toscana',105000),('Gelato artesanal',35000)],'activity':[('Galería Uffizi',195000),('Cúpula del Duomo',145000),('Excursión por la Toscana',290000)]},
 'Milán':{'lodging':[('Hotel cerca de Centrale · noche',720000),('Hotel boutique · noche',890000)],'food':[('Risotto alla milanese',115000),('Aperitivo milanés',95000),('Panzerotto tradicional',38000)],'activity':[('Duomo y terrazas',190000),('Última Cena con reserva',240000),('Tour de diseño y moda',160000)]},
 'Oporto':{'lodging':[('Hotel centro histórico · noche',430000),('Casa de huéspedes · noche',310000)],'food':[('Francesinha tradicional',65000),('Bacalao portugués',95000),('Pastel de nata y café',28000)],'activity':[('Ribeira y puente Dom Luís I',75000),('Bodega de vino de Oporto',145000),('Crucero de los seis puentes',95000)]},
 'Edimburgo':{'lodging':[('Hotel céntrico · noche',760000),('Hostal privado · noche',420000)],'food':[('Haggis tradicional',95000),('Desayuno escocés',65000),('Pub gastronómico',125000)],'activity':[('Castillo de Edimburgo',165000),('Tour histórico a pie',95000),('Excursión a Highlands',390000)]},
 'Montreal':{'lodging':[('Hotel centro · noche',610000),('Alojamiento boutique · noche',750000)],'food':[('Poutine tradicional',55000),('Bagel de Montreal',28000),('Ruta gastronómica del Viejo Montreal',155000)],'activity':[('Viejo Montreal y puerto',95000),('Mont Royal y miradores',65000),('Museo de Bellas Artes',110000)]},
 'Chicago':{'lodging':[('Hotel Loop · noche',850000),('Hotel cerca del río · noche',1050000)],'food':[('Pizza deep-dish',85000),('Hot dog estilo Chicago',45000),('Tour gastronómico local',190000)],'activity':[('Crucero de arquitectura por el río',210000),('Mirador 360 Chicago',175000),('Millennium Park y museo',145000)]},
 'San Francisco':{'lodging':[('Hotel céntrico · noche',1050000),('Hotel boutique · noche',1280000)],'food':[('Clam chowder en pan',85000),('Dim sum en Chinatown',95000),('Mercado Ferry Building',125000)],'activity':[('Alcatraz con ferry',260000),('Puente Golden Gate y miradores',125000),('Tranvías y barrios históricos',145000)]},
 'Kioto':{'lodging':[('Hotel cerca de estación · noche',650000),('Ryokan tradicional · noche',1050000)],'food':[('Kaiseki tradicional',220000),('Ramen de Kioto',85000),('Mercado Nishiki y degustación',110000)],'activity':[('Fushimi Inari y templos',115000),('Arashiyama y bosque de bambú',145000),('Ceremonia de té',175000)]},
 'Melbourne':{'lodging':[('Hotel centro · noche',890000),('Apartamento turístico · noche',760000)],'food':[('Brunch y café de especialidad',75000),('Cena multicultural',145000),('Mercados Queen Victoria',85000)],'activity':[('Great Ocean Road · excursión',390000),('Tour de arte urbano',95000),('Jardín Botánico y paseo guiado',75000)]},
 'Cusco':{'lodging':[('Hostal cerca de Plaza de Armas · noche',280000),('Hotel boutique · noche',490000)],'food':[('Cuy o cocina andina',85000),('Lomo saltado',65000),('Degustación de maíz y cacao',75000)],'activity':[('Valle Sagrado con guía',260000),('City tour y sitios arqueológicos',145000),('Montaña de colores · excursión',320000)]},
 'Buenos Aires':{'lodging':[('Hotel en Palermo · noche',510000),('Hotel céntrico · noche',390000),('Apartamento turístico · noche',430000)],'food':[('Parrilla argentina tradicional',135000),('Empanadas y vino sin alcohol',55000),('Café histórico y pastelería',50000)],'activity':[('Tango y cena',280000),('San Telmo y La Boca',125000),('Tour de arquitectura porteña',95000)]}
})

FACTORS={'Colombia':1,'México':1.12,'Estados Unidos':2.35,'Canadá':2.15,'España':1.8,'Francia':2.05,'Reino Unido':2.25,'Portugal':1.55,'Italia':1.85,'Alemania':1.95,'Países Bajos':2.05,'Perú':1.02,'Brasil':1.18,'Argentina':1.25,'Chile':1.45,'Panamá':1.45,'Costa Rica':1.55,'Ecuador':1,'República Dominicana':1.4,'Uruguay':1.6,'Bolivia':.85,'Japón':2,'Corea del Sur':1.85,'Tailandia':.95,'Turquía':1.25}
def services(national=True):
    key='national_services' if national else 'international_services'
    if national and S['national_paid']: print(color('La etapa nacional ya está pagada.',YELLOW));pause();return
    if not national and not S['national_paid']: print(color('Paga primero la etapa nacional.',YELLOW));pause();return
    if not national and S['international_paid']: print(color('La etapa internacional ya está pagada.',YELLOW));pause();return
    city=(S['national_routes'][-1]['to'] if national and S['national_routes'] else 'Bucaramanga') if national else (S['international_routes'][-1]['to'] if S['international_routes'] else latest_national())
    country=country_for(city); factor=FACTORS.get(country,1.25); header(('03 · EXPERIENCIAS EN COLOMBIA' if national else '06 · EXPERIENCIAS INTERNACIONALES'),f'Destino actual: {city} · {country}')
    print('┌────────────────────────────────────────────────────────────┐\n│ RECONOCE EL DESTINO                                        │\n└────────────────────────────────────────────────────────────┘')
    print('1. Comida y gastronomía\n2. Hospedaje\n3. Actividades y sitios de interés\n0. Volver')
    cat=ask_int('Categoría: ',0,3)
    if cat==0:return
    catkey={1:'food',2:'lodging',3:'activity'}[cat]; generic={'food':[('Restaurante de cocina típica local',65000),('Mercado gastronómico y degustación',55000),('Desayuno tradicional',22000),('Cena en restaurante recomendado',95000),('Café y postre típico',30000),('Tour de comida callejera',78000)],'lodging':[('Hotel céntrico de categoría media · noche',240000),('Hotel económico · noche',145000),('Alojamiento con desayuno · noche',290000),('Hotel boutique · noche',360000),('Apartamento turístico · noche',270000),('Hostal céntrico · noche',110000)],'activity':[('Recorrido guiado por lugares emblemáticos',85000),('Museo o experiencia cultural',45000),('Excursión local de medio día',125000),('Tour panorámico de la ciudad',95000),('Experiencia artesanal o taller local',70000),('Excursión de día completo',220000),('Miradores y fotografía',60000)]}
    choices=EXPERIENCES.get(city,{}).get(catkey,generic[catkey])
    if not national: choices=[(name,round(price*factor/1000)*1000) for name,price in choices]
    print('\n┌─ OPCIONES PARA '+city.upper()+' '+'─'*max(1,38-len(city))+'┐')
    for i,(name,price) in enumerate(choices,1):print(f'│ {i:>2}. {name[:43]:43} │\n│     {money(price):>43} │')
    print('│  0. Volver'.ljust(54)+'│\n└'+'─'*52+'┘')
    n=ask_int('Selecciona opción: ',0,len(choices))
    if n==0:return
    name,price=choices[n-1]; qty=ask_qty('Cantidad de personas/noches: ')
    S[key].append({'city':city,'country':country,'category':catkey,'name':name,'qty':qty,'price':int(price),'total':int(price)*qty})
    save(); category_label={'food':'Comida y gastronomía','lodging':'Hospedaje','activity':'Actividad y sitio de interés'}[catkey]; print(color(f'Servicio agregado · {category_label} · {city} ({country}) · {qty} × {name} · {money(price*qty)}',GREEN));pause()

def summary(national=True):
    routes=S['national_routes'] if national else S['international_routes']; svcs=S['national_services'] if national else S['international_services']; title='PRESUPUESTO NACIONAL' if national else 'PRESUPUESTO INTERNACIONAL'
    header(title)
    box('A · RUTAS Y VUELOS',[f'{i}. {r["from"]} ({country_for(r.get("from", ""))}) → {r["to"]} ({country_for(r.get("to", ""))}) · {r["transport"]} · {r["qty"]} viajero(s) · {money(r["total"])}' for i,r in enumerate(routes,1)] or ['Sin rutas agregadas.'],82,BLUE)
    box('B · EXPERIENCIAS Y SERVICIOS',[f'{i}. {x["city"]} ({x.get("country") or country_for(x.get("city", ""))}) · { {"food":"COMIDA/GASTRONOMÍA","lodging":"HOSPEDAJE","activity":"ACTIVIDAD"}.get(x.get("category"),"SERVICIO")} · {x["name"]} · cantidad {x["qty"]} · {money(x["total"])}' for i,x in enumerate(svcs,1)] or ['Sin servicios agregados.'],82,MAGENTA)
    box('C · TOTAL DE LA ETAPA',[f'Rutas: {money(total_rows(routes))}',f'Servicios: {money(total_rows(svcs))}',f'TOTAL: {money(total_rows(routes)+total_rows(svcs))}',f'Estado del pago: {"CONFIRMADO" if S["national_paid" if national else "international_paid"] else "PENDIENTE"}'],74,GREEN)
    pause()

def pay_stage(national=True):
    paidkey='national_paid' if national else 'international_paid'; paykey='national_payment' if national else 'international_payment'
    if not national and not S['national_paid']: print(color('Debes confirmar el pago nacional antes de pagar la etapa internacional.',YELLOW));pause();return
    if S[paidkey]: print(color('Esta etapa ya fue pagada. No se realizará un segundo cobro.',YELLOW));pause();return
    rows=(S['national_routes']+S['national_services']) if national else (S['international_routes']+S['international_services'])
    total=total_rows(rows)
    if total<=0: print(color('Agrega rutas, vuelos o servicios antes de pagar esta etapa.',YELLOW));pause();return
    c=S['customer']
    if not c.get('first') or not c.get('last'):
        print(color('Primero completa los datos del viajero.',YELLOW));pause();return
    header('04 · PAGO NACIONAL' if national else '07 · PAGO INTERNACIONAL','Selecciona un medio de pago para esta etapa')
    a=S['accounts']; demo1=DATA['demoCard']; demo2=DATA['demoCard2']
    box('RESUMEN DEL COBRO',[f'Viajero: {c["first"]} {c["last"]}',f'Subtotal: {money(total)}','',f'CRÉDITO TI · cupo disponible: {money(a["card"])}',f'CRÉDITO PLUS TI · cupo disponible: {money(a["card2"])}',f'DÉBITO TI · saldo disponible: {money(a["debit"])}',f'EFECTIVO · saldo disponible: {money(a["cash"])}','Los saldos se actualizan después de confirmar el pago.'],82,BLUE)
    print('\n┌──────────────────── MEDIOS DE PAGO ────────────────────┐\n│ 1. Efectivo                                              │\n│ 2. Tarjeta de crédito (2 % de interés)                   │\n│ 3. Tarjeta Crédito Plus (1,3 % de interés)               │\n│ 4. Tarjeta débito (sin interés)                          │\n│ 0. Cancelar                                              │\n└─────────────────────────────────────────────────────────┘')
    method=ask_int('Método: ',0,4)
    if method==0:return
    accounts=S['accounts']; interest=0; change=0; installments=1; received=0
    if method==1:
        try: received=int(input('Efectivo recibido en COP (puedes escribir puntos): ').replace('.','').replace(',','').strip())
        except ValueError: print(color('Monto no válido.',RED));pause();return
        if received<total: print(color('El efectivo recibido no cubre el total.',RED));pause();return
        if accounts['cash']<total: print(color('Saldo de caja insuficiente.',RED));pause();return
        accounts['cash']-=total;change=received-total;methodname='Efectivo';charged=total
    else:
        cardkey={2:'card',3:'card2',4:'debit'}[method]; demo={2:DATA['demoCard'],3:DATA['demoCard2'],4:DATA['demoDebitCard']}[method]
        user=input('Usuario de tarjeta: ').strip(); password=input('Contraseña de tarjeta: ')
        if user!=demo['username'] or password!=demo['password']:
            print(color('Credenciales incorrectas. No se efectuó el cobro.',RED));pause();return
        if method in (2,3):
            installments=ask_int(f'Número de cuotas (1–{12 if method==2 else 24}): ',1,12 if method==2 else 24)
            rate=.02 if method==2 else .013; interest=round(total*rate);charged=total+interest
            if accounts[cardkey]<charged: print(color(f'Cupo insuficiente. Disponible: {money(accounts[cardkey])}',RED));pause();return
            accounts[cardkey]-=charged;methodname='Crédito' if method==2 else 'Crédito Plus'
        else:
            charged=total
            if accounts[cardkey]<charged: print(color('Saldo de débito insuficiente.',RED));pause();return
            accounts[cardkey]-=charged;methodname='Débito'
    account_key = 'cash' if method==1 else {2:'card',3:'card2',4:'debit'}[method]
    remaining = accounts[account_key]
    monthly = round(charged/installments) if method in (2,3) else 0
    rate_label = '2 %' if method==2 else ('1,3 %' if method==3 else '0 %')
    result={'method':methodname,'base':total,'interest':interest,'total':charged,'change':change,'received':received,'installments':installments,'monthly_estimate':monthly,'remaining_balance':remaining,'interest_rate':rate_label,'account_key':account_key,'date':datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    S[paykey]=result;S[paidkey]=True;save()
    lines=[f'Etapa: {"Nacional" if national else "Internacional"}',f'Método: {methodname}',f'Subtotal: {money(total)}',f'Tasa de interés: {rate_label}',f'Intereses cobrados: {money(interest)}',f'Total cobrado: {money(charged)}']
    if method in (2,3): lines += [f'Número de cuotas: {installments}',f'Cuota aproximada: {money(monthly)} por mes']
    lines += [f'Saldo/cupo restante: {money(remaining)}',f'Cambio: {money(change)}' if method==1 else '', 'El saldo de la cuenta fue actualizado localmente.']
    box('PAGO CONFIRMADO',lines,76,GREEN)
    pause()

def invoice():
    header('08 · FACTURA FINAL','Comprobante organizado por etapas y conceptos.')
    if not S['national_paid'] or not S['international_paid']:
        box('FACTURA PENDIENTE',['Completa y paga la etapa nacional.','Completa y paga la etapa internacional.'],74,YELLOW);pause();return
    c=S['customer']; n=S['national_payment'] or {}; i=S['international_payment'] or {}
    grand=int(n.get('total',0))+int(i.get('total',0))
    box('FACTURA TURISMO INTERNACIONAL',[f'Número provisional: TI-{datetime.now().strftime("%Y%m%d%H%M%S")}',f'Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',f'Viajero: {c.get("first","")} {c.get("last","")}',f'Identificación: {c.get("id","") or "No registrada"}'],82,CYAN)
    box('01 · VIAJE NACIONAL',[f'{r.get("from")} → {r.get("to")} | {r.get("transport")} | {money(r.get("total",0))}' for r in S['national_routes']] or ['Sin rutas nacionales.'],82,BLUE)
    box('02 · SERVICIOS NACIONALES',[f'{x.get("city")} (Colombia) · { {'food':'COMIDA/GASTRONOMÍA','lodging':'HOSPEDAJE','activity':'ACTIVIDAD'}.get(x.get("category"),'SERVICIO') } · {x.get("name")} × {x.get("qty",1)} | {money(x.get("total",0))}' for x in S['national_services']] or ['Sin servicios nacionales.'],82,BLUE)
    box('03 · PAGO NACIONAL',[f'Subtotal: {money(n.get("base",0))}',f'Método: {n.get("method","—")}',f'Tasa de interés: {n.get("interest_rate","—")}',f'Intereses: {money(n.get("interest",0))}',f'Número de cuotas: {n.get("installments",1)}',f'Cuota aproximada: {money(n.get("monthly_estimate",0))}',f'Saldo/cupo restante: {money(n.get("remaining_balance",0))}',f'TOTAL PAGADO: {money(n.get("total",0))}'],82,MAGENTA)
    box('04 · VIAJE INTERNACIONAL',[f'{r.get("from")} ({country_for(r.get("from",""))}) → {r.get("to")} ({country_for(r.get("to",""))}) | {r.get("transport")} | {money(r.get("total",0))}' for r in S['international_routes']] or ['Sin vuelos internacionales.'],82,CYAN)
    box('05 · SERVICIOS INTERNACIONALES',[f'{x.get("city")} ({x.get("country")}) · { {'food':'COMIDA/GASTRONOMÍA','lodging':'HOSPEDAJE','activity':'ACTIVIDAD'}.get(x.get("category"),'SERVICIO') } · {x.get("name")} × {x.get("qty",1)} | {money(x.get("total",0))}' for x in S['international_services']] or ['Sin servicios internacionales.'],82,CYAN)
    box('06 · PAGO INTERNACIONAL',[f'Subtotal: {money(i.get("base",0))}',f'Método: {i.get("method","—")}',f'Tasa de interés: {i.get("interest_rate","—")}',f'Intereses: {money(i.get("interest",0))}',f'Número de cuotas: {i.get("installments",1)}',f'Cuota aproximada: {money(i.get("monthly_estimate",0))}',f'Saldo/cupo restante: {money(i.get("remaining_balance",0))}',f'TOTAL PAGADO: {money(i.get("total",0))}'],82,MAGENTA)
    box('TOTAL GENERAL DE LA FACTURA',[f'ETAPA NACIONAL: {money(n.get("total",0))}',f'ETAPA INTERNACIONAL: {money(i.get("total",0))}',f'TOTAL PAGADO: {money(grand)}'],82,GREEN)
    # La factura final se guarda automáticamente; no depende de responder a una pregunta.
    now=datetime.now()
    number='TI-'+now.strftime('%Y%m%d%H%M%S%f')
    inv={'number':number,'date':now.strftime('%Y-%m-%d %H:%M:%S'),'customer':dict(c),'national_routes':list(S['national_routes']),'national_services':list(S['national_services']),'international_routes':list(S['international_routes']),'international_services':list(S['international_services']),'national_payment':dict(n),'international_payment':dict(i),'total':grand}
    S['history'].append(inv)
    S['national_routes']=[];S['national_services']=[];S['international_routes']=[];S['international_services']=[]
    S['national_paid']=False;S['international_paid']=False;S['national_payment']=None;S['international_payment']=None
    save()
    print(color(f'Factura {inv["number"]} guardada automáticamente en el historial. Ya puedes iniciar un nuevo viaje.',GREEN))
    pause()

def history():
    header('09 · HISTORIAL DE FACTURAS','Comprobantes guardados en este equipo.')
    if not S['history']: print('No hay facturas guardadas todavía.')
    else:
        for idx,inv in enumerate(reversed(S['history']),1):
            box(f'FACTURA {idx} · {inv.get("number","—")}',[f'Fecha: {inv.get("date","—")}',f'Viajero: {inv.get("customer",{}).get("first","")} {inv.get("customer",{}).get("last","")}',f'Rutas: {len(inv.get("national_routes",[]))} nacionales · {len(inv.get("international_routes",[]))} internacionales',f'Servicios: {len(inv.get("national_services",[]))} nacionales · {len(inv.get("international_services",[]))} internacionales',f'Total pagado: {money(inv.get("total",0))}'],82,GREEN)
    print('\n1. Ver detalle por número\n2. Borrar historial\n0. Volver')
    n=ask_int('Opción: ',0,2)
    if n==1 and S['history']:
        num=input('Número de factura: ').strip(); inv=next((x for x in S['history'] if x.get('number')==num),None)
        if inv:
            c=inv.get('customer',{}); np=inv.get('national_payment',{}); ip=inv.get('international_payment',{})
            box('DETALLE · FACTURA '+inv.get('number','—'),[f'Fecha: {inv.get("date","—")}',f'Viajero: {c.get("first","")} {c.get("last","")}',f'Identificación: {c.get("id","") or "No registrada"}'],82,CYAN)
            for title,key in [('RUTAS NACIONALES','national_routes'),('SERVICIOS NACIONALES','national_services'),('VUELOS INTERNACIONALES','international_routes'),('EXPERIENCIAS INTERNACIONALES','international_services')]:
                box(title,[f'{x.get("from",x.get("city",""))} ({country_for(x.get("from",x.get("city","")))}) {"→ " + x.get("to","") + " (" + country_for(x.get("to","")) + ")" if x.get("to") else "· " + {'food':'COMIDA','lodging':'HOSPEDAJE','activity':'ACTIVIDAD'}.get(x.get("category"),'SERVICIO') + " · " + x.get("name","") } · {money(x.get("total",x.get("price",0)))}' for x in inv.get(key,[])] or ['Sin conceptos.'],82,BLUE)
            box('PAGOS Y TOTAL',[f'Nacional: {np.get("method","—")} · cuotas {np.get("installments",1)} · subtotal {money(np.get("base",0))} · intereses {money(np.get("interest",0))} · total {money(np.get("total",0))}',f'Internacional: {ip.get("method","—")} · cuotas {ip.get("installments",1)} · subtotal {money(ip.get("base",0))} · intereses {money(ip.get("interest",0))} · total {money(ip.get("total",0))}',f'TOTAL FACTURA: {money(inv.get("total",0))}'],82,GREEN)
        else: print(color('No se encontró esa factura.',RED))
        pause()
    elif n==2 and input('Escribe BORRAR para confirmar: ').strip()=='BORRAR': S['history']=[];save();print(color('Historial borrado. No se revierten pagos.',YELLOW));pause()

def reset_trip():
    header('NUEVA COTIZACIÓN')
    if input('¿Vaciar el viaje actual? (s/n): ').strip().lower()=='s':
        S['national_routes']=[];S['national_services']=[];S['international_routes']=[];S['international_services']=[];S['national_paid']=False;S['international_paid']=False;S['national_payment']=None;S['international_payment']=None
        # Cada nueva cotización comienza con los saldos/cupos iniciales configurados.
        S['accounts']=initial_accounts()
        save();print(color('Cotización reiniciada. Saldos restaurados a sus valores iniciales y facturas anteriores conservadas.',GREEN))
    pause()

def main():
    while True:
        header('PANEL PRINCIPAL','Cada módulo está separado en cuadros. Sigue el orden para completar el viaje.')
        last=latest_destination(); nstatus='PAGADO' if S['national_paid'] else 'PENDIENTE'; istatus='PAGADO' if S['international_paid'] else ('BLOQUEADO' if not S['national_paid'] else 'PENDIENTE')
        box('ESTADO DEL VIAJE',[f'Destino actual: {last} · {country_for(last)}',f'Etapa nacional: {nstatus} · {money(national_total())}',f'Etapa internacional: {istatus} · {money(international_total())}',f'Facturas guardadas: {len(S["history"])}'],74,GREEN)
        print('┌────────────────────── MENÚ POR ETAPAS ──────────────────────┐')
        items=[('1','Información de tarjetas + datos del viajero'),('2','Viaje nacional · vuelos y buses'),('3','Reconocimiento nacional · comida, hoteles y actividades'),('4','Resumen y pago nacional'),('5','Viaje internacional · vuelos y conexiones'),('6','Reconocimiento internacional · comida, hoteles y actividades'),('7','Resumen y pago internacional'),('8','Factura final'),('9','Historial de facturas'),('10','Nueva cotización'),('0','Guardar y salir')]
        for num,label in items: print(f'│ {num:>2}. {label:<56} │')
        print('└'+'─'*62+'┘')
        n=ask_int('Selecciona una opción: ',0,10)
        if n==0:save();print(color('Datos guardados. ¡Buen viaje!',GREEN));break
        actions={1:cards_panel,2:lambda:add_route(True),3:lambda:services(True),4:lambda:stage_summary_pay(True),5:lambda:add_route(False),6:lambda:services(False),7:lambda:stage_summary_pay(False),8:invoice,9:history,10:reset_trip}
        actions[n]()
def stage_summary_pay(national):
    summary(national)
    if S['national_paid' if national else 'international_paid']:return
    rows=(S['national_routes']+S['national_services']) if national else (S['international_routes']+S['international_services'])
    if rows and input('¿Continuar al pago de esta etapa? (s/n): ').strip().lower()=='s':pay_stage(national)
if __name__=='__main__':
    try:main()
    except (KeyboardInterrupt,EOFError):save();print('\nDatos guardados. Hasta pronto.')
