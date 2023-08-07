from pyasn1.type import univ, namedtype, tag, constraint, namedval, char, useful
from acsespec import *


class CSTASecurityData(univ.Sequence):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('messageSequenceNumber',univ.Integer())
    )

class NumberDigits(char.IA5String):
  pass

class DeviceNumber(univ.Integer):
  pass #tagSet = univ.Integer.tagSet.tagImplicitly(tag.Tag(tag.tagClassUniversal,tag.tagFormatSimple,1))

#class DeviceID(univ.Choice):
#  componentType=namedtype.NamedTypes(
#    namedtype.NamedType('dialingNumber',NumberDigits().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,0))),
#    namedtype.NamedType('deviceNumber',DeviceNumber().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,1)))
#    )

class DeviceIdentifier(univ.Choice):
  componentType=namedtype.NamedTypes(
    namedtype.OptionalNamedType('dialingNumber',NumberDigits().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,0))),
    namedtype.OptionalNamedType('deviceNumber',DeviceNumber().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,1))),
    namedtype.OptionalNamedType('other',univ.OctetString().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,6)))
    )
  
class DeviceID(univ.Sequence):
  componentType=namedtype.NamedTypes(
    namedtype.NamedType('deviceIdentifier',DeviceIdentifier()),
    namedtype.OptionalNamedType('mediaCallCharacteristics',univ.Null()),
    namedtype.OptionalNamedType('other',univ.OctetString()),
    )
  #tagSet = univ.Sequence.tagSet.tagImplicitly(tag.Tag(tag.tagClassApplication,tag.tagFormatConstructed,1))

class ReqDeviceCategory(univ.Choice):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('reqStandardDevice',univ.Enumerated()), #
  )

class KmeDeviceCategory(univ.Choice):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('standardDevice',ReqDeviceCategory().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,0))), #univ.Enumerated().subtype(implicitTag=tag.Tag(tag.tagClassUniversal,tag.tagFormatSimple,0))), #
  )
  #tagSet = univ.Choice.tagSet.tagImplicitly(tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,0))

class KmeRequestedDevice(univ.Choice):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('category',KmeDeviceCategory().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,1))), #1
  )
  #tagSet = univ.Choice.tagSet.tagImplicitly(tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,0))

class KmeGetSystemDataReq(univ.Choice):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('deviceList',KmeRequestedDevice().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,4))), #4
  )
  #tagSet = univ.Choice.tagSet.tagImplicitly(tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,0))

class KmeSystemDataLinkedReplyValues(univ.Choice):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('crossRefID',univ.OctetString()),
    namedtype.OptionalNamedType('segmentID',univ.Integer()),
    namedtype.OptionalNamedType('lastSegment',univ.Boolean()),
    #namedtype.OptionalNamedType('sysData',KmeRequestedDevice())
  )

class KmeDeviceStateEntry(univ.Sequence):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('device', DeviceID()),
    namedtype.OptionalNamedType('number', char.IA5String()),
    namedtype.OptionalNamedType('status', univ.Enumerated()),
    namedtype.OptionalNamedType('status2', univ.Integer()),
  )

class KmeDeviceStateList(univ.SequenceOf):
  componentType=KmeDeviceStateEntry() #.subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,4))

class KmeDeviceStateListHandle(univ.Choice):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('KmeDeviceStateList', KmeDeviceStateList()),
  )

class KmeGetSystemDataRsp(univ.Sequence):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('deviceList',KmeDeviceStateListHandle().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,38))), 
  )
  #tagSet = univ.Sequence.tagSet.tagImplicitly(tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,0))

class KmeGetSystemDataRspHandle(univ.Choice):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('KmeGetSystemDataRsp', KmeGetSystemDataRsp()),
  )

class KmeGetSystemData(univ.Choice):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('request', KmeGetSystemDataReq()),
    #namedtype.OptionalNamedType('result', KmeGetSystemDataRsp())
  )
  #tagSet = univ.Choice.tagSet.tagImplicitly(tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,0))

class KmeSystemDataLinkedReply(univ.Sequence):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('crossRefID', KmeSystemDataLinkedReplyValues().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,0))), #univ.OctetString()), #0
    namedtype.OptionalNamedType('segmentID',KmeSystemDataLinkedReplyValues().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,1))), #univ.Integer()), #1
    namedtype.OptionalNamedType('lastSegment',KmeSystemDataLinkedReplyValues().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,2))), # univ.Boolean()), #2
    namedtype.OptionalNamedType('sysData',KmeGetSystemDataRspHandle().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,3))) # KmeGetSystemDataRsp()) #3
  )
  #tagSet = univ.Choice.tagSet.tagImplicitly(tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,3))

class KmeSystemDataLinkedReplyHandle(univ.Choice):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('KmeSystemDataLinkedReply', KmeSystemDataLinkedReply()),
  )

class KmeGetSystemDataPosAckHandle(univ.Choice):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('KmeGetSystemDataPosAck', univ.OctetString()),
  )

class KmeSystemData(univ.Choice):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('getSystemData', KmeGetSystemData().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,0))), #0
  #setSystemData
  #systemDataChanged
    namedtype.OptionalNamedType('systemDataLinkedReply', KmeSystemDataLinkedReplyHandle().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,3))), #3
    namedtype.OptionalNamedType('getSystemDataPosAck', KmeGetSystemDataPosAckHandle().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,4))), #4
  #lockSystemData
  #systemDataStatus
  #dataRevisionRecord
  #getDataRevisionRecord
  #setprogrammingEventOn
  )
  tagSet = univ.Choice.tagSet.tagImplicitly(tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,4))

class HoldType(univ.Choice):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('holdType', univ.Enumerated())
  )

class CallID(univ.Choice):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('callID', univ.OctetString())
  )

class DeviceIDHandle(univ.Choice):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('device', DeviceID())
  )

#cl (0) -- Reverse Charging
#tr (1) -- Call Transfer
#fw (2) -- Call Forwarding
#d0 (3) -- DISA/TIE
#rm (4) -- Remote Maintenance
#na (5) -- No Answer
class KmeCdrConditionCode(univ.Choice):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('kmeCdrConditionCode', univ.Enumerated())
  )

class KmeAdditionalData(univ.Choice):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('device', DeviceIDHandle().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,6))),
    namedtype.OptionalNamedType('holdType', HoldType().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,9))),
    namedtype.OptionalNamedType('conditionCode', KmeCdrConditionCode().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,10))),
    namedtype.OptionalNamedType('callID', CallID().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,13))),
    namedtype.OptionalNamedType('didNo', DeviceIDHandle().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,17)))
  )
  tagSet = univ.Choice.tagSet.tagImplicitly(tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,6))

class KMESpecificPrivateData(univ.Choice):
  componentType = namedtype.NamedTypes(
    #namedtype.OptionalNamedType('kmeCallControl',univ.Integer()), #KmeCallControlSrvEvt 1),
    #kmeDeviceStatus KmeDeviceStatus 2
    #kmeDeviceMonitor KmeDeviceMonitor 3
    namedtype.OptionalNamedType('kmeSystemData',KmeSystemData()), #4 EscapeArgument.privateData.private.kmeSystemData.getSystemData.request
    #kmeLocalAlerm [5] KmeLocalAlerm,
    namedtype.OptionalNamedType('kmeAdditionalData', KmeAdditionalData()), #[6]
    #kmePrivateEvent [7] KmePrivateEvent,
    #kmeResourceControl [8] KmeResourceControl,
    #kmeGeneric [9] KmeGenericSrvEvt,
    #kmeExtendedDataAccess [10] OCTET STRING
    #kmePDFControl [11] KmePDFSrvEvt
    #kmeAlterIf [12] KmeAlterIfSrvEvt
    #kmeHotelControl [13] KmeHotelSrvEvt:
  )
  #tagSet = univ.Choice.tagSet.tagImplicitly(tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,0))

class CSTAPrivateDataData(univ.Choice):
  componentType = namedtype.NamedTypes(
    namedtype.NamedType('string',univ.OctetString()),
    #namedtype.NamedType('integer',univ.Integer()),
    namedtype.NamedType('private',KMESpecificPrivateData())
    )
  

class CSTAPrivateData(univ.Sequence):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('manufacturer',univ.ObjectIdentifier()),
    namedtype.OptionalNamedType('data',CSTAPrivateDataData().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,4))),
    namedtype.OptionalNamedType('dataAdditional',CSTAPrivateDataData())
    )

class CSTAPrivateData_list(univ.SequenceOf):
  componentType=CSTAPrivateDataData() # .subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,6))
  
class CSTACommonArguments(univ.Sequence):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('security',CSTASecurityData().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,0))),
    namedtype.OptionalNamedType('privateData',CSTAPrivateData_list().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,1)))
    )
  tagSet = univ.Sequence.tagSet.tagImplicitly(tag.Tag(tag.tagClassApplication,tag.tagFormatConstructed,30))

class SystemStatus(univ.Enumerated):
  tagSet = univ.Enumerated.tagSet.tagImplicitly(tag.Tag(tag.tagClassUniversal,tag.tagFormatSimple,1))

class SystemStatusResult(univ.Sequence):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('opcode',univ.Integer()),
    namedtype.OptionalNamedType('priv',CSTAPrivateData()),
    namedtype.OptionalNamedType('null',univ.Null())
    )

class SystemStatusArg(univ.Sequence):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('systemStatus',SystemStatus()),
    namedtype.OptionalNamedType('extensions',CSTACommonArguments())
    )

class OtherPlan(univ.OctetString):
  tagSet = univ.OctetString.tagSet.tagImplicitly(tag.Tag(tag.tagClassApplication,tag.tagFormatSimple,21))

class InternalNum(NumberDigits):
  tagSet = univ.OctetString.tagSet.tagImplicitly(tag.Tag(tag.tagClassContext,tag.tagFormatSimple,4))

class PublicTON(univ.Choice):
  componentType = namedtype.NamedTypes(
    namedtype.NamedType('unknown',char.IA5String().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,0))),
    namedtype.NamedType('unknown',char.IA5String().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,1))),
    namedtype.NamedType('unknown',char.IA5String().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,2))),
    namedtype.NamedType('unknown',char.IA5String().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,3))),
    namedtype.NamedType('unknown',char.IA5String().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,4))),
    namedtype.NamedType('unknown',char.IA5String().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,5))),    
    )

class PrivateTON(univ.Choice):
  componentType = namedtype.NamedTypes(
    namedtype.NamedType('unknown',char.IA5String().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,0))),
    namedtype.NamedType('unknown',char.IA5String().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,1))),
    namedtype.NamedType('unknown',char.IA5String().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,2))),
    namedtype.NamedType('unknown',char.IA5String().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,3))),
    namedtype.NamedType('unknown',char.IA5String().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,4))),
    namedtype.NamedType('unknown',char.IA5String().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,5))),
    namedtype.NamedType('unknown',char.IA5String().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,6))),    
    )
  
class ExtendedDeviceID(univ.Choice):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('deviceIdentifier',DeviceID()),
    namedtype.OptionalNamedType('implicitPublic',NumberDigits().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,2))),
    namedtype.OptionalNamedType('explicitPublic',PublicTON().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,3))),
    namedtype.OptionalNamedType('implicitPrivate',InternalNum()),
    namedtype.OptionalNamedType('explicitPrivate',PrivateTON().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,5))),
    namedtype.OptionalNamedType('other',OtherPlan().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,6)))
    )

class DynamicID(univ.OctetString):
  tagSet = univ.OctetString.tagSet.tagImplicitly(tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,0))
  subtypeSpec = constraint.ValueRangeConstraint(0, 32)

class LocalDeviceID(univ.Choice):
  componentType=namedtype.NamedTypes(
    namedtype.NamedType('staticID',DeviceID()),
    namedtype.OptionalNamedType('dynamicID',DynamicID())
    )

class BothConnectionID(univ.Sequence):
  componentType=namedtype.NamedTypes(
    namedtype.NamedType('callID',univ.OctetString().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,0))),
    namedtype.NamedType('deviceID',LocalDeviceID().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,1)))
    )
  #tagSet = univ.Sequence.tagSet.tagImplicitly(tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,1))

#class ConnectionID(univ.Sequence):
#  componentType=namedtype.NamedTypes(
#    namedtype.NamedType('call',univ.OctetString().subtype(implicitTag=tag.Tag(tag.tagClassUniversal,tag.tagFormatSimple,0))),
#    namedtype.OptionalNamedType('device',ConDeviceID())
#    )
#  tagSet = univ.Sequence.tagSet.tagImplicitly(tag.Tag(tag.tagClassApplication,tag.tagFormatConstructed,11))

class ConnectionID(univ.Choice):
  componentType=namedtype.NamedTypes(
    namedtype.NamedType('callID',univ.OctetString().subtype(implicitTag=tag.Tag(tag.tagClassUniversal,tag.tagFormatSimple,0))),
    namedtype.NamedType('deviceID',LocalDeviceID().subtype(implicitTag=tag.Tag(tag.tagClassUniversal,tag.tagFormatConstructed,1))),
    namedtype.NamedType('both',BothConnectionID())
    )
  tagSet = univ.Choice.tagSet.tagImplicitly(tag.Tag(tag.tagClassApplication,tag.tagFormatConstructed,11))

class MonitorCrossRefID(univ.OctetString):
  tagSet = univ.OctetString.tagSet.tagImplicitly(tag.Tag(tag.tagClassApplication,tag.tagFormatSimple,21))

class EscapeRegisterID(univ.OctetString):
  tagSet = univ.OctetString.tagSet.tagImplicitly(tag.Tag(tag.tagClassApplication,tag.tagFormatSimple,0))

class NoOfCallsInQueue(univ.Integer):
  tagSet = univ.Integer.tagSet.tagImplicitly(tag.Tag(tag.tagClassUniversal,tag.tagFormatSimple,1))

class ConnectionIDList(univ.SequenceOf):
  tagSet = univ.SequenceOf.tagSet.tagImplicitly(tag.Tag(tag.tagClassApplication,tag.tagFormatSimple,12))
  componentType=ConnectionID()

class CallInfoDetail(univ.Sequence):
  componentType = namedtype.NamedTypes(
    namedtype.NamedType('endpoint',ConnectionID()),
    namedtype.OptionalNamedType('staticEndpoint',DeviceID())
  )

class CallInfo(univ.SequenceOf):
  tagSet = univ.SequenceOf.tagSet.tagImplicitly(tag.Tag(tag.tagClassApplication,tag.tagFormatSimple,13))
  componentType=CallInfoDetail()

class AssociatedNID(univ.Choice):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('deviceIdentifier',DeviceID()),
    namedtype.OptionalNamedType('notKnown',univ.Null()),
    )

class ConnectionListDetail(univ.Sequence):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('newConnection', ConnectionID().subtype(explicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,0))),
    namedtype.OptionalNamedType('associatedNID', AssociatedNID().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,3)))
    )
  
class ConnectionList(univ.SequenceOf):
  componentType=ConnectionListDetail()
  
class CallingDeviceID(univ.Choice):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('deviceIdentifier',DeviceID()),
    namedtype.OptionalNamedType('notKnown',univ.Null().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,7))),
    namedtype.OptionalNamedType('notRequired',univ.Null().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,8)))
    )
  tagSet = univ.Choice.tagSet.tagImplicitly(tag.Tag(tag.tagClassApplication,tag.tagFormatConstructed,1))

class CalledDeviceID(univ.Choice):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('deviceIdentifier',ExtendedDeviceID()),
    namedtype.OptionalNamedType('notKnown',univ.Null().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,7))),
    namedtype.OptionalNamedType('notRequired',univ.Null().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,8)))
    )
  tagSet = univ.Choice.tagSet.tagImplicitly(tag.Tag(tag.tagClassApplication,tag.tagFormatConstructed,2))

class SubjectDeviceID(univ.Choice):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('deviceIdentifier',ExtendedDeviceID()),
    namedtype.OptionalNamedType('notKnown',univ.Null().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,7))),
    namedtype.OptionalNamedType('notRequired',univ.Null().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,8)))
    )
  tagSet = univ.Choice.tagSet.tagImplicitly(tag.Tag(tag.tagClassApplication,tag.tagFormatConstructed,3))

class RedirectionDeviceID(univ.Choice):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('deviceIdentifier',ExtendedDeviceID()),
    namedtype.OptionalNamedType('notKnown',univ.Null().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,7))),
    namedtype.OptionalNamedType('notRequired',univ.Null().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,8)))
    )
  tagSet = univ.Choice.tagSet.tagImplicitly(tag.Tag(tag.tagClassApplication,tag.tagFormatConstructed,4))

class AssociatedCallingDeviceID(univ.Choice):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('deviceIdentifier',ExtendedDeviceID()),
    namedtype.OptionalNamedType('notKnown',univ.Null().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,7)))
    )
  tagSet = univ.Choice.tagSet.tagImplicitly(tag.Tag(tag.tagClassApplication,tag.tagFormatConstructed,5))

class AssociatedCalledDeviceID(univ.Choice):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('deviceIdentifier',ExtendedDeviceID()),
    namedtype.OptionalNamedType('notKnown',univ.Null().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,7)))
    )
  tagSet = univ.Choice.tagSet.tagImplicitly(tag.Tag(tag.tagClassApplication,tag.tagFormatSimple,6))

class NetworkCallingDeviceID(univ.Choice):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('deviceIdentifier',ExtendedDeviceID()),
    namedtype.OptionalNamedType('notKnown',univ.Null().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,7)))
    )
  tagSet = univ.Choice.tagSet.tagImplicitly(tag.Tag(tag.tagClassApplication,tag.tagFormatConstructed,7))

class NetworkCalledDeviceID(univ.Choice):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('deviceIdentifier',ExtendedDeviceID()),
    namedtype.OptionalNamedType('notKnown',univ.Null().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,7)))
    )
  tagSet = univ.Choice.tagSet.tagImplicitly(tag.Tag(tag.tagClassApplication,tag.tagFormatConstructed,8))

class ChargedDevice(univ.Choice):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('operator', DeviceID().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,0))),
    namedtype.OptionalNamedType('nonOperator', DeviceID().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,1)))
    )

class CSTAObject(univ.Choice):
  componentType=namedtype.NamedTypes(
    namedtype.NamedType('deviceObject',DeviceID()),
    namedtype.NamedType('callObject',ConnectionID())
    )

class MonitorObject(CSTAObject):
  pass

#class MonitorFilter(univ.Sequence):
#  componentType = namedtype.NamedTypes(
#    namedtype.OptionalNamedType("call",univ.BitString().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,0))),
#    namedtype.OptionalNamedType("feature",univ.BitString().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,1))),
#    namedtype.OptionalNamedType("agent",univ.BitString().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,2))),
#    namedtype.OptionalNamedType("maintenance",univ.BitString().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,3))),
#    namedtype.OptionalNamedType("private",univ.BitString().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,4)))
#    )

class MonitorFilter(univ.Sequence):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType("callControl",univ.BitString().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,0))),
    namedtype.OptionalNamedType("callAssociated",univ.BitString().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,6))),
    namedtype.OptionalNamedType("mediaAttachment",univ.BitString().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,7))),
    namedtype.OptionalNamedType("physicalDeviceFeature",univ.BitString().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,8))),
    namedtype.OptionalNamedType("logicalDeviceFeature",univ.BitString().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,9))),
    namedtype.OptionalNamedType("maintenance",univ.BitString().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,3))),
    namedtype.OptionalNamedType("voiceUnit",univ.BitString().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,5))),
    namedtype.OptionalNamedType("private",univ.BitString().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,4)))
    )
  tagSet = univ.Sequence.tagSet.tagImplicitly(tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,0))

class LocalConnectionState(univ.Enumerated):
  tagSet = univ.Enumerated.tagSet.tagImplicitly(tag.Tag(tag.tagClassApplication,tag.tagFormatSimple,14))

class Boolean(univ.Integer):
  tagSet = univ.Enumerated.tagSet.tagImplicitly(tag.Tag(tag.tagClassUniversal,tag.tagFormatSimple,1))

class ConferencedEvent(univ.Sequence):
  componentType = namedtype.NamedTypes(
    namedtype.NamedType('primaryOldCall',ConnectionID()),
    namedtype.OptionalNamedType('secondaryOldCall',ConnectionID()),
    namedtype.NamedType('conferencingDevice',SubjectDeviceID()),
    namedtype.NamedType('addedParty',SubjectDeviceID()),
    namedtype.NamedType('conferenceConnections',ConnectionList()),
    namedtype.OptionalNamedType('localConnectionInfo',LocalConnectionState()),
    namedtype.NamedType('cause',univ.Enumerated())
  )
  tagSet = univ.Sequence.tagSet.tagImplicitly(tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,2))

class ConnectionClearedEvent(univ.Sequence):
  componentType = namedtype.NamedTypes(
    namedtype.NamedType('droppedConnection',ConnectionID()),
    namedtype.NamedType('releasingDevice',SubjectDeviceID()),
    namedtype.OptionalNamedType('localConnectionInfo',LocalConnectionState()),
    namedtype.NamedType('cause',univ.Enumerated()),
    namedtype.OptionalNamedType('extensions',CSTACommonArguments())
  )
  tagSet = univ.Sequence.tagSet.tagImplicitly(tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,3))

class DeliveredEvent(univ.Sequence):
  componentType = namedtype.NamedTypes(
    namedtype.NamedType('connection',ConnectionID()),
    namedtype.NamedType('alertingDevice',SubjectDeviceID()),
    namedtype.NamedType('callingDevice',CallingDeviceID()),
    namedtype.NamedType('calledDevice',CalledDeviceID()),
    namedtype.NamedType('lastRedirectionDevice',RedirectionDeviceID()),
    namedtype.OptionalNamedType('localConnectionInfo',LocalConnectionState()),
    namedtype.NamedType('cause',univ.Enumerated()),
    namedtype.OptionalNamedType('networkCallingDevice',NetworkCallingDeviceID()),
    namedtype.OptionalNamedType('networkCalledDevice',NetworkCalledDeviceID()),
    namedtype.OptionalNamedType('associatedCallingDevice',AssociatedCallingDeviceID()),
    namedtype.OptionalNamedType('associatedCalledDevice',AssociatedCalledDeviceID()),
    namedtype.OptionalNamedType('extensions',CSTACommonArguments())
    )
  tagSet = univ.Sequence.tagSet.tagImplicitly(tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,4))

class DivertedEvent(univ.Sequence):
  componentType = namedtype.NamedTypes(
    namedtype.NamedType('connection',ConnectionID()),
    namedtype.NamedType('divertingDevice',SubjectDeviceID()),
    namedtype.NamedType('newDestination',SubjectDeviceID()),
    namedtype.OptionalNamedType('callingDevice',CallingDeviceID()),
    namedtype.OptionalNamedType('calledDevice',CalledDeviceID()),
    namedtype.NamedType('lastRedirectionDevice',RedirectionDeviceID()),
    namedtype.OptionalNamedType('localConnectionInfo',LocalConnectionState()),
    namedtype.NamedType('cause',univ.Enumerated()),
    namedtype.OptionalNamedType('networkCallingDevice',NetworkCallingDeviceID()),
    namedtype.OptionalNamedType('networkCalledDevice',NetworkCalledDeviceID()),
    namedtype.OptionalNamedType('associatedCallingDevice',AssociatedCallingDeviceID()),
    namedtype.OptionalNamedType('associatedCalledDevice',AssociatedCalledDeviceID()),
    namedtype.OptionalNamedType('extensions',CSTACommonArguments())
    )
  tagSet = univ.Sequence.tagSet.tagImplicitly(tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,6))

class EstablishedEvent(univ.Sequence):
  componentType = namedtype.NamedTypes(
    namedtype.NamedType('establishedConnection',ConnectionID()),
    namedtype.NamedType('answeringDevice',SubjectDeviceID()),
    namedtype.NamedType('callingDevice',CallingDeviceID()),
    namedtype.NamedType('calledDevice',CalledDeviceID()),
    namedtype.NamedType('lastRedirectionDevice',RedirectionDeviceID()),
    namedtype.OptionalNamedType('localConnectionInfo',LocalConnectionState()),
    namedtype.NamedType('cause',univ.Enumerated()),
    namedtype.OptionalNamedType('networkCallingDevice',NetworkCallingDeviceID()),
    namedtype.OptionalNamedType('networkCalledDevice',NetworkCalledDeviceID()),
    namedtype.OptionalNamedType('associatedCallingDevice',AssociatedCallingDeviceID()),
    namedtype.OptionalNamedType('associatedCalledDevice',AssociatedCalledDeviceID()),
    namedtype.OptionalNamedType('extensions',CSTACommonArguments())
    )
  tagSet = univ.Sequence.tagSet.tagImplicitly(tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,7))

class FailedEvent(univ.Sequence):
  componentType = namedtype.NamedTypes(
    namedtype.NamedType('failedConnection',ConnectionID()),
    namedtype.NamedType('failingDevice',SubjectDeviceID()),
    namedtype.NamedType('callingDevice',CallingDeviceID()),
    namedtype.NamedType('calledDevice',CalledDeviceID()),
    namedtype.NamedType('lastRedirectionDevice',RedirectionDeviceID()),
    namedtype.OptionalNamedType('localConnectionInfo',LocalConnectionState()),
    namedtype.NamedType('cause',univ.Enumerated()),
    namedtype.OptionalNamedType('networkCallingDevice',NetworkCallingDeviceID()),
    namedtype.OptionalNamedType('networkCalledDevice',NetworkCalledDeviceID()),
    namedtype.OptionalNamedType('associatedCallingDevice',AssociatedCallingDeviceID()),
    namedtype.OptionalNamedType('associatedCalledDevice',AssociatedCalledDeviceID()),
    namedtype.OptionalNamedType('extensions',CSTACommonArguments())
    )
  tagSet = univ.Sequence.tagSet.tagImplicitly(tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,8))

class HeldEvent(univ.Sequence):
  componentType = namedtype.NamedTypes(
    namedtype.NamedType('heldConnection',ConnectionID()),
    namedtype.NamedType('holdingDevice',SubjectDeviceID()),
    namedtype.OptionalNamedType('localConnectionInfo',LocalConnectionState()),
    namedtype.NamedType('cause',univ.Enumerated()),
    namedtype.OptionalNamedType('extensions',CSTACommonArguments())
    )
  tagSet = univ.Sequence.tagSet.tagImplicitly(tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,9))

class NetworkReachedEvent(univ.Sequence):
  componentType = namedtype.NamedTypes(
    namedtype.NamedType('outboundConnection',ConnectionID()),
    namedtype.NamedType('networkInterfaceUsed',SubjectDeviceID()),
    namedtype.NamedType('callingDevice',CallingDeviceID()),
    namedtype.NamedType('calledDevice',CalledDeviceID()),
    namedtype.NamedType('lastRedirectionDevice',RedirectionDeviceID()),
    namedtype.OptionalNamedType('localConnectionInfo',LocalConnectionState()),
    namedtype.NamedType('cause',univ.Enumerated()),
    namedtype.OptionalNamedType('extensions',CSTACommonArguments())
    )
  tagSet = univ.Sequence.tagSet.tagImplicitly(tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,11))

class OriginatedEvent(univ.Sequence):
  componentType = namedtype.NamedTypes(
    namedtype.NamedType('originatedConnection',ConnectionID()),
    namedtype.NamedType('callingDevice',SubjectDeviceID()),
    namedtype.NamedType('calledDevice',CalledDeviceID()),
    namedtype.OptionalNamedType('localConnectionInfo',LocalConnectionState()),
    namedtype.NamedType('cause',univ.Enumerated()),
    namedtype.OptionalNamedType('networkCallingDevice',NetworkCallingDeviceID()),
    namedtype.OptionalNamedType('networkCalledDevice',NetworkCalledDeviceID()),
    namedtype.OptionalNamedType('associatedCallingDevice',AssociatedCallingDeviceID()),
    namedtype.OptionalNamedType('associatedCalledDevice',AssociatedCalledDeviceID()),
    namedtype.OptionalNamedType('extensions',CSTACommonArguments())
    )
  tagSet = univ.Sequence.tagSet.tagImplicitly(tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,13))

class QueuedEvent(univ.Sequence):
  componentType = namedtype.NamedTypes(
    namedtype.NamedType('queuedConnection',ConnectionID()),
    namedtype.NamedType('queue',SubjectDeviceID()),
    namedtype.NamedType('callingDevice',CallingDeviceID()),
    namedtype.NamedType('calledDevice',CalledDeviceID()),
    namedtype.NamedType('lastRedirectionDevice',RedirectionDeviceID()),
    namedtype.OptionalNamedType('callsInFront',univ.Integer().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,1))),
    namedtype.OptionalNamedType('localConnectionInfo',LocalConnectionState()),
    namedtype.NamedType('cause',univ.Enumerated()),
    namedtype.OptionalNamedType('networkCallingDevice',NetworkCallingDeviceID()),
    namedtype.OptionalNamedType('networkCalledDevice',NetworkCalledDeviceID()),
    namedtype.OptionalNamedType('associatedCallingDevice',AssociatedCallingDeviceID()),
    namedtype.OptionalNamedType('associatedCalledDevice',AssociatedCalledDeviceID()),
    namedtype.OptionalNamedType('extensions',CSTACommonArguments())
    )
  tagSet = univ.Sequence.tagSet.tagImplicitly(tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,14))

class RetrievedEvent(univ.Sequence):
  componentType = namedtype.NamedTypes(
    namedtype.NamedType('retrievedConnection',ConnectionID()),
    namedtype.NamedType('retrievingDevice',SubjectDeviceID()),
    namedtype.OptionalNamedType('localConnectionInfo',LocalConnectionState()),
    namedtype.NamedType('cause',univ.Enumerated()),
    namedtype.OptionalNamedType('extensions',CSTACommonArguments())
    )
  tagSet = univ.Sequence.tagSet.tagImplicitly(tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,15))

class ServiceInitiatedEvent(univ.Sequence):
  componentType = namedtype.NamedTypes(
    namedtype.NamedType('initiatedConnection',ConnectionID()),
    namedtype.NamedType('initiatingDevice',SubjectDeviceID()),
    namedtype.OptionalNamedType('localConnectionInfo',LocalConnectionState()),
    namedtype.NamedType('cause',univ.Enumerated()),
    namedtype.OptionalNamedType('networkCallingDevice',NetworkCallingDeviceID()),
    namedtype.OptionalNamedType('networkCalledDevice',NetworkCalledDeviceID()),
    namedtype.OptionalNamedType('extensions',CSTACommonArguments())
    )
  tagSet = univ.Sequence.tagSet.tagImplicitly(tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,16))

class TransferredEvent(univ.Sequence):
  componentType = namedtype.NamedTypes(
    namedtype.NamedType('primaryOldCall',ConnectionID()),
    namedtype.OptionalNamedType('secondaryOldCall',ConnectionID().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,0))),
    namedtype.NamedType('transferringDevice',SubjectDeviceID()),
    namedtype.NamedType('transferredToDevice',SubjectDeviceID()),
    namedtype.NamedType('transferredConnections',ConnectionList().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,1))),
    namedtype.OptionalNamedType('localConnectionInfo',LocalConnectionState()),
    namedtype.NamedType('cause',univ.Enumerated()),
    namedtype.OptionalNamedType('extensions',CSTACommonArguments())
    )
  tagSet = univ.Sequence.tagSet.tagImplicitly(tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,17))

class CallControlEvents(univ.Choice):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('conferenced',ConferencedEvent()),
    namedtype.OptionalNamedType('connectionCleared',ConnectionClearedEvent()),
    namedtype.OptionalNamedType('delivered',DeliveredEvent()),
    namedtype.OptionalNamedType('diverted',DivertedEvent()),
    namedtype.OptionalNamedType('established',EstablishedEvent()),
    namedtype.OptionalNamedType('failed',FailedEvent()),
    namedtype.OptionalNamedType('held',HeldEvent()),
    namedtype.OptionalNamedType('networkReached',NetworkReachedEvent()),
    namedtype.OptionalNamedType('originated',OriginatedEvent()),
    namedtype.OptionalNamedType('queued',QueuedEvent()),
    namedtype.OptionalNamedType('retrieved',RetrievedEvent()),
    namedtype.OptionalNamedType('serviceInitiated',ServiceInitiatedEvent()),
    namedtype.OptionalNamedType('transferred',TransferredEvent())
    )

class EventInfoParts(univ.Choice):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('call',ConnectionID()),
    namedtype.OptionalNamedType('controller',SubjectDeviceID()),
    namedtype.OptionalNamedType('callingDevice',CallingDeviceID()),
    namedtype.OptionalNamedType('calledDevice',CalledDeviceID()),
    namedtype.OptionalNamedType('lastRedirectionDevice',RedirectionDeviceID()),
    namedtype.OptionalNamedType('numberedQueued',NoOfCallsInQueue()),
    namedtype.OptionalNamedType('conferenceconnections',ConnectionList()),
    namedtype.OptionalNamedType('localConnectInfo',LocalConnectionState()),
    namedtype.OptionalNamedType('cause',univ.Enumerated()),
    namedtype.OptionalNamedType('switch',Boolean()),
    namedtype.OptionalNamedType('test',univ.Sequence()),
    namedtype.OptionalNamedType('test',univ.Integer().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,0)))
    )

class EventInfo(univ.SequenceOf):
  componentType = EventInfoParts()
  tagSet = univ.SequenceOf.tagSet.tagImplicitly(tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,0))

class RingerID(univ.OctetString):
  pass

class RingerStatusEvent(univ.Sequence):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('device', SubjectDeviceID()),
	  namedtype.OptionalNamedType('ringer', univ.OctetString()),
	  namedtype.OptionalNamedType('ringMode',	univ.Enumerated()),
	  #namedtype.OptionalNamedType('ringCount', univ.Integer().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,0))), 	#	[0] IMPLICIT INTEGER (0..1000) 			OPTIONAL,
	  #ringPattern	 	[1] IMPLICIT INTEGER 			OPTIONAL,
	  #ringVolume 		[2] Volume			OPTIONAL,
	  namedtype.OptionalNamedType('extensions',	CSTACommonArguments())
  )
  tagSet = univ.Sequence.tagSet.tagImplicitly(tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,8))

class ButtonPressEvent(univ.Sequence):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('device', SubjectDeviceID()),
	  namedtype.OptionalNamedType('button',	univ.OctetString()),
	  namedtype.OptionalNamedType('buttonLabel', char.IA5String()),
	  #namedtype.OptionalNamedType('buttonAssociatedNumber		DeviceID			OPTIONAL,
	  #namedtype.OptionalNamedType('extensions		CSTACommonArguments			OPTIONAL}
  )
  tagSet = univ.Sequence.tagSet.tagImplicitly(tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,1))

class PhysicalDeviceFeatureEvents(univ.Choice):
  componentType = namedtype.NamedTypes(
    #buttonInformation',  		[ 0] IMPLICIT ButtonInformationEvent,
	  namedtype.OptionalNamedType('buttonPress', ButtonPressEvent()),
	  #displayUpdated		[ 2] IMPLICIT DisplayUpdatedEvent,
	  #hookswitch		[ 3] IMPLICIT HookswitchEvent,
	  #lampMode		[ 4] IMPLICIT LampModeEvent,
	  #messageWaiting		[ 5] IMPLICIT MessageWaitingEvent,
	  #microphoneGain		[ 6] IMPLICIT MicrophoneGainEvent,
	  #microphoneMute		[ 7] IMPLICIT MicrophoneMuteEvent,
	  namedtype.OptionalNamedType('ringerStatus',RingerStatusEvent()),
	  #speakerMute		[ 9] IMPLICIT SpeakerMuteEvent,
	  #speakerVolume		[10] IMPLICIT SpeakerVolumeEvent}
  )

class CauseHAndle(univ.Choice):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('cause', univ.Enumerated())
  )

class AgentBusyEvent(univ.Sequence):
  componentType = namedtype.NamedTypes(
  namedtype.OptionalNamedType('agentDevice', SubjectDeviceID()),
	#agentID		AgentID			OPTIONAL,
	#acdGroup		DeviceID			OPTIONAL,
	#pendingAgentState		[2] IMPLICIT PendingAgentState			OPTIONAL,
	#namedtype.OptionalNamedType('cause', CauseHAndle().subtype(implicitTag=tag.Tag(tag.tagClassApplication,tag.tagFormatConstructed,3))),
	#extensions 		CSTACommonArguments			OPTIONAL}
  )

class LogicalDeviceFeatureEvents(univ.Choice):
  componentType = namedtype.NamedTypes(
  	namedtype.OptionalNamedType('agentBusy', AgentBusyEvent().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,0))),
	  #agentLoggedOn		[ 1] IMPLICIT AgentLoggedOnEvent,
	  #agentLoggedOff		[ 2] IMPLICIT AgentLoggedOffEvent,
	  #agentNotReady		[ 3] IMPLICIT AgentNotReadyEvent,
	  #agentReady		[ 4] IMPLICIT AgentReadyEvent,
	  #agentWorkingAfterCall		[ 5] IMPLICIT AgentWorkingAfterCallEvent,
	  #autoAnswer		[ 6] IMPLICIT AutoAnswerEvent,
	  #autoWorkMode		[ 7] IMPLICIT AutoWorkModeEvent,
	  #callBack		[ 8] IMPLICIT CallBackEvent,
	  #callBackMessage		[ 9] IMPLICIT CallBackMessageEvent,
	  #callerIDStatus		[10] IMPLICIT CallerIDStatusEvent,
	  #doNotDisturb		[11] IMPLICIT DoNotDisturbEvent,
	  #forwarding		[12] IMPLICIT ForwardingEvent,
	  #routeingMode		[13] IMPLICIT RouteingModeEvent
  )

class EventSpecificInfo(univ.Choice):
  componentType = namedtype.NamedTypes(
  	namedtype.OptionalNamedType('callControlEvents',CallControlEvents().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,0))),
        #callAssociatedEvents			[1] CallAssociatedEvents,
        #mediaAttachmentEvents			[2] MediaAttachmentEvents,
    namedtype.OptionalNamedType('physicalDeviceFeatureEvents', PhysicalDeviceFeatureEvents().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,3))),
    #namedtype.OptionalNamedType('logicalDeviceFeatureEvents',LogicalDeviceFeatureEvents().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,4))), 	#	[4] LogicalDeviceFeatureEvents,
        #deviceMaintenanceEvents			[5] DeviceMaintenanceEvents,
        #voiceUnitEvents			[6] VoiceUnitEvents,
        #vendorSpecEvents			[7] VendorSpecEvents}
  )
  #tagSet = univ.Sequence.tagSet.tagImplicitly(tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,0))

class MonitorStartArgument(univ.Sequence):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('monitorObject',MonitorObject()),
    namedtype.OptionalNamedType('requestedMonitorFilter',MonitorFilter())
    )

class MakeCallArgument(univ.Sequence):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('callingDevice',DeviceID()),
    namedtype.OptionalNamedType('calledDirectoryNumber',DeviceID())
    )
  
class EscapeArgument(univ.Sequence):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('EscapeRegisterID',EscapeRegisterID()),
    namedtype.OptionalNamedType('CSTASecurityData',CSTASecurityData()),
    namedtype.OptionalNamedType('cstaprivatedata',CSTAPrivateData())
    )
  tagSet = univ.Sequence.tagSet.tagImplicitly(tag.Tag(tag.tagClassApplication,tag.tagFormatConstructed,4))

class ArgumentSeqParts(univ.Choice):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('crossRefIdentifier',MonitorCrossRefID()),
    namedtype.OptionalNamedType('eventType',univ.Integer()),
    namedtype.OptionalNamedType('systemStatus',SystemStatus()),
    namedtype.OptionalNamedType('monitorObject',MonitorObject()),
    namedtype.OptionalNamedType('extensions',CSTACommonArguments()),
    namedtype.OptionalNamedType('eventInfo',EventInfo()),
    namedtype.OptionalNamedType('cstaprivatedata',CSTAPrivateData()),
    namedtype.OptionalNamedType('requestedMonitorFilter',MonitorFilter())
    )

class ArgumentSeq(univ.SequenceOf):
  componentType=ArgumentSeqParts()

class EventTypeID(univ.Choice):
  componentType=namedtype.NamedTypes(
    namedtype.OptionalNamedType("cSTAform",univ.Integer().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,0))),
    )

class NumberOfChargingUnitsItem(univ.Sequence):
  componentType=namedtype.NamedTypes(
    namedtype.OptionalNamedType("chargingUnits", univ.Integer()),
    namedtype.OptionalNamedType("typeOfUnits", univ.OctetString()),
  )

class NumberOfChargingUnits(univ.SequenceOf):
  componentType=NumberOfChargingUnitsItem()      

class NumberOfCurrencyUnits(univ.Sequence):
  componentType=namedtype.NamedTypes(
    namedtype.OptionalNamedType("currencyType", univ.OctetString()),
	  namedtype.OptionalNamedType("currencyAmount", univ.Integer()),
	  namedtype.OptionalNamedType("currencyMultiplier", univ.Enumerated()),
  )

class NumberUnits(univ.Choice):
  componentType=namedtype.NamedTypes(
    namedtype.OptionalNamedType("numberOfChargeUnits", NumberOfChargingUnits().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,0))),
	  namedtype.OptionalNamedType("numberOfCurrencyUnits", NumberOfCurrencyUnits().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,1))),
  )

class ChargingInfo(univ.Sequence):
  componentType=namedtype.NamedTypes(
    namedtype.OptionalNamedType("numberUnits", NumberUnits()),
    namedtype.OptionalNamedType("typeOfChargingInfo", univ.Enumerated())
  )

class StartCDRTransmissionArgument(univ.Sequence):
  componentType=namedtype.NamedTypes(
    namedtype.OptionalNamedType("transferMode", univ.Enumerated()),
    )

class CDRInformationItem(univ.Sequence):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('recordCreationTime', useful.GeneralizedTime()),
    namedtype.OptionalNamedType('callingDevice', CallingDeviceID()),
    namedtype.OptionalNamedType('calledDevice', CalledDeviceID()),
    namedtype.OptionalNamedType('associatedCallingDevice', AssociatedCallingDeviceID()),
    namedtype.OptionalNamedType('associatedCalledDevice', AssociatedCalledDeviceID()),
    namedtype.OptionalNamedType('networkCalledDevice', NetworkCalledDeviceID()),
    namedtype.OptionalNamedType('chargedDevice', ChargedDevice().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,2))),
    namedtype.OptionalNamedType('connectionEnd', useful.GeneralizedTime().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,6))),
    namedtype.OptionalNamedType('connectionDuration', univ.Integer().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,7))),
    namedtype.OptionalNamedType('billingID', univ.Enumerated().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,11))),
    namedtype.OptionalNamedType('chargingInfo', ChargingInfo().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,12))),
    namedtype.OptionalNamedType('reasonForTerm', univ.Enumerated().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,14))),
    namedtype.OptionalNamedType('accountInfo', univ.OctetString().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,16))), 
    )

class CDRInfo(univ.SequenceOf):
  componentType=CDRInformationItem()

def argumentseq(op=-1):
  jack = namedtype.NamedTypes(
    namedtype.OptionalNamedType('crossRefIdentifier',MonitorCrossRefID()),
    namedtype.OptionalNamedType('eventType',univ.Integer()),
    #namedtype.OptionalNamedType('systemStatus',SystemStatus()),
    namedtype.OptionalNamedType('systemStatus',univ.Enumerated()),
    #namedtype.OptionalNamedType('moniterObject',MonitorObject()),
    namedtype.OptionalNamedType('extensions',CSTACommonArguments()),
    #namedtype.OptionalNamedType('eventInfo',EventInfo()),
    namedtype.OptionalNamedType('eventInfo',EventSpecificInfo()),
    namedtype.OptionalNamedType('EscapeRegisterID',EscapeRegisterID()),
    namedtype.OptionalNamedType('cstaprivatedata',CSTAPrivateDataData()), #.subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,4))),
    #namedtype.OptionalNamedType('escape', EscapeArgument())
    namedtype.OptionalNamedType('cdrInfo', CDRInfo())
    )
  if(op==21):
    jack=namedtype.NamedTypes(
      namedtype.OptionalNamedType('crossRefIdentifier',MonitorCrossRefID()),
      namedtype.OptionalNamedType('systemStatus',SystemStatus()),
      namedtype.OptionalNamedType('eventType',EventTypeID()),
      namedtype.OptionalNamedType('extensions',CSTACommonArguments()),
      #namedtype.OptionalNamedType('eventInfo',EventInfo()),
      namedtype.OptionalNamedType('eventInfo',EventSpecificInfo()),
      #namedtype.OptionalNamedType('cstaprivatedata',CSTAPrivateData())
      )
  elif(op==51):
    jack=namedtype.NamedTypes(
      namedtype.OptionalNamedType('EscapeRegisterID',EscapeRegisterID()),
      namedtype.OptionalNamedType('crossRefIdentifier',MonitorCrossRefID()),
      namedtype.OptionalNamedType('cstaprivatedata',CSTAPrivateDataData()) #.subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,4)))
      )
  elif(op==71):
    jack=namedtype.NamedTypes(
      namedtype.OptionalNamedType('moniterObject',MonitorObject()),
      namedtype.OptionalNamedType('requestedMonitorFilter',MonitorFilter()),
      )
  elif(op==10):
    jack=namedtype.NamedTypes(
      namedtype.OptionalNamedType('callingDevice',DeviceID()),
      namedtype.OptionalNamedType('calledDirectoryNumber',DeviceID()),
      )

  return univ.SequenceOf(componentType=univ.Choice(componentType=jack))

class OperationErrors(univ.Enumerated):
  tagSet = univ.Enumerated.tagSet.tagImplicitly(tag.Tag(tag.tagClassUniversal,tag.tagFormatSimple,0))

class SecurityErrors(univ.Enumerated):
  pass #tagSet = univ.Enumerated.tagSet.tagImplicitly(tag.Tag(tag.tagClassUniversal,tag.tagFormatSimple,0))

class StateIncompatibilityErrors(univ.Enumerated):
  pass #tagSet = univ.Enumerated.tagSet.tagImplicitly(tag.Tag(tag.tagClassUniversal,tag.tagFormatSimple,0))

class SystemResourceAvailabilityErrors(univ.Enumerated):
  pass #tagSet = univ.Enumerated.tagSet.tagImplicitly(tag.Tag(tag.tagClassUniversal,tag.tagFormatSimple,0))

class SubscribedResourceAvailabilityErrors(univ.Enumerated):
  pass #tagSet = univ.Enumerated.tagSet.tagImplicitly(tag.Tag(tag.tagClassUniversal,tag.tagFormatSimple,0))

class PerformanceManagementErrors(univ.Enumerated):
  pass #tagSet = univ.Enumerated.tagSet.tagImplicitly(tag.Tag(tag.tagClassUniversal,tag.tagFormatSimple,0))

class PrivateDataErrors(univ.Enumerated):
  pass #tagSet = univ.Enumerated.tagSet.tagImplicitly(tag.Tag(tag.tagClassUniversal,tag.tagFormatSimple,0))

class UniversalFailure(univ.Choice):
  componentType=namedtype.NamedTypes(
    namedtype.OptionalNamedType("operation",OperationErrors()),
    namedtype.OptionalNamedType("security",SecurityErrors()),
    namedtype.OptionalNamedType("stateIncompatibility",StateIncompatibilityErrors()),
    namedtype.OptionalNamedType("systemResourceAvailability",SystemResourceAvailabilityErrors()),
    namedtype.OptionalNamedType("subscribedResourceAvailability",SubscribedResourceAvailabilityErrors()),
    namedtype.OptionalNamedType("performanceManagement",PerformanceManagementErrors()),
    namedtype.OptionalNamedType("privateData",PrivateDataErrors()),
    namedtype.OptionalNamedType("unspecified",univ.Null()) #.subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,7))),
    )
  
#class UniversalFailure(univ.Choice):
#  componentType=namedtype.NamedTypes(
#    namedtype.OptionalNamedType("operationalErrors",OperationErrors().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,0))),
#    namedtype.OptionalNamedType("stateErrors",StateIncompatibilityErrors()),
#    namedtype.OptionalNamedType("systemResourceErrors",SystemResourceAvailabilityErrors()),
#    namedtype.OptionalNamedType("subscribedResourceAvailabilityErrors",SubscribedResourceAvailabilityErrors()),
#    namedtype.OptionalNamedType("performanceErrors",PerformanceManagementErrors()),
#    namedtype.OptionalNamedType("securityErrors",SecurityErrors()),
#    namedtype.OptionalNamedType("unspecifiedErrors",univ.Null().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,7))),
#    namedtype.OptionalNamedType("nonStandardErrors",PrivateDataErrors())
#    )

class ErrorArgs(univ.Choice):
  componentType=namedtype.NamedTypes(
    namedtype.OptionalNamedType("null",univ.Null()),
    namedtype.OptionalNamedType("universalFailure",UniversalFailure().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,0))),
    #namedtype.OptionalNamedType("systemStatus",univ.Integer().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,1))),
    #namedtype.OptionalNamedType("systemStatus",univ.Integer().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,2))),
    )

def args(op=-1):
  if(op==71):
    ret = MonitorStartArgument()
  elif(op==10):
    ret = MakeCallArgument()
  elif(op==363):
    ret = StartCDRTransmissionArgument()
  else:
    ret = univ.Choice(componentType=namedtype.NamedTypes(
      namedtype.OptionalNamedType("null",univ.Null()),
      namedtype.OptionalNamedType("ArgSeq",argumentseq(op)),
      #namedtype.OptionalNamedType("systemStatus",CSTACommonArguments()),
      namedtype.OptionalNamedType("systemStatus",SystemStatus()),
      namedtype.OptionalNamedType("enum",univ.Enumerated())
      ))
  return ret

class MonitorStartResult(univ.Sequence):
  componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType('crossRefIdentifier',MonitorCrossRefID()),
    namedtype.OptionalNamedType('monitorFilter',MonitorFilter()),
    namedtype.OptionalNamedType("cdrCrossRefID",univ.OctetString())
    )

class ResultSeq(univ.SequenceOf):
  componentType = univ.Choice(componentType=namedtype.NamedTypes(
    namedtype.OptionalNamedType('opcode',univ.Integer()),
    #namedtype.OptionalNamedType('priv',CSTAPrivateData()),
    namedtype.OptionalNamedType('null',univ.Null()),
    namedtype.OptionalNamedType('MonitorStartResult',MonitorStartResult()),
    #namedtype.OptionalNamedType('initiatedCall',ConnectionID()),
    #namedtype.OptionalNamedType('universalFailure',UniversalFailure()),
    namedtype.OptionalNamedType('extensions',CSTACommonArguments()),
    ))

class Result(univ.Choice):
  componentType=namedtype.NamedTypes(
    namedtype.OptionalNamedType('null',univ.Null()),
    namedtype.OptionalNamedType('ResultSeq',ResultSeq()),
    )

#class RejectArgs(univ.Choice):
#  componentType=namedtype.NamedTypes(
#    namedtype.OptionalNamedType('null',univ.Null()),
#    namedtype.OptionalNamedType('systemStatus',univ.Integer()),
#    namedtype.OptionalNamedType('general',univ.Integer().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,0))),
#    namedtype.OptionalNamedType('invoke',univ.Integer().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,1))),
#    namedtype.OptionalNamedType('returnResult',univ.Integer().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,2))),
#    namedtype.OptionalNamedType('returnError',univ.Integer().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,3))),
#    namedtype.OptionalNamedType('systemStatus',univ.Integer().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,4))),
#    namedtype.OptionalNamedType('systemStatus',univ.Integer().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,5)))
#    )

class RejectArgs(univ.Choice):
  componentType=namedtype.NamedTypes(
    namedtype.OptionalNamedType('null',univ.Null()),
    namedtype.OptionalNamedType('invokeid',univ.Integer()),
    namedtype.OptionalNamedType('general',univ.Integer().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,0))),
    namedtype.OptionalNamedType('invoke',univ.Integer().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,1))),
    namedtype.OptionalNamedType('returnResult',univ.Integer().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,2))),
    namedtype.OptionalNamedType('returnError',univ.Integer().subtype(implicitTag=tag.Tag(tag.tagClassContext,tag.tagFormatSimple,3)))
  )

class InvokeId(univ.Choice):
  componentType=namedtype.NamedTypes(
    namedtype.OptionalNamedType('null',univ.Null()),
    namedtype.OptionalNamedType('invokeid',univ.Integer())
  )
 
class Invoke(univ.Sequence):
  tagSet = univ.Sequence.tagSet.tagImplicitly(tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,1))

def invoke(op=-1):
  ret=Invoke(componentType=namedtype.NamedTypes(
      namedtype.NamedType('invokeid',univ.Integer()),
      namedtype.OptionalNamedType('opcode',univ.Integer()),
      namedtype.OptionalNamedType('args',args(op))
      ))
  return ret
    

class ReturnResult(univ.Sequence):
  componentType=namedtype.NamedTypes(
    namedtype.NamedType('invokeid',univ.Integer()),
    namedtype.OptionalNamedType('opcode',univ.Integer()),
    namedtype.OptionalNamedType('args',Result())
    )
  tagSet = univ.Sequence.tagSet.tagImplicitly(tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,2))
  
class ReturnError(univ.Sequence):
  componentType=namedtype.NamedTypes(
    namedtype.NamedType('invokeid',univ.Integer()),
    namedtype.NamedType('errorcode',univ.Integer()),
    namedtype.OptionalNamedType('args',ErrorArgs())
    )
  tagSet = univ.Sequence.tagSet.tagImplicitly(tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,3))

class Reject(univ.SequenceOf):
  componentType=RejectArgs()
  tagSet = univ.Sequence.tagSet.tagImplicitly(tag.Tag(tag.tagClassContext,tag.tagFormatConstructed,4))

def Rose(op=-1):
  ros = univ.Choice(componentType = namedtype.NamedTypes(
    namedtype.OptionalNamedType("Invoke",invoke(op)),
    namedtype.OptionalNamedType("ReturnResult",ReturnResult()),
    namedtype.OptionalNamedType("ReturnError",ReturnError()),
    namedtype.OptionalNamedType("Reject",Reject()),
    namedtype.OptionalNamedType("AARQ-apdu",AARQ_apdu()),
    namedtype.OptionalNamedType("AARE-apdu",AARE_apdu()),
    namedtype.OptionalNamedType("ABRT-apdu",ABRT_apdu()),
    ))
  return ros

rose = Rose()