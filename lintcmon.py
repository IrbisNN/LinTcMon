#!/usr/bin/python

import select
import time
import asyncio
import psycopg2
import phonesystem
from settings import ATS_ID, ATS_IP, ATS_PORT, DB_SERVER, DB_USER, DB_PWD, NUMBER_PREF, PREF_MAKECALL


mydb = None
mydb = psycopg2.connect(database="TapiCalls", host=DB_SERVER, user=DB_USER, password=DB_PWD)
mydb.autocommit = True
if mydb:
  cur = mydb.cursor()
  cur.execute("commit;")

HOST = ATS_IP
PORT = ATS_PORT

so = phonesystem.PhoneSystem((HOST,PORT),mydb)
so.atsID = ATS_ID
so.numberPref = NUMBER_PREF
so.prefMakeCalls = PREF_MAKECALL

#so.send_direct_mess(b'602380020780A10706052B0C00815ABE14281206072B0C00821D8148A007A0050303000800')
so.SendSec()

socopen = True
last=time.time()
while socopen:
  sin,sout,serr = select.select([so.connect],[],[so.connect],so.timeout()+0.1)
  for income in sin:
    data=""
    if income == so.connect:
      try:
        data = so.readmess()
      except Exception as e:
        print(e)
        #socopen = False
      so.handleCsta(data)
  if so.timeout()==0:
    so.chekMakeCall()
    #so.chekNumberStatus()
    so.resetTimeout()
    so.updatePing()