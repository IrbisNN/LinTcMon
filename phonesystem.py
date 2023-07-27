import time
import socket
from acsespec import *
from rose import *
from pyasn1.codec.ber import encoder,decoder
import codecs
from datetime import datetime

encode_hex = codecs.getencoder("hex_codec")
decode_hex = codecs.getdecoder("hex_codec")

class PhoneSystem:
  id = 0
  connect = None
  hostname = ('192.168.8.15', 33333)
  last = time.time()
  outdebug = 0
  indebug = 0
  mydb = None
  calls = {}
  usernames = {}
  numbers = {}
  avtiveNumbers = []
  atsID = ""
  numberPref = ""
  failedCauses = [3,13,65,14,29,15,16,69,33]
  initialized = False
  lastPing = time.time()
  prefMakeCalls = ""
  """Blocked - 35
  Busy - 3
  Call Cancelled - 5
  Destination Not Obtainable - 13
  Destination Out of Order - 65
  Do Not Disturb - 14
  Reorder Tone - 29
  Incompatible Destination - 15
  Invalid Account Code - 16
  Invalid Number Format - 69
  Network Signal - 46
  Normal - 78
  Resource Not Available - 40
  Trunks Busy - 33 """

  def __init__(self,host=('192.168.8.15', 33333),db=None):
    self.hostname = host
    self.connect = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    self.startup(self.hostname)
    self.mydb = db

  def startup(self,hostname):
    self.connect.connect_ex(hostname)
    self.connect.setblocking(False)
    #self.connect.send(b'B')

  def timeout(self):
    tm = 3-(time.time()-self.last)
    if tm<0:
      tm=0
    return tm

  def resetTimeout(self):
    self.last = time.time()


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
      print(f"Out Hex:  {encode_hex(mess_hex)[0]}")
      print(f"Out ASN1: {mess}")
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
  
  def DTMF(self,connectionid,charactersToSend):
    if type(connectionid) != type({}):
      return
    o = invoke(19)
    o.setComponentByName('invokeid',self.NextID())
    o.setComponentByName('opcode',19)
    arg = ArgumentSeq()
    #arg.setComponentByPosition(0,cstautils.toConnectionID(connectionid))
    arg.setComponentByPosition(1,char.IA5String(charactersToSend))
    o.setComponentByName('args',arg)
    self.sendMess(o)

  def SendStatus(self):
    result = invoke(52)
    result.setComponentByName('opcode',52)
    result.setComponentByName('invokeid',self.NextID())
    result['args']['systemStatus'] = SystemStatus(2)
    ret = Rose(52)
    ret.setComponentByName('invoke',result)
    self.sendMess(ret)
    self.resetTimeout()
    for key,val in self.calls.items():
      if val["callstate"] == "Delivered":
        if time.time()-val["started"] > 5 * 60:
          #cstautils.writelog(self,0,key)
          del self.calls[key]

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
          self.mydb.commit()  


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
      print(f"Out Hex:  {encode_hex(dat)[0]}")
      print(f"Out ASN1: {mess}")
    self.connect.send(bytes('\0' + chr(len(dat)), encoding='utf-8'))
    self.connect.send(dat)

  def NextID(self):
    if self.id == 32767:
      self.id = 1
    else:  
      self.id += 1
    return self.id
    
  def readmess(self):
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
      while length>got:
        data = self.connect.recv(ord(data))
        if not data:
          return ""
        full.append(data)
        got = got + len(data)
      return b''.join(full)
    except socket.error as e:
      return full


  def handleCsta(self,data):
    if data:
      if data == "P":
        self.SendSec()
      else:
        if self.indebug:
          print(f"In  Hex:  {encode_hex(data)[0]}")
        if data[0] == 0:
          data = data[2:]
        if self.indebug:
          print(f"In  Hex without 2 oct:  {encode_hex(data)[0]}")
        if encode_hex(data)[0] == b'612f80020780a10706052b0c00815aa203020100a305a103020101be14281206072b0c00821d8148a007a0050303000800':
          print(f"In  ASN1: {data}")
        elif encode_hex(data)[0] == b'a10c020101020200d330030a0102':
          #self.handleAARE(data)
          #self.send_direct_mess(b'A20B0201013006020200D30500')
          self.handleAARE(data)
        elif encode_hex(data)[0] != b'612f80020780a10706052b0c00815aa203020100a305a103020101be14281206072b0c00821d8148a007a0050303000800':
          self.initialized = True
          try:
            decode = decoder.decode(data,asn1Spec=Rose())[0]
          except Exception as ex:
            print(f"Error reading In Hex without 2 oct: {encode_hex(data)[0]}")
            return
          if self.indebug:
            print(f"In  ASN1: {decode}")
          #if data[0] == 0:
          #  data = data[2:]
          #decode = decoder.decode(data,asn1Spec=Rose())[0]
          #if self.indebug:
          #  print(f"In  ASN1: {decode}")
          Obj = decode.getComponent()
          if Obj.isSameTypeWith(AARE_apdu()):
            self.handleAARE(data)
          if Obj.isSameTypeWith(ReturnResult()):
            self.handleResult(data)
          if Obj.isSameTypeWith(Invoke()):
            self.handleInvoke(Obj.getComponentByName('opcode'),data)
        else:
          print(f"In  ASN1: {data}")

  def handleAARE(self,data):
    #decode = decoder.decode(data,asn1Spec=Rose())[0]
    #print(f"In  ASN1: {decode}")
    self.send_direct_mess(b'A11602020602020133300DA40BA009A407A105A0030A0105')
    self.send_direct_mess(b'A116020200E0020133300DA40BA009A407A105A0030A0102')
    #self.StartUpMonitors(settings.localext)
    #self.send_direct_mess(b'A11602020602020133300DA40BA009A407A105A0030A0105')
    #self.send_direct_mess(b'A111020178020147300930058003313031A000')

  def handleResult(self,data):
    decode = decoder.decode(data,asn1Spec=Rose())[0]
    Obj = decode.getComponent()
    ar = Obj.getComponentByName("args")
    ar = ar.getComponentByName("ResultSeq")
    #if(ar.getComponentByPosition(0) not in settings.handledopcodes):
    #  print(f"In ASN1: {decode}")

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
    elif(opcode == 51):  
      decode = decoder.decode(data,asn1Spec=Rose(opcode))[0]
      Obj = decode.getComponent()
      args = Obj.getComponentByName("args").getComponentByName("ArgSeq")
      ar = args.getComponentByPosition(0)
      ar = ar.getComponentByName("cstaprivatedata").getComponentByName("private").getComponentByName("kmeSystemData")
      ar = ar.getComponentByName("systemDataLinkedReply").getComponentByName("KmeSystemDataLinkedReply").getComponentByName("sysData")
      ar = ar.getComponentByName("KmeGetSystemDataRsp").getComponentByName("deviceList").getComponentByName("KmeDeviceStateList")
      for listEntry in ar:
        numberID = listEntry.getComponentByName("device").getComponentByName("deviceIdentifier").getComponentByName("deviceNumber")
        number = listEntry.getComponentByName("number")
        self.numbers[int(numberID)] = int(number)
        self.StartMonitorDeviceNumber(int(numberID))
        #if len(str(number)) == 4:
        #  self.addState(str(number))
    else:
     decode = decoder.decode(data,asn1Spec=Rose(opcode))[0]
     Obj = decode.getComponent()
     print(f"In ASN1: {decode}")

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
    print(event)
    print(refID)
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
    if event == 'Originated':
      print(cc)
      originatedConnection = cc.getComponentByName("originatedConnection")
      both = originatedConnection.getComponentByName("both")
      callID = both.getComponentByName("callID")
      print(callID)
      callingDevice = cc.getComponentByName("callingDevice")
      callingNumber = self.getNumber(callingDevice)
      print(callingNumber)
      calledDevice = cc.getComponentByName("calledDevice")
      calledNumber = self.getNumber(calledDevice)
      print(calledNumber)
      associatedCalledDevice = cc.getComponentByName("associatedCalledDevice")
      associatedCalledNumber = self.getNumber(associatedCalledDevice)
      if associatedCalledNumber:
        print(associatedCalledNumber)
      associatedCallingDevice = cc.getComponentByName("associatedCallingDevice")
      associatedCallingNumber = self.getNumber(associatedCallingDevice)
      if associatedCallingNumber:
        print(associatedCallingNumber)
    elif event == 'Established':
      print(cc)
      originatedConnection = cc.getComponentByName("establishedConnection")
      both = originatedConnection.getComponentByName("both")
      callID = both.getComponentByName("callID")
      print(callID)
      callingDevice = cc.getComponentByName("callingDevice")
      callingNumber = self.getNumber(callingDevice)
      print(callingNumber)
      calledDevice = cc.getComponentByName("calledDevice")
      calledNumber = self.getNumber(calledDevice)
      print(calledNumber)
      answeringDevice = cc.getComponentByName("answeringDevice")
      answeringNumber = self.getNumber(answeringDevice)
      print(answeringNumber)
      if answeringNumber and answeringNumber != calledNumber:
        calledNumber = answeringNumber
      associatedCalledDevice = cc.getComponentByName("associatedCalledDevice")
      associatedCalledNumber = self.getNumber(associatedCalledDevice)
      if associatedCalledNumber:
        print(associatedCalledNumber)
      associatedCallingDevice = cc.getComponentByName("associatedCallingDevice")
      associatedCallingNumber = self.getNumber(associatedCallingDevice)
      if associatedCallingNumber:
        print(associatedCallingNumber)
    elif event == 'Failed':  
      cause = cc.getComponentByName("cause")
      #if int(cause) in self.failedCauses:
      print(cc)
      failedConnection = cc.getComponentByName("failedConnection")
      both = failedConnection.getComponentByName("both")
      callID = both.getComponentByName("callID")
      print(callID)
      callingDevice = cc.getComponentByName("callingDevice")
      callingNumber = self.getNumber(callingDevice)
      print(callingNumber)
      calledDevice = cc.getComponentByName("calledDevice")
      calledNumber = self.getNumber(calledDevice)
      print(calledNumber)
      associatedCalledDevice = cc.getComponentByName("associatedCalledDevice")
      associatedCalledNumber = self.getNumber(associatedCalledDevice)
      if associatedCalledNumber:
        print(associatedCalledNumber)
      associatedCallingDevice = cc.getComponentByName("associatedCallingDevice")
      associatedCallingNumber = self.getNumber(associatedCallingDevice)
      if associatedCallingNumber:
        print(associatedCallingNumber)
    elif event == 'ConnectionCleared':  
      print(cc)
      originatedConnection = cc.getComponentByName("droppedConnection")
      both = originatedConnection.getComponentByName("both")
      callID = both.getComponentByName("callID")
      print(callID)
      releasingDevice = cc.getComponentByName("releasingDevice")
      releasingNumber = self.getNumber(releasingDevice)
      print(releasingNumber)
    elif event == 'ServiceInitiated':  
      print(cc)
      originatedConnection = cc.getComponentByName("initiatedConnection")
      both = originatedConnection.getComponentByName("both")
      callID = both.getComponentByName("callID")
      print(callID)
      initiatingDevice = cc.getComponentByName("initiatingDevice")
      initiatingNumber = self.getNumber(initiatingDevice)
      print(initiatingNumber)
      networkCalledDevice = cc.getComponentByName("networkCalledDevice")
      networkCalledNumber = self.getNumber(networkCalledDevice)
      print(networkCalledNumber)
    elif event == 'Transferred':
      print(cc)  
      primaryOldCall = cc.getComponentByName("primaryOldCall")
      both = primaryOldCall.getComponentByName("both")
      primaryCallID = both.getComponentByName("callID")
      secondaryOldCall = cc.getComponentByName("secondaryOldCall")
      both = secondaryOldCall.getComponentByName("both")
      secondaryCallID = both.getComponentByName("callID")
      if secondaryCallID.isValue == False:
        secondaryCallID = ""

      transferringDevice = cc.getComponentByName("transferringDevice")
      transferringNumber = self.getNumber(transferringDevice)
      print(transferringNumber)

      transferredToDevice = cc.getComponentByName("transferredToDevice")
      transferredToNumber = self.getNumber(transferredToDevice)
      print(transferredToNumber)
      calledNumber = transferredToNumber

      transferredConnections = cc.getComponentByName("transferredConnections")
      for transCon in transferredConnections:
        newConnection = transCon.getComponentByName("newConnection")
        both = newConnection.getComponentByName("both")
        callID = both.getComponentByName("callID")
        print(callID)
        transferredNumber = self.getNumberDeviceID(both)
        print(transferredNumber)
        if str(transferredNumber) != str(transferredToNumber):
          callingNumber = transferredNumber

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

    if (bool(primaryCallID) or bool(secondaryCallID)) and bool(transferringNumber):
      self.changeState(transferringNumber, 0)

    if bool(callID) and bool(releasingNumber) and len(str(releasingNumber)) == 4:
      self.changeState(releasingNumber, 0)

    if bool(callID) and bool(initiatingNumber) and len(str(initiatingNumber)) == 4:
      self.changeState(initiatingNumber, 1)

    if bool(callID) and bool(networkCalledNumber) and len(str(networkCalledNumber)) == 4:
      self.changeState(networkCalledNumber, 1)


  def handleEvent(self, data):
    dec = decoder.decode(data,asn1Spec=Rose())[0] # dec = decoder.decode(data,asn1Spec=Rose(21))[0]
    Obj = dec.getComponent()
    # print(f"In ASN1: {dec}")
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
          print(dec)
          print(ex)
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

    print(ID)
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
                  INSERT INTO "NCalls"(startdate, ID, CallerID, CalledID, Origin, "Line", ATSID, CallID, LastEvent)
                  VALUES (NOW(), '{ID}', '{kwargs["callingNumber"]}', '{kwargs["calledNumber"]}', '{origin}', 'TapiLin', '{self.atsID}', '{ID}', NOW());
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
                  INSERT INTO "NCalls"(answerdate, ID, CallerID, CalledID, Origin, "Line", ATSID, CallID, LastEvent)
                  VALUES (NOW(), '{ID}', '{kwargs["callingNumber"]}', '{kwargs["calledNumber"]}', '{origin}', 'TapiLin', '{self.atsID}', '{ID}', NOW());
                  END IF; END $do$"""
    elif  kwargs["event"] == 'Failed': 
      query = f"""DO $do$ BEGIN IF EXISTS (SELECT ID FROM "NCalls" WHERE ID = '{ID}' AND LastEvent > NOW() - interval '30 minutes')
                  THEN UPDATE "NCalls"
                  SET DropDate = NOW(),
                  CallerID = '{kwargs["callingNumber"]}',
                  CalledID = '{kwargs["calledNumber"]}',
                  Origin = '{origin}',
                  "Line" = 'TapiLin',
                  CallID = '{ID}',
                  Exterminate = '0',
                  LastEvent = NOW()
                  WHERE  ID = '{ID}' AND LastEvent > NOW() - interval '30 minutes';
                  ELSE
                  INSERT INTO "NCalls"(DropDate, ID, CallerID, CalledID, Origin, "Line", ATSID, CallID, LastEvent)
                  VALUES (NOW(), '{ID}', '{kwargs["callingNumber"]}', '{kwargs["calledNumber"]}', '{origin}', 'TapiLin', '{self.atsID}', '{ID}', NOW());
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
                  INSERT INTO "NCalls"(answerdate, ID, CallerID, CalledID, Origin, "Line", ATSID, CallID, LastEvent)
                  VALUES (NOW(), '{ID}', '{kwargs["callingNumber"]}', '{kwargs["calledNumber"]}', '{origin}', 'TapiLin', '{self.atsID}', '{ID}', NOW());
                  END IF; END $do$"""


    if self.mydb and query:
      with self.mydb:
        cur = self.mydb.cursor();
        with cur:
          cur.execute(query)
          self.mydb.commit()
      

  def changeState(self, number, status=0):
    print(number, status)
    if status == 1 and str(number) not in self.avtiveNumbers:
      self.avtiveNumbers.append(str(number))
    elif status == 0 and str(number) in self.avtiveNumbers:
      self.avtiveNumbers.remove(str(number))
    query = f"""SELECT public.tcmonupdatestatus('{self.numberPref}{number}',  {status})"""
  
    with self.mydb:
      cur = self.mydb.cursor();
      with cur:
        cur.execute(query)
        self.mydb.commit()

  def addState(self, number, status=0):
    print(number, status)
  
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
    with self.mydb:
      cur = self.mydb.cursor();
      with cur:
        cur.execute(query)
        self.mydb.commit()