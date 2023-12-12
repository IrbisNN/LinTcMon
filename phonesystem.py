import time
import socket
from acsespec import *
from rose import *
from pyasn1.codec.ber import encoder,decoder
import codecs
from datetime import datetime
import os
import psycopg2
import logging
import logging.handlers

encode_hex = codecs.getencoder("hex_codec")
decode_hex = codecs.getdecoder("hex_codec")

class PhoneSystem:
  id = 0
  connect = None
  hostname = ('', 33333)
  last = time.time()
  outdebug = 0
  indebug = 0
  eventdebug = 0
  dbparam = {}
  mydb = None
  calls = {}
  usernames = {}
  numbers = {}
  avtiveNumbers = []
  atsID = ""
  numberPref = ""
  #failedCauses = [3,13,65,14,29,15,16,69,33]
  failedCauses = [46,65,35]
  initialized = False
  lastPing = time.time()
  prefMakeCalls = ""
  version = "2023-11-11_LinTcMon"
  server = os.uname()[1]
  CDRConditionCode = {0:"Reverse Charging",1:"Call Transfer",2:"Call Forwarding",3:"DISA/TIE",4:"Remote Maintenance",5:"No Answer"}
  CDRStarted = False
  socopen = False
  my_logger = None

  def __init__(self, host=('', 33333), dbparametrs=None, debug=0):
    LOG_FILENAME = "out.log"
    self.my_logger = logging.getLogger('EventLogger')
    self.my_logger.setLevel(logging.DEBUG)
    handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=104857600, backupCount=3)
    df = logging.Formatter('$asctime ${levelname} $message', style='$')
    handler.setFormatter(df)
    self.my_logger.addHandler(handler)

    self.indebug = debug
    self.eventdebug = debug
    self.dbparam = dbparametrs
    self.connectdb()
    self.hostname = host
    self.connect = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    self.startup(self.hostname)

  def startup(self, hostname):
    self.logdebug("Connect to ATS")
    self.connect.connect_ex(hostname)
    self.connect.setblocking(False)
    #self.connect.send(b'B')
    self.socopen = True

  def timeout(self):
    tm = 3-(time.time()-self.last)
    if tm < 0:
      tm = 0
    return tm

  def resetTimeout(self):
    self.last = time.time()
    datediff = time.time() - self.lastPing
    if datediff > 1*60 and self.CDRStarted == False:
      self.startCDR()
    elif datediff > 5*60:
      self.reconnectATS()

  def reconnectATS(self):
    self.logdebug("Reconnect to ATS")
    try:
      self.connect.shutdown(socket.SHUT_RDWR)
      self.connect.close()    
    except socket.error as e:
      self.logerror(e)
    self.CDRStarted = False  
    self.socopen = False
    self.connect = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    #self.startup(self.hostname)
    self.lastPing = time.time()

  def SendSec(self):
    app = ApplicationContextName().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,1))
    # app.setComponentByName('', univ.ObjectIdentifier('1.3.12.0.180.1'))
    app.setComponentByName('', univ.ObjectIdentifier('1.3.12.0.218'))
    security = AARQ_apdu().setComponentByName('application-context-name', app)
    security.setComponentByName('protocol-version', ''.join(format(ord(i), '08b') for i in 'version3'))
    self.sendMess(security)
    

  def send_direct_mess(self, mess=None):
    mess_hex = decode_hex(mess)[0]
    if self.outdebug:
      self.logdebug(f"Out Hex:  {encode_hex(mess_hex)[0]}")
      self.logdebug(f"Out ASN1: {mess}")
    self.connect.send(bytes('\0' + chr(len(mess_hex)), encoding='utf-8'))
    self.connect.send(mess_hex)

  def MakeCall(self,calling,called):
    o = invoke(10)
    o.setComponentByName('invokeid',self.NextID())
    o.setComponentByName('opcode',10)
    deviceIdentifierCalling = DeviceIdentifier()
    deviceIdentifierCalling.setComponentByName('dialingNumber', calling)
    deviceIdentifierCalled = DeviceIdentifier()
    deviceIdentifierCalled.setComponentByName('dialingNumber', called)
    devCalling = DeviceID()
    devCalling.setComponentByName('deviceIdentifier', deviceIdentifierCalling)
    devCalled = DeviceID()
    devCalled.setComponentByName('deviceIdentifier', deviceIdentifierCalled)
    o['args']['callingDevice'] = devCalling
    o['args']['calledDirectoryNumber'] = devCalled
    self.sendMess(o)
  
  def chekMakeCall(self):
    if self.initialized == False:
      return
    query = f"""SELECT ID, InnerNumber, PhoneNumber FROM "MakeCalls" WHERE "Date" >= NOW() - interval '2 minutes' and Done = false and ATSID = '{self.atsID}'"""
    if self.mydb and query:
      with self.mydb:
        cur = self.mydb.cursor();
        with cur:
          cur.execute(query)
          makeCalls = cur.fetchall()
          for call in makeCalls:
            ExtNumber = call[2].strip()
            IntNumber = call[1].strip()
            if len(ExtNumber) < 10:
              ExtNumber = self.prefMakeCalls + ExtNumber
            else:
              ExtNumber = self.prefMakeCalls + "8" + ExtNumber
            if len(IntNumber) == 4 and len(ExtNumber) > 6:
              self.MakeCall(IntNumber, ExtNumber);
            query = f"""UPDATE "MakeCalls" SET Done = true WHERE ID = {call[0]}"""
            cur.execute(query)


  def chekNumberStatus(self):
    for key,val in self.numbers.items():
      if val in self.avtiveNumbers:
        self.changeState(val, 1)
      else:
        self.changeState(val, 0)  

  def StartMonitor(self,ext):
    m = invoke(71)
    m.setComponentByName('invokeid',self.NextID())
    m.setComponentByName('opcode',71)
    arg = MonitorStartArgument()
    mon = MonitorObject()
    dev = DeviceID()
    fil = MonitorFilter()
    dev['deviceIdentifier'].setComponentByName('dialingNumber',ext)
    mon.setComponentByName('deviceObject',dev)
    arg.setComponentByPosition(0,mon)
    arg.setComponentByPosition(1,fil)
    #arg['monitorObject'] = mon
    #m['args']['ArgSeq'] = arg
    m['args'] = arg
    self.sendMess(m)

  def StartMonitorDeviceNumber(self,ext):
    m = invoke(71)
    m.setComponentByName('invokeid',self.NextID())
    m.setComponentByName('opcode',71)
    arg = MonitorStartArgument()
    mon = MonitorObject()
    dev = DeviceID()
    fil = MonitorFilter()
    dev['deviceIdentifier'].setComponentByName('deviceNumber',ext)
    mon.setComponentByName('deviceObject',dev)
    arg.setComponentByPosition(0,mon)
    arg.setComponentByPosition(1,fil)
    #arg['monitorObject'] = mon
    #m['args']['ArgSeq'] = arg
    m['args'] = arg
    self.sendMess(m)

  def StartUpMonitors(self,ran):
    for i in ran:
      self.StartMonitor(i)

  def sendMess(self,mess):
    dat = encoder.encode(mess)
    if self.outdebug:
      self.logdebug(f"Out Hex:  {encode_hex(dat)[0]}")
      self.logdebug(f"Out ASN1: {mess}")
    try:  
      self.connect.send(bytes('\0' + chr(len(dat)), encoding='utf-8'))
      self.connect.send(dat)
    except socket.error as e:
        self.socopen = False

  def NextID(self):
    if self.id == 32767:
      self.id = 1
    else:  
      self.id += 1
    return self.id
    
  def readmess(self):
    full = None
    try:
      data = self.connect.recv(1)
      if not data:
        return ""
      full = [data]
      data = self.connect.recv(1)
      if not data:
        return ""
      full.append(data)
      length = ord(data)
      got = 0
      fulllength = int(encode_hex(b''.join(full))[0], base=16)
      while length>got:
        data = self.connect.recv(fulllength)
        if not data:
          return ""
        full.append(data)
        got = got + len(data)
      return b''.join(full)
    except socket.error as e:
      return full

  def startCDR(self):
    if self.CDRStarted == True:
      return
    #CDRTransferMode
    m = invoke(363)
    m.setComponentByName('invokeid',self.NextID())
    m.setComponentByName('opcode',363)
    arg = StartCDRTransmissionArgument()
    arg.setComponentByName('transferMode', 0)
    m['args'] = arg
    self.sendMess(m)
    self.CDRStarted = True

  def handleCsta(self,data):
    if data:
      if data == "P":
        self.SendSec()
      else:
        if isinstance(data, list):
          data = data[0]

        if self.indebug:
          self.logdebug(f"In  Hex:  {encode_hex(data)[0]}")

        data = data[2:]
        if self.indebug:
          self.logdebug(f"In  Hex without 2 oct:  {encode_hex(data)[0]}")
        if encode_hex(data)[0] == b'800100':
          self.reconnectATS()
        elif encode_hex(data)[0] == b'612f80020780a10706052b0c00815aa203020100a305a103020101be14281206072b0c00821d8148a007a0050303000800':
          self.logdebug(f"In  ASN1: {data}")
        elif encode_hex(data)[0] == b'a10c020101020200d330030a0102':
          #self.handleAARE(data)
          #self.send_direct_mess(b'A20B0201013006020200D30500')
          self.handleAARE(data)
        elif encode_hex(data)[0] != b'612f80020780a10706052b0c00815aa203020100a305a103020101be14281206072b0c00821d8148a007a0050303000800':
          try:
            decode = decoder.decode(data,asn1Spec=Rose())[0]
          except Exception as ex:
            self.logerror(f"Error reading In Hex without 2 oct: {encode_hex(data)[0]}")
            return
          if self.indebug:
            self.logdebug(f"In  ASN1: {decode}")
          #if data[0] == 0:
          #  data = data[2:]
          #decode = decoder.decode(data,asn1Spec=Rose())[0]
          #if self.indebug:
          #  self.logdebug(f"In  ASN1: {decode}")
          Obj = decode.getComponent()
          if Obj.isSameTypeWith(AARE_apdu()):
            self.handleAARE(data)
          if Obj.isSameTypeWith(ReturnResult()):
            self.handleResult(data)
          if Obj.isSameTypeWith(Invoke()):
            self.handleInvoke(Obj.getComponentByName('opcode'),data)
        else:
          self.logdebug(f"In  ASN1: {data}")


  def handleAARE(self,data):
    self.initialized = True
    #decode = decoder.decode(data,asn1Spec=Rose())[0]
    #self.logdebug(f"In  ASN1: {decode}")
    self.send_direct_mess(b'A11602020602020133300DA40BA009A407A105A0030A0105')
    self.send_direct_mess(b'A116020200E0020133300DA40BA009A407A105A0030A0102')
    #self.StartUpMonitors(settings.localext)
    #self.send_direct_mess(b'A111020178020147300930058003313031A000')
    self.addServer()
    #self.startCDR()

  def handleResult(self,data):
    decode = decoder.decode(data,asn1Spec=Rose())[0]
    Obj = decode.getComponent()
    ar = Obj.getComponentByName("args")
    ar = ar.getComponentByName("ResultSeq")
    #if(ar.getComponentByPosition(0) not in settings.handledopcodes):
    #  self.logdebug(f"In ASN1: {decode}")

  def handleInvoke(self,opcode,data):
    if(opcode == 21):
      self.handleEvent(data)
    elif(opcode == 52):
      result = ReturnResult()
      decode = decoder.decode(data,asn1Spec=Rose(opcode))[0]
      Obj = decode.getComponent()
      res = ResultSeq()
      res.setComponentByPosition(0,univ.Integer(52))
      res.setComponentByPosition(1,univ.Null())
      result.setComponentByName('invokeid',Obj.getComponentByName('invokeid'))
      result.setComponentByName('args',res)
      self.sendMess(result)
    elif(opcode == 211):
      result = ReturnResult()
      decode = decoder.decode(data,asn1Spec=Rose(opcode))[0]
      Obj = decode.getComponent()
      res = ResultSeq()
      res[0].setComponentByPosition(0,univ.Integer(211))
      res[1].setComponentByPosition(1,univ.Null(''))
      result.setComponentByName('invokeid',Obj.getComponentByName('invokeid'))
      result.setComponentByName('args',res, verifyConstraints=False)
      self.sendMess(result)
      self.updatePing()
    elif(opcode == 51):  
      decode = decoder.decode(data,asn1Spec=Rose(opcode))[0]
      Obj = decode.getComponent()
      args = Obj.getComponentByName("args").getComponentByName("ArgSeq")
      ar = args.getComponentByPosition(0)
      ar = ar.getComponentByName("cstaprivatedata").getComponentByName("private").getComponentByName("kmeSystemData")
      ls = ar.getComponentByName("systemDataLinkedReply").getComponentByName("KmeSystemDataLinkedReply").getComponentByName("lastSegment")
      ar = ar.getComponentByName("systemDataLinkedReply").getComponentByName("KmeSystemDataLinkedReply").getComponentByName("sysData")
      ar = ar.getComponentByName("KmeGetSystemDataRsp").getComponentByName("deviceList").getComponentByName("KmeDeviceStateList")
      for listEntry in ar:
        numberID = listEntry.getComponentByName("device").getComponentByName("deviceIdentifier").getComponentByName("deviceNumber")
        number = listEntry.getComponentByName("number")
        self.numbers[int(numberID)] = int(number)
        self.StartMonitorDeviceNumber(int(numberID))
        if len(str(number)) == 4:
          self.addState(str(number))
    elif(opcode == 361):
      self.handleCDR(data)
    else:
     decode = decoder.decode(data,asn1Spec=Rose(opcode))[0]
     Obj = decode.getComponent()
     self.logdebug(f"In ASN1: {decode}")

  def getNumber(self, component):
    deviceIdentifier = component.getComponentByName("deviceIdentifier")
    if deviceIdentifier.isSameTypeWith(ExtendedDeviceID()):
      deviceIdentifier = deviceIdentifier.getComponentByName("deviceIdentifier")
    deviceIdentifier = deviceIdentifier.getComponentByName("deviceIdentifier")
    if len(deviceIdentifier.components) > 0:
      number = deviceIdentifier.getComponent()
      if number.isSameTypeWith(DeviceIdentifier().getComponentByName("dialingNumber")) & number.isValue:
        return number
      elif number.isSameTypeWith(DeviceIdentifier().getComponentByName("deviceNumber")) & number.isValue:
        if int(number) in self.numbers:
          return self.numbers[int(number)]
      elif number.isSameTypeWith(DeviceIdentifier().getComponentByName("other")) & number.isValue:
        return number

    return None
  
  def getNumberDeviceID(self, component):
    deviceID = component.getComponentByName("deviceID")
    staticID = deviceID.getComponentByName("staticID")
    deviceIdentifier = staticID.getComponentByName("deviceIdentifier")
    if len(deviceIdentifier.components) > 0:
      number = deviceIdentifier.getComponent()
      if number.isSameTypeWith(DeviceIdentifier().getComponentByName("dialingNumber")) & number.isValue:
        return number
      elif number.isSameTypeWith(DeviceIdentifier().getComponentByName("deviceNumber")) & number.isValue:
        if int(number) in self.numbers:
          return self.numbers[int(number)]
      elif number.isSameTypeWith(DeviceIdentifier().getComponentByName("other")) & number.isValue:
        return number

    return None
  
  def updateCalls(self, cc, event, refID):
    if self.eventdebug:
      self.logdebug(event)
      self.logdebug(refID)
    callID = ""
    callingNumber = ""
    calledNumber = ""
    associatedCalledNumber = ""
    associatedCallingNumber = ""
    releasingNumber = ""
    initiatingNumber = ""
    networkCalledNumber = ""
    primaryCallID = ""
    secondaryCallID = ""
    transferringNumber = ""
    transferredToNumber = ""
    alertingNumber = ""
    if event == 'Originated':
      if self.eventdebug:
        self.logdebug(cc)
      originatedConnection = cc.getComponentByName("originatedConnection")
      both = originatedConnection.getComponentByName("both")
      callID = both.getComponentByName("callID")
      if self.eventdebug:
        self.logdebug(callID)
      callingDevice = cc.getComponentByName("callingDevice")
      callingNumber = self.getNumber(callingDevice)
      if self.eventdebug:
        self.logdebug(callingNumber)
      calledDevice = cc.getComponentByName("calledDevice")
      calledNumber = self.getNumber(calledDevice)
      if self.eventdebug:
        self.logdebug(calledNumber)
      associatedCalledDevice = cc.getComponentByName("associatedCalledDevice")
      associatedCalledNumber = self.getNumber(associatedCalledDevice)
      if associatedCalledNumber and self.eventdebug:
        self.logdebug(associatedCalledNumber)
      associatedCallingDevice = cc.getComponentByName("associatedCallingDevice")
      associatedCallingNumber = self.getNumber(associatedCallingDevice)
      if associatedCallingNumber and self.eventdebug:
        self.logdebug(associatedCallingNumber)
    elif event == 'Established':
      if self.eventdebug:
        self.logdebug(cc)
      originatedConnection = cc.getComponentByName("establishedConnection")
      both = originatedConnection.getComponentByName("both")
      callID = both.getComponentByName("callID")
      if self.eventdebug:
        self.logdebug(callID)
      callingDevice = cc.getComponentByName("callingDevice")
      callingNumber = self.getNumber(callingDevice)
      if self.eventdebug:
        self.logdebug(callingNumber)
      calledDevice = cc.getComponentByName("calledDevice")
      calledNumber = self.getNumber(calledDevice)
      if self.eventdebug:
        self.logdebug(calledNumber)
      answeringDevice = cc.getComponentByName("answeringDevice")
      answeringNumber = self.getNumber(answeringDevice)
      if self.eventdebug:
        self.logdebug(answeringNumber)
      if answeringNumber and answeringNumber != calledNumber:
        calledNumber = answeringNumber
      associatedCalledDevice = cc.getComponentByName("associatedCalledDevice")
      associatedCalledNumber = self.getNumber(associatedCalledDevice)
      if associatedCalledNumber and self.eventdebug:
        self.logdebug(associatedCalledNumber)
      associatedCallingDevice = cc.getComponentByName("associatedCallingDevice")
      associatedCallingNumber = self.getNumber(associatedCallingDevice)
      if associatedCallingNumber and self.eventdebug:
        self.logdebug(associatedCallingNumber)
    elif event == 'Failed':  
      if self.eventdebug:
        self.logdebug(cc)
      cause = cc.getComponentByName("cause")
      #if int(cause) in self.failedCauses:
      failedConnection = cc.getComponentByName("failedConnection")
      both = failedConnection.getComponentByName("both")
      callID = both.getComponentByName("callID")
      if self.eventdebug:
        self.logdebug(callID)
      callingDevice = cc.getComponentByName("callingDevice")
      callingNumber = self.getNumber(callingDevice)
      if self.eventdebug:
        self.logdebug(callingNumber)
      calledDevice = cc.getComponentByName("calledDevice")
      calledNumber = self.getNumber(calledDevice)
      if self.eventdebug:
        self.logdebug(calledNumber)
      associatedCalledDevice = cc.getComponentByName("associatedCalledDevice")
      associatedCalledNumber = self.getNumber(associatedCalledDevice)
      if associatedCalledNumber and self.eventdebug:
        self.logdebug(associatedCalledNumber)
      associatedCallingDevice = cc.getComponentByName("associatedCallingDevice")
      associatedCallingNumber = self.getNumber(associatedCallingDevice)
      if associatedCallingNumber and self.eventdebug:
        self.logdebug(associatedCallingNumber)
    elif event == 'ConnectionCleared':  
      if self.eventdebug:
        self.logdebug(cc)
      originatedConnection = cc.getComponentByName("droppedConnection")
      both = originatedConnection.getComponentByName("both")
      callID = both.getComponentByName("callID")
      if self.eventdebug:
        self.logdebug(callID)
      releasingDevice = cc.getComponentByName("releasingDevice")
      releasingNumber = self.getNumber(releasingDevice)
      if self.eventdebug:
        self.logdebug(releasingNumber)
    elif event == 'ServiceInitiated':  
      if self.eventdebug:
        self.logdebug(cc)
      originatedConnection = cc.getComponentByName("initiatedConnection")
      both = originatedConnection.getComponentByName("both")
      callID = both.getComponentByName("callID")
      if self.eventdebug:
        self.logdebug(callID)
      initiatingDevice = cc.getComponentByName("initiatingDevice")
      initiatingNumber = self.getNumber(initiatingDevice)
      if self.eventdebug:
        self.logdebug(initiatingNumber)
      networkCalledDevice = cc.getComponentByName("networkCalledDevice")
      networkCalledNumber = self.getNumber(networkCalledDevice)
      if self.eventdebug:
        self.logdebug(networkCalledNumber)
    elif event == 'Transferred':
      if self.eventdebug:
        self.logdebug(cc)  
      primaryOldCall = cc.getComponentByName("primaryOldCall")
      both = primaryOldCall.getComponentByName("both")
      primaryCallID = both.getComponentByName("callID")
      secondaryOldCall = cc.getComponentByName("secondaryOldCall")
      both = secondaryOldCall.getComponentByName("both")
      secondaryCallID = both.getComponentByName("callID")
      if secondaryCallID.isValue == False:
        return
        secondaryCallID = ""

      transferringDevice = cc.getComponentByName("transferringDevice")
      transferringNumber = self.getNumber(transferringDevice)
      if self.eventdebug:
        self.logdebug(transferringNumber)

      transferredToDevice = cc.getComponentByName("transferredToDevice")
      transferredToNumber = self.getNumber(transferredToDevice)
      if self.eventdebug:
        self.logdebug(transferredToNumber)
      calledNumber = transferredToNumber

      transferredConnections = cc.getComponentByName("transferredConnections")
      for transCon in transferredConnections:
        newConnection = transCon.getComponentByName("newConnection")
        both = newConnection.getComponentByName("both")
        callID = both.getComponentByName("callID")
        if self.eventdebug:
          self.logdebug(callID)
        transferredNumber = self.getNumberDeviceID(both)
        if self.eventdebug:
          self.logdebug(transferredNumber)
        if str(transferredNumber) != str(transferredToNumber):
          callingNumber = transferredNumber
    elif event == 'Delivered':
      if self.eventdebug:
        self.logdebug(cc)
      connection = cc.getComponentByName("connection")
      both = connection.getComponentByName("both")
      callID = both.getComponentByName("callID")
      if self.eventdebug:
        self.logdebug(callID)
      alertingDevice = cc.getComponentByName("alertingDevice")
      alertingNumber = self.getNumber(alertingDevice)
      if self.eventdebug:
        self.logdebug(alertingNumber)
 
    if bool(callID) and bool(callingNumber) and bool(calledNumber):
      self.addToDB(event=event,
                    callID=str(callID),
                    callingNumber=str(callingNumber),
                    calledNumber=str(calledNumber),
                    primaryCallID=str(primaryCallID),
                    secondaryCallID=str(secondaryCallID),
                    transferringNumber=str(transferringNumber))

    if bool(primaryCallID) and bool(transferringNumber) and bool(transferredToNumber):
      self.addToDB(event='Failed',
                    callID=str(primaryCallID),
                    callingNumber=str(transferringNumber),
                    calledNumber=str(transferredToNumber))

    if bool(secondaryCallID) and bool(callingNumber) and bool(transferringNumber):
      self.addToDB(event='Failed',
                    callID=str(secondaryCallID),
                    callingNumber=str(callingNumber),
                    calledNumber=str(transferringNumber))

    if (bool(primaryCallID) or bool(secondaryCallID)) and bool(transferringNumber) and len(str(transferringNumber)) == 4:
      self.changeState(transferringNumber, 0)

    if bool(callID) and bool(releasingNumber) and len(str(releasingNumber)) == 4:
      self.changeState(releasingNumber, 0)

    if bool(callID) and bool(initiatingNumber) and len(str(initiatingNumber)) == 4:
      self.changeState(initiatingNumber, 1)

    if bool(callID) and bool(networkCalledNumber) and len(str(networkCalledNumber)) == 4:
      self.changeState(networkCalledNumber, 1)

    if bool(callID) and bool(alertingNumber) and len(str(alertingNumber)) == 4:
      self.changeState(alertingNumber, 1)

    if event == 'Failed' and bool(callID) and int(cause) in self.failedCauses:
      if bool(callingNumber) and len(str(callingNumber)) == 4:
        self.changeState(callingNumber, 0)
      if bool(calledNumber) and len(str(calledNumber)) == 4:
        self.changeState(calledNumber, 0)

  def handleCDR(self, data):
    result = ReturnResult()
    decode = decoder.decode(data,asn1Spec=Rose())[0]
    Obj = decode.getComponent()
    res = ResultSeq()
    res[0].setComponentByPosition(0,univ.Integer(361))
    res[1].setComponentByPosition(1,univ.Null(''))
    result.setComponentByName('invokeid',Obj.getComponentByName('invokeid'))
    result.setComponentByName('args',res, verifyConstraints=False)
    self.sendMess(result)
    
    ID = ""
    line = ""
    recordCreationTime = ""
    callingDevice = ""
    calledDevice = ""
    associatedCallingDevice = ""
    associatedCalledDevice = ""
    #networkCalledDevice = ""
    connectionEnd = ""
    connectionDuration = ""
    conditionCode = ""

    dec = decoder.decode(data,asn1Spec=Rose())[0]
    #self.logdebug(f"In ASN1: {dec}")
    Obj = dec.getComponent()
    args = Obj.getComponentByName("args").getComponentByName("ArgSeq")
    for i in args:
      info = i.getComponent()
      if info.isSameTypeWith(CDRInfo()):
        for infoItem in info:
          recordCreationTime = infoItem.getComponentByName("recordCreationTime")
          callingDevice = self.getNumber(infoItem["callingDevice"])
          calledDevice = self.getNumber(infoItem["calledDevice"])
          associatedCallingDevice = self.getNumber(infoItem["associatedCallingDevice"])
          associatedCalledDevice = self.getNumber(infoItem["associatedCalledDevice"])
          #networkCalledDevice = self.getNumber(infoItem["networkCalledDevice"])
          connectionEnd = infoItem["connectionEnd"]
          connectionDuration = infoItem["connectionDuration"]
      elif info.isSameTypeWith(CSTACommonArguments()):
        privateData = info.getComponentByName("privateData")
        for i in privateData:
          conditionCode = i["private"]["kmeAdditionalData"]["conditionCode"]["kmeCdrConditionCode"]

    ID = f'{ID}{recordCreationTime}{callingDevice}{calledDevice}'
    if associatedCallingDevice:
      line = associatedCallingDevice
    if associatedCalledDevice:
      line = associatedCalledDevice
    if connectionEnd.isValue == False:
      connectionEnd = ""
    if connectionDuration.isValue == False:
      connectionDuration = 0
    else:
      connectionDuration //= 10
    if conditionCode:  
      conditionCode = self.CDRConditionCode[conditionCode]

    query = f"""DO $do$ BEGIN IF NOT EXISTS (SELECT "ID" FROM "TAPICDR" WHERE "ID" = '{ID}')
                  THEN INSERT INTO "TAPICDR"("ID", datestart, callingnumber, callednumber, "line", dateend, duration, conditioncode, atsid)
                  VALUES ('{ID}',
                    TO_TIMESTAMP('{recordCreationTime}', 'YYYYMMDDHH24MISS')::timestamp,
                    '{callingDevice}',
                    '{calledDevice}',
                    '{line}',
                    TO_TIMESTAMP('{connectionEnd}', 'YYYYMMDDHH24MISS')::timestamp,
                    '{connectionDuration}',
                    '{conditionCode}',
                    '{self.atsID}');
                  END IF; END $do$"""
    self.executeQuery(query)
          
  def handleEvent(self, data):
    dec = decoder.decode(data,asn1Spec=Rose())[0] # dec = decoder.decode(data,asn1Spec=Rose(21))[0]
    Obj = dec.getComponent()
    # self.logdebug(f"In ASN1: {dec}")
    args = Obj.getComponentByName("args").getComponentByName("ArgSeq")
    refID = b''
    event = ''
    for i in args:
      i = i.getComponent()
      if i.isSameTypeWith(MonitorCrossRefID()):
        refID = encode_hex(bytes(i))[0]
      if i.isSameTypeWith(EventSpecificInfo()):
        cc = i.getComponentByName("callControlEvents")
        try:
          cc = cc.getComponent()
          if cc.isSameTypeWith(ConferencedEvent()):
            event = 'Conferenced'
          elif cc.isSameTypeWith(ConnectionClearedEvent()):
            event = 'ConnectionCleared'
          elif cc.isSameTypeWith(DeliveredEvent()):
            event = 'Delivered'
          elif cc.isSameTypeWith(DivertedEvent()):
            event = 'Diverted'
          elif cc.isSameTypeWith(EstablishedEvent()):
            event = 'Established'
          elif cc.isSameTypeWith(FailedEvent()):
            event = 'Failed'
          elif cc.isSameTypeWith(HeldEvent()):
            event = 'Held'
          elif cc.isSameTypeWith(NetworkReachedEvent()):
            event = 'NetworkReached'
          elif cc.isSameTypeWith(OriginatedEvent()):
            event = 'Originated'
          elif cc.isSameTypeWith(QueuedEvent()):
            event = 'Queued'
          elif cc.isSameTypeWith(RetrievedEvent()):
            event = 'Retrieved'
          elif cc.isSameTypeWith(ServiceInitiatedEvent()):
            event = 'ServiceInitiated'
          elif cc.isSameTypeWith(TransferredEvent()):
            event = 'Transferred'
        except Exception as ex:
          self.logerror(ex)
        #if i.isSameTypeWith(EventTypeID()):
        #  typeid = i.getComponentByName("cSTAform")
        #if i.isSameTypeWith(EventInfo()):
        #  ev = i
    if event:
      self.updateCalls(cc, event, refID)  

  def addToDB(self, **kwargs):
    now = datetime.now()
    ID = self.atsID + kwargs["callID"] + now.strftime("%Y%m%d")
    origin = ''
    if int(kwargs["callingNumber"]) in self.numbers.values() and int(kwargs["calledNumber"]) in self.numbers.values():
        origin = "Internal"
    elif int(kwargs["callingNumber"]) in self.numbers.values():
      origin = "Outgoing"
    elif int(kwargs["calledNumber"]) in self.numbers.values():
      origin = "Incomming"
    else:
      origin = "Unknow"

    if kwargs["event"] == 'Originated':
      query = f"""DO $do$ BEGIN IF EXISTS (SELECT ID FROM "NCalls" WHERE ID = '{ID}' AND LastEvent > NOW() - interval '10 minutes')
                  THEN UPDATE "NCalls"
                  SET startdate = NOW(),
                  DropDate = NULL,
                  CallerID = '{kwargs["callingNumber"]}',
                  CalledID = '{kwargs["calledNumber"]}',
                  Origin = '{origin}',
                  "Line" = 'TapiLin',
                  CallID = '{ID}',
                  Exterminate = '0',
                  LastEvent = NOW()
                  WHERE  ID = '{kwargs["callID"]}' AND LastEvent > NOW() - interval '10 minutes';
                  ELSE
                  INSERT INTO "NCalls"(startdate, ID, CallerID, CalledID, Origin, "Line", ATSID, CallID, LastEvent, Exterminate)
                  VALUES (NOW(), '{ID}', '{kwargs["callingNumber"]}', '{kwargs["calledNumber"]}', '{origin}', 'TapiLin', '{self.atsID}', '{ID}', NOW(), '0');
                  END IF; END $do$"""
    elif  kwargs["event"] == 'Established':
      query = f"""DO $do$ BEGIN IF EXISTS (SELECT ID FROM "NCalls" WHERE ID = '{ID}' AND LastEvent > NOW() - interval '10 minutes')
                  THEN UPDATE "NCalls"
                  SET answerdate = NOW(),
                  DropDate = NULL,
                  CallerID = '{kwargs["callingNumber"]}',
                  CalledID = '{kwargs["calledNumber"]}',
                  Origin = '{origin}',
                  "Line" = 'TapiLin',
                  CallID = '{ID}',
                  Exterminate = '0',
                  LastEvent = NOW()
                  WHERE  ID = '{ID}' AND LastEvent > NOW() - interval '10 minutes';
                  ELSE
                  INSERT INTO "NCalls"(answerdate, ID, CallerID, CalledID, Origin, "Line", ATSID, CallID, LastEvent, Exterminate)
                  VALUES (NOW(), '{ID}', '{kwargs["callingNumber"]}', '{kwargs["calledNumber"]}', '{origin}', 'TapiLin', '{self.atsID}', '{ID}', NOW(), '0');
                  END IF; END $do$"""
    elif  kwargs["event"] == 'Failed': 
      query = f"""DO $do$ BEGIN IF EXISTS (SELECT ID FROM "NCalls" WHERE ID = '{ID}' AND LastEvent > NOW() - interval '30 minutes')
                  THEN UPDATE "NCalls"
                  SET DropDate = NOW(),
                  --CallerID = '{kwargs["callingNumber"]}',
                  --CalledID = '{kwargs["calledNumber"]}',
                  Origin = '{origin}',
                  "Line" = 'TapiLin',
                  CallID = '{ID}',
                  Exterminate = '0',
                  LastEvent = NOW()
                  WHERE  ID = '{ID}' AND LastEvent > NOW() - interval '30 minutes';
                  ELSE
                  INSERT INTO "NCalls"(DropDate, ID, CallerID, CalledID, Origin, "Line", ATSID, CallID, LastEvent, Exterminate)
                  VALUES (NOW(), '{ID}', '{kwargs["callingNumber"]}', '{kwargs["calledNumber"]}', '{origin}', 'TapiLin', '{self.atsID}', '{ID}', NOW(), '0');
                  END IF; END $do$"""
    elif  kwargs["event"] == 'Transferred':
      query = f"""DO $do$ BEGIN IF EXISTS (SELECT ID FROM "NCalls" WHERE ID = '{ID}' AND LastEvent > NOW() - interval '10 minutes')
                  THEN UPDATE "NCalls"
                  SET answerdate = NOW(),
                  startdate = NOW(),
                  CallerID = '{kwargs["callingNumber"]}',
                  CalledID = '{kwargs["calledNumber"]}',
                  Origin = '{origin}',
                  "Line" = 'TapiLin',
                  CallID = '{ID}',
                  Exterminate = '0',
                  LastEvent = NOW()
                  WHERE  ID = '{ID}' AND LastEvent > NOW() - interval '10 minutes';
                  ELSE
                  INSERT INTO "NCalls"(answerdate, ID, CallerID, CalledID, Origin, "Line", ATSID, CallID, LastEvent, Exterminate)
                  VALUES (NOW(), '{ID}', '{kwargs["callingNumber"]}', '{kwargs["calledNumber"]}', '{origin}', 'TapiLin', '{self.atsID}', '{ID}', NOW(), '0');
                  END IF; END $do$"""

    self.executeQuery(query)
      

  def changeState(self, number, status=0):
    if self.eventdebug:
      self.logdebug(f"{number} - {status}")
    if int(number) in self.numbers.values(): 
      if status == 1 and str(number) not in self.avtiveNumbers:
        self.avtiveNumbers.append(str(number))
      elif status == 0 and str(number) in self.avtiveNumbers:
        self.avtiveNumbers.remove(str(number))
      query = f"""SELECT public.tcmonupdatestatus('{self.numberPref}{number}',  {status})"""
      self.executeQuery(query)

  def addState(self, number, status=0):
    if self.eventdebug:
      self.logdebug(f"{number} - {status}")
  
    query = f"""DO $do$ BEGIN CASE WHEN EXISTS (SELECT * FROM "BusyCalls" WHERE extension = '{self.numberPref}{number}' )
                THEN
                  UPDATE "BusyCalls"
                  SET status = {status}
                  WHERE  extension = '{self.numberPref}{number}'
                    AND  status <> 2;
                ELSE
                  INSERT INTO "BusyCalls"("ID", extension, ats, status)
                  VALUES ('{self.atsID}{self.numberPref}{number}', '{self.numberPref}{number}', '{self.atsID}', {status});
                END CASE;  END $do$"""
    self.executeQuery(query)

  def addServer(self):
    query = f"""DO $do$ BEGIN CASE WHEN EXISTS (SELECT * FROM public."TapiServers" WHERE ATSID = '{self.atsID}')
                  THEN
                    UPDATE "TapiServers"
                    SET LastStartDate = NOW()
                    , Version = '{self.version}'
                    , Server = '{self.server}'
                    , pingdate = NOW()
                    WHERE  ATSID = '{self.atsID}';
                  ELSE
                    INSERT INTO public."TapiServers"(ATSID, Server, Version, LastStartDate, pingdate)
                    VALUES ('{self.atsID}', '{self.server}', '{self.version}', NOW(), NOW());
                  END CASE; END $do$"""
    self.executeQuery(query)

  def updatePing(self):
    if self.initialized == True:
      self.lastPing = time.time()
      query = f"""UPDATE "TapiServers"
                      SET pingdate = NOW()
                      WHERE  ATSID = '{self.atsID}'"""
      self.executeQuery(query)

  def executeQuery(self, query):
    if self.mydb and query:
      try:
        with self.mydb:
          cur = self.mydb.cursor();
          with cur:
            cur.execute(query)
      except (psycopg2.DatabaseError, psycopg2.OperationalError) as error:
        time.sleep(5)
        self.logdebug("Reconnect ot DB")
        self.connectdb()

  def connectdb(self):
    if not self.mydb:
      try:
        self.mydb = psycopg2.connect(database="TapiCalls", host=self.dbparam["host"], user=self.dbparam["user"], password=self.dbparam["password"])
        self.mydb.autocommit = True
        if self.mydb:
          cur = self.mydb.cursor()
          cur.execute("commit;")
          self.logdebug("DB Connected")
      except psycopg2.OperationalError as error:
        time.sleep(5)
        self.logdebug("Reconnect ot DB")
        self.connectdb()
      except (Exception, psycopg2.Error) as error:
          raise error
      
  def logdebug(self, msg):
    self.my_logger.debug(msg)
    if self.outdebug:
      print(msg)

  def logerror(self, msg):
    self.my_logger.error(msg)
    if self.outdebug:
      print(msg)