from firebase import firebase
from datetime import datetime
import time
import sys
import requests

from pirc522 import RFID
import RPi.GPIO as GPIO
import json
run = True
rdr = RFID()
util = rdr.util()
util.debug = True

def test_internet():
    url='http://www.google.com/'
    timeout=1
    try:
        _ = requests.get(url, timeout=timeout)
        print("have connection")
        return True
    except requests.ConnectionError:
        print("have not connection")
        return False

def enregistrer_historique(now,cin,fir,info):
    day=now.day
    month=now.month
    year=now.year
    h=now.hour
    m=now.minute
    date=str(day)+"/"+str(month)+"/"+str(year)+"-"+str(h)+":"+str(m)   
    if info[1]==1:
        res2= fir.post('/historique/',{'date':date,'id': cin,'nom':info[0]})
    else:
        res2= fir.post('/historique/',{'date':date,'id': cin,'nom':'inc'})     

def etat_refuse():
    GPIO.setwarnings(False)
    GPIO.setup(36,GPIO.OUT,initial=GPIO.LOW)
    for x in range(2):
        GPIO.output(36,GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(36,GPIO.LOW)
        time.sleep(0.2)

def action_mecanique():
    servoPIN = 13
    GPIO.setwarnings(False)
    GPIO.setup(servoPIN, GPIO.OUT)
    p = GPIO.PWM(servoPIN, 50)
    p.start(2)
    time.sleep(0.2)
    p.ChangeDutyCycle(7)
    time.sleep(2.3)
    p.ChangeDutyCycle(2)
    time.sleep(0.2)
    del p

def affichage_detection():
    GPIO.setwarnings(False)
    GPIO.setup(5,GPIO.OUT,initial=GPIO.LOW)
    for x in range(2):
        GPIO.output(5,GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(5,GPIO.LOW)
        time.sleep(0.1)

def affichage_error():
    GPIO.setwarnings(False)
    GPIO.setup(5,GPIO.OUT,initial=GPIO.LOW)
    GPIO.setup(29,GPIO.OUT,initial=GPIO.LOW)
    GPIO.setup(36,GPIO.OUT,initial=GPIO.LOW)
    GPIO.output(36,GPIO.HIGH)
    GPIO.output(29,GPIO.HIGH)
    time.sleep(0.7)
    GPIO.output(36,GPIO.LOW)
    GPIO.output(29,GPIO.LOW)           

def remplir_JSON_user(result):
    if result is not None:
        with open('acces.json', 'w') as user_file:
            json.dump(result, user_file)

def prendre_JSON_user():
    with open('acces.json', 'r') as user_file:
        result=json.load(user_file)
    return result

def verif_users(result,cin):
    ok=0
    nom=''
    prenom=''
    for cle,val in result.items():
        for cl,vl in val.items():
            if val['id']==cin:
                ok=1
                nom=val['nom']
                prenom=val['prenom']
    if ok==1:
        GPIO.setwarnings(False)
        GPIO.setup(29,GPIO.OUT,initial=GPIO.LOW)
        for x in range(2):
            GPIO.output(29,GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(29,GPIO.LOW)
            time.sleep(0.1)
        action_mecanique()
    else:
        etat_refuse()
    info=(nom,ok)
    return info


def verif_users_json(result,cin):
    ok=0
    for cle,val in result.items():
        if val['id']==cin:
            ok=1
    if ok==1:
        GPIO.setwarnings(False)
        GPIO.setup(29,GPIO.OUT,initial=GPIO.LOW)
        for x in range(2):
            GPIO.output(29,GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(29,GPIO.LOW)
            time.sleep(0.1)
        action_mecanique()
    else:
        etat_refuse()
    info=(ok)
    return info

def enregistrer_historique_json(now,cin):
    day=now.day
    month=now.month
    year=now.year
    h=now.hour
    m=now.minute
    date=str(day)+"/"+str(month)+"/"+str(year)+"-"+str(h)+":"+str(m)
    data_his={'date':date,'id':cin}
    with open('historique.json', 'a+') as historique_file:
        json.dump(data_his, historique_file)
    
print("Starting")
cin=''
now=datetime.now()

while run:
    rdr.wait_for_tag()
    (error, data) = rdr.request()
    if not error:
        print("\nDetected card: " )
        (error, uid) = rdr.anticoll()
        time.sleep(0.3)
        cin=str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3])
    affichage_detection()
    print(cin)
    if not error:
        if test_internet()==True:
            fir= firebase.FirebaseApplication('https://python-example-4fa7c.firebaseio.com/', None) 
            result = fir.get('utilisateurs/', '')
            remplir_JSON_user(result)
            info=verif_users(result,cin)
            enregistrer_historique(now,cin,fir,info)
        else:
            result=prendre_JSON_user()
            info=verif_users_json(result,cin)
            enregistrer_historique_json(now,cin)
        time.sleep(0.2)
        GPIO.cleanup((36,5,13,29))
    else:
        affichage_error()
        GPIO.cleanup((36,5,13,29))
        

   
