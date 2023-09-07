import json
import os
import time
from datetime import datetime


class ConfigManager:
    def __init__(self, pathConfigFile: str = None):
        self.jsonConfig, self.pathConfigFile = self.__loadConfigFile(pathConfigFile)
        self.DEFAULT_ID_TYPE = "IRI"

    def __loadConfigFile(self, pathConfigFile):
        if pathConfigFile == None:
            file_name = os.path.basename(__file__)
            pathConfigFile = __file__.replace(file_name, "config.json")
        else:
            pathConfigFile = pathConfigFile.replace("\\", "/")
            if not pathConfigFile.endswith("config.json"):
                if pathConfigFile.endswith("/"):
                    pathConfigFile = pathConfigFile + "config.json"
                else:
                    pathConfigFile = pathConfigFile + "/config.json"

        if not os.path.isfile(pathConfigFile):
            raise FileNotFoundError(f"No 'config.json'-file found in {pathConfigFile.replace('/config.json', '')}")

        f = open(pathConfigFile)
        return json.loads(f.read()), pathConfigFile

    def getDevicesList(self):
        devices = []
        if "devices" in self.jsonConfig.keys():
            var1 = self.jsonConfig["devices"]
            for deviceId in var1:
                try:
                    devices.append(int(deviceId))
                except ValueError:
                    print(f"Provided DeviceId '{deviceId}' is invalid and therefor ignored.")
        return devices



    def getServerUrl(self):
        if "serverUrl" in self.jsonConfig.keys():
            return self.jsonConfig['serverUrl']
        raise RuntimeError("No serverUrl defined in config-file")

    def __getSemanticId(self, name):
        try:
            var1 = self.jsonConfig[name]
        except KeyError:
            print(f"No {name} defined in config-file. Defaulting to: empty semantic id.")
            return {"keys": []}

        if "keys" in var1.keys():
            self.checkForMandatoryKeys(["idType", "value", "local", "type"], var1["keys"], name)
            return var1
        else:
            self.checkForMandatoryKeys(["idType", "value", "local", "type"], var1, name)
            return {"keys": [var1]}

    def checkForMandatoryKeys(self, mandatoryKeys: list, dictToCheck: dict, dictName: str):
        missingKeys = []
        for key in mandatoryKeys:
            if key not in dictToCheck.keys():
                missingKeys.append(key)
        if len(missingKeys) != 0:
            raise KeyError(f"{dictName} missing mandatory keys: {str(missingKeys)}")

    def getSemanticIdAID(self):
        return self.__getSemanticId("semanticIdAid")

    def getSemanticIdAIMC(self):
        return self.__getSemanticId("semanticIdAimc")

    def getSemanticIdLiveData(self):
        return self.__getSemanticId("semanticIdLiveData")


    def getIdAAS(self, deviceName, deviceId):
        return self.__getId("schemeIdAas", deviceName, deviceId)

    def getIdAID(self, deviceName, deviceId):
        return self.__getId("schemeIdAid", deviceName, deviceId)

    def getIdAIMC(self, deviceName, deviceId):
        return self.__getId("schemeIdAimc", deviceName, deviceId)

    def getIdLiveData(self, deviceName, deviceId):
        return self.__getId("schemeIdLiveData", deviceName, deviceId)

    def __getId(self, name, deviceName, deviceId):
        DEFAULT_ID = f"{name}-$timestamp$"
        if name in self.jsonConfig.keys():
            var3 = self.jsonConfig[name]
        else:
            var3 = {'id': f'{name}-$timestamp$', 'idType': self.DEFAULT_ID_TYPE}
            utilClass.doPrint(f"No {name} defined in config-file. Defaulting to: '{str(var3)}'")

        if type(var3) == str:
            return {"id": utilClass.applySchemeId(var3, deviceName, deviceId), "idType": self.DEFAULT_ID_TYPE}
        elif type(var3) == dict:
            for key in var3.keys():
                if key != "id" and key != "idType" and key != "idShort":
                    utilClass.doPrint(f"Ignoring unknown key '{key}' in {name}")

            var7 = {}
            if "id" in var3.keys():
                var7["id"] = utilClass.applySchemeId(var3["id"], deviceName, deviceId)
            else:
                var7["id"] = utilClass.applySchemeId(DEFAULT_ID, deviceName, deviceId)
                utilClass.doPrint(f"No id defined for {name}. Defaulting to: '{var7['id']}'")
            if "idType" in var3.keys():
                var7["idType"] = var3["idType"]
            else:
                var7["idType"] = self.DEFAULT_ID_TYPE
                utilClass.doPrint(f"No idType defined for {name}. Defaulting to: '{var7['idType']}'")
            return var7

    def getAssetId(self, deviceName, deviceId):
        default = f"bacnet_device_{deviceId}_{deviceName}"
        if "assetId" in self.jsonConfig.keys():
            assetId = self.jsonConfig["assetId"]
            if type(assetId) == str:
                return assetId.replace("$deviceName$", deviceName).replace("$deviceId$", str(deviceId))
            utilClass.doPrint(f"Value of key assetId should be String, is {str(type(assetId))}. Defaulting assetId to: '{default}'")
            return default

    def getIdShortAAS(self, deviceName, deviceId):
        var11 = self.__getIdShort("schemeIdAas", deviceName, deviceId)
        return var11.replace("$deviceName$", deviceName).replace("$deviceId$", str(deviceId))
    def getIdShortAID(self, deviceName, deviceId):
        return self.__getIdShort("schemeIdAid", deviceName, deviceId)
    def getIdShortAIMC(self, deviceName, deviceId):
        return self.__getIdShort("schemeIdAimc", deviceName, deviceId)
    def getIdShortLiveData(self, deviceName, deviceId):
        return self.__getIdShort("schemeIdLiveData", deviceName, deviceId)

    def __getIdShort(self, name, deviceName, deviceId):
        defaults = {
            "schemeIdAas": "$deviceName$($deviceId$)",
            "schemeIdAid": "AssetInterfacesDescription",
            "schemeIdAimc": "AssetInterfaceMappingConfiguration",
            "schemeIdLiveData": "BACnetDatapointsInformation"
        }
        if name in self.jsonConfig.keys():
            var9 = self.jsonConfig[name]
            if type(var9) == dict:
                if "idShort" in var9.keys():
                    return utilClass.applySchemeId(var9["idShort"], deviceName, deviceId)
                else:
                    utilClass.doPrint(f"No idShort defined for {name} in config-file. Defaulting to: '{defaults[name]}'")
                    return utilClass.applySchemeId(defaults[name], deviceName, deviceId)
            else:
                utilClass.doPrint(f"Value of key {name} should be JSON-object, is {str(type(var9))}. Defaulting idShort to: '{defaults[name]}'")
                return utilClass.applySchemeId(defaults[name], deviceName, deviceId)
        else:
            utilClass.doPrint(f"No {name} defined in config-file. Defaulting idShort to: '{defaults[name]}'")
            return utilClass.applySchemeId(defaults[name], deviceName, deviceId)


class utilClass:
    @staticmethod
    def doPrint(string, end="\n", newline=False):
        date_time = datetime.fromtimestamp(time.time())
        timestamp = date_time.strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]

        if newline:
            print(f"\n{timestamp} - INFO    | {string}", end=end)
        else:
            print(f"{timestamp} - INFO    | {string}", end=end)


    @staticmethod
    def applySchemeId(scheme, deviceName, deviceId):
        if type(scheme) == str:
            return utilClass.__applyScheme(scheme, deviceName, deviceId)
        elif type(scheme) == dict:
            if "id" not in scheme.keys():
                raise ValueError(f"Provided dictionary does not contain key 'id'")
            scheme["id"] = utilClass.__applyScheme(scheme["id"], deviceName, deviceId)
            return scheme
        else:
            raise ValueError(f"Illegal argument type: {type(scheme)}")

    @staticmethod
    def __applyScheme(id: str, deviceName, deviceId) -> str:
        time_ns = str(time.time_ns())
        st = time.localtime()
        return id \
            .replace("$timestamp$", time_ns) \
            .replace("$timestamp_ns$", time_ns) \
            .replace("$timestamp_ms$", time_ns[:-3]) \
            .replace("$timestamp_s$", time_ns[:-6]) \
            .replace("$day$", str(st.tm_mday)) \
            .replace("$month$", str(st.tm_mon)) \
            .replace("$year$", str(st.tm_year)) \
            .replace("$hour$", str(st.tm_hour)) \
            .replace("$min$", str(st.tm_min)) \
            .replace("$sec$", str(st.tm_sec)) \
            .replace("$deviceName$", str(deviceName)) \
            .replace("$deviceId$", str(deviceId))


protocolServices = {0: "acknowledgeAlarm",
                    1: "confirmedCovNotification",
                    2: "confirmedEventNotification",
                    3: "getAlarmSummary",
                    4: "getEnrollmentSummary",
                    5: "subscribeCov",
                    6: "atomicReadFile",
                    7: "atomicWriteFile",
                    8: "addListElement",
                    9: "removeListElement",
                    10: "createObject",
                    11: "deleteObject",
                    12: "readProperty",
                    13: "readPropertyConditional",
                    14: "readPropertyMultiple",
                    15: "writeProperty",
                    16: "writePropertyMultiple",
                    17: "deviceCommunicationControl",
                    18: "confirmedPrivateTransfer",
                    19: "confirmedTextMessage",
                    20: "reinitializeDevice",
                    21: "vtOpen",
                    22: "vtClose",
                    23: "vtData",
                    24: "authenticate",
                    25: "requestKey",
                    26: "iAm",
                    27: "iHave",
                    28: "unconfirmedCovNotification",
                    29: "unconfirmedEventNotification",
                    30: "unconfirmedPrivateTransfer",
                    31: "unconfirmedTextMessage",
                    32: "timeSynchronization",
                    33: "whoHas",
                    34: "whoIs",
                    35: "readRange",
                    36: "utcTimeSynchronization",
                    37: "lifeSafetyOperation",
                    38: "subscribeCovProperty",
                    39: "getEventInformation",
                    40: "writeGroup",
                    41: "subscribeCovPropertyMultiple",
                    42: "confirmedCovNotificationMultiple",
                    43: "unconfirmedCovNotificationMultiple"}

propertyNameForId = {
    0: "ackedTransitions",
    1: "ackRequired",
    2: "action",
    3: "actionText",
    4: "activeText",
    5: "activeVtSessions",
    6: "alarmValue",
    7: "alarmValues",
    8: "all",
    9: "allWritesSuccessful",
    10: "apduSegmentTimeout",
    11: "apduTimeout",
    12: "applicationSoftwareVersion",
    13: "archive",
    14: "bias",
    15: "changeOfStateCount",
    16: "changeOfStateTime",
    17: "notificationClass",
    19: "controlledVariableReference",
    20: "controlledVariableUnits",
    21: "controlledVariableValue",
    22: "covIncrement",
    23: "dateList",
    24: "daylightSavingsStatus",
    25: "deadband",
    26: "derivativeConstant",
    27: "derivativeConstantUnits",
    28: "description",
    29: "descriptionOfHalt",
    30: "deviceAddressBinding",
    31: "deviceType",
    32: "effectivePeriod",
    33: "elapsedActiveTime",
    34: "errorLimit",
    35: "eventEnable",
    36: "eventState",
    37: "eventType",
    38: "exceptionSchedule",
    39: "faultValues",
    40: "feedbackValue",
    41: "fileAccessMethod",
    42: "fileSize",
    43: "fileType",
    44: "firmwareRevision",
    45: "highLimit",
    46: "inactiveText",
    47: "inProcess",
    48: "instanceOf",
    49: "integralConstant",
    50: "integralConstantUnits",
    52: "limitEnable",
    53: "listOfGroupMembers",
    54: "listOfObjectPropertyReferences",
    56: "localDate",
    57: "localTime",
    58: "location",
    59: "lowLimit",
    60: "manipulatedVariableReference",
    61: "maximumOutput",
    62: "maxApduLengthAccepted",
    63: "maxInfoFrames",
    64: "maxMaster",
    65: "maxPresValue",
    66: "minimumOffTime",
    67: "minimumOnTime",
    68: "minimumOutput",
    69: "minPresValue",
    70: "modelName",
    71: "modificationDate",
    72: "notifyType",
    73: "numberOfApduRetries",
    74: "numberOfStates",
    75: "objectIdentifier",
    76: "objectList",
    77: "objectName",
    78: "objectPropertyReference",
    79: "objectType",
    80: "optional",
    81: "outOfService",
    82: "outputUnits",
    83: "eventParameters",
    84: "polarity",
    85: "presentValue",
    86: "priority",
    87: "priorityArray",
    88: "priorityForWriting",
    89: "processIdentifier",
    90: "programChange",
    91: "programLocation",
    92: "programState",
    93: "proportionalConstant",
    94: "proportionalConstantUnits",
    96: "protocolObjectTypesSupported",
    97: "protocolServicesSupported",
    98: "protocolVersion",
    99: "readOnly",
    100: "reasonForHalt",
    102: "recipientList",
    103: "reliability",
    104: "relinquishDefault",
    105: "required",
    106: "resolution",
    107: "segmentationSupported",
    108: "setpoint",
    109: "setpointReference",
    110: "stateText",
    111: "statusFlags",
    112: "systemStatus",
    113: "timeDelay",
    114: "timeOfActiveTimeReset",
    115: "timeOfStateCountReset",
    116: "timeSynchronizationRecipients",
    117: "units",
    118: "updateInterval",
    119: "utcOffset",
    120: "vendorIdentifier",
    121: "vendorName",
    122: "vtClassesSupported",
    123: "weeklySchedule",
    124: "attemptedSamples",
    125: "averageValue",
    126: "bufferSize",
    127: "clientCovIncrement",
    128: "covResubscriptionInterval",
    130: "eventTimeStamps",
    131: "logBuffer",
    132: "logDeviceObjectProperty",
    133: "enable",
    134: "logInterval",
    135: "maximumValue",
    136: "minimumValue",
    137: "notificationThreshold",
    139: "protocolRevision",
    140: "recordsSinceNotification",
    141: "recordCount",
    142: "startTime",
    143: "stopTime",
    144: "stopWhenFull",
    145: "totalRecordCount",
    146: "validSamples",
    147: "windowInterval",
    148: "windowSamples",
    149: "maximumValueTimestamp",
    150: "minimumValueTimestamp",
    151: "varianceValue",
    152: "activeCovSubscriptions",
    153: "backupFailureTimeout",
    154: "configurationFiles",
    155: "databaseRevision",
    156: "directReading",
    157: "lastRestoreTime",
    158: "maintenanceRequired",
    159: "memberOf",
    160: "mode",
    161: "operationExpected",
    162: "setting",
    163: "silenced",
    164: "trackingValue",
    165: "zoneMembers",
    166: "lifeSafetyAlarmValues",
    167: "maxSegmentsAccepted",
    168: "profileName",
    169: "autoSlaveDiscovery",
    170: "manualSlaveAddressBinding",
    171: "slaveAddressBinding",
    172: "slaveProxyEnable",
    173: "lastNotifyRecord",
    174: "scheduleDefault",
    175: "acceptedModes",
    176: "adjustValue",
    177: "count",
    178: "countBeforeChange",
    179: "countChangeTime",
    180: "covPeriod",
    181: "inputReference",
    182: "limitMonitoringInterval",
    183: "loggingObject",
    184: "loggingRecord",
    185: "prescale",
    186: "pulseRate",
    187: "scale",
    188: "scaleFactor",
    189: "updateTime",
    190: "valueBeforeChange",
    191: "valueSet",
    192: "valueChangeTime",
    193: "alignIntervals",
    195: "intervalOffset",
    196: "lastRestartReason",
    197: "loggingType",
    202: "restartNotificationRecipients",
    203: "timeOfDeviceRestart",
    204: "timeSynchronizationInterval",
    205: "trigger",
    206: "utcTimeSynchronizationRecipients",
    207: "nodeSubtype",
    208: "nodeType",
    209: "structuredObjectList",
    210: "subordinateAnnotations",
    211: "subordinateList",
    212: "actualShedLevel",
    213: "dutyWindow",
    214: "expectedShedLevel",
    215: "fullDutyBaseline",
    218: "requestedShedLevel",
    219: "shedDuration",
    220: "shedLevelDescriptions",
    221: "shedLevels",
    222: "stateDescription",
    226: "doorAlarmState",
    227: "doorExtendedPulseTime",
    228: "doorMembers",
    229: "doorOpenTooLongTime",
    230: "doorPulseTime",
    231: "doorStatus",
    232: "doorUnlockDelayTime",
    233: "lockStatus",
    234: "maskedAlarmValues",
    235: "securedStatus",
    244: "absenteeLimit",
    245: "accessAlarmEvents",
    246: "accessDoors",
    247: "accessEvent",
    248: "accessEventAuthenticationFactor",
    249: "accessEventCredential",
    250: "accessEventTime",
    251: "accessTransactionEvents",
    252: "accompaniment",
    253: "accompanimentTime",
    254: "activationTime",
    255: "activeAuthenticationPolicy",
    256: "assignedAccessRights",
    257: "authenticationFactors",
    258: "authenticationPolicyList",
    259: "authenticationPolicyNames",
    260: "authenticationStatus",
    261: "authorizationMode",
    262: "belongsTo",
    263: "credentialDisable",
    264: "credentialStatus",
    265: "credentials",
    266: "credentialsInZone",
    267: "daysRemaining",
    268: "entryPoints",
    269: "exitPoints",
    270: "expirationTime",
    271: "extendedTimeEnable",
    272: "failedAttemptEvents",
    273: "failedAttempts",
    274: "failedAttemptsTime",
    275: "lastAccessEvent",
    276: "lastAccessPoint",
    277: "lastCredentialAdded",
    278: "lastCredentialAddedTime",
    279: "lastCredentialRemoved",
    280: "lastCredentialRemovedTime",
    281: "lastUseTime",
    282: "lockout",
    283: "lockoutRelinquishTime",
    285: "maxFailedAttempts",
    286: "members",
    287: "musterPoint",
    288: "negativeAccessRules",
    289: "numberOfAuthenticationPolicies",
    290: "occupancyCount",
    291: "occupancyCountAdjust",
    292: "occupancyCountEnable",
    294: "occupancyLowerLimit",
    295: "occupancyLowerLimitEnforced",
    296: "occupancyState",
    297: "occupancyUpperLimit",
    298: "occupancyUpperLimitEnforced",
    300: "passbackMode",
    301: "passbackTimeout",
    302: "positiveAccessRules",
    303: "reasonForDisable",
    304: "supportedFormats",
    305: "supportedFormatClasses",
    306: "threatAuthority",
    307: "threatLevel",
    308: "traceFlag",
    309: "transactionNotificationClass",
    310: "userExternalIdentifier",
    311: "userInformationReference",
    317: "userName",
    318: "userType",
    319: "usesRemaining",
    320: "zoneFrom",
    321: "zoneTo",
    322: "accessEventTag",
    323: "globalIdentifier",
    326: "verificationTime",
    327: "baseDeviceSecurityPolicy",
    328: "distributionKeyRevision",
    329: "doNotHide",
    330: "keySets",
    331: "lastKeyServer",
    332: "networkAccessSecurityPolicies",
    333: "packetReorderTime",
    334: "securityPduTimeout",
    335: "securityTimeWindow",
    336: "supportedSecurityAlgorithms",
    337: "updateKeySetTimeout",
    338: "backupAndRestoreState",
    339: "backupPreparationTime",
    340: "restoreCompletionTime",
    341: "restorePreparationTime",
    342: "bitMask",
    343: "bitText",
    344: "isUtc",
    345: "groupMembers",
    346: "groupMemberNames",
    347: "memberStatusFlags",
    348: "requestedUpdateInterval",
    349: "covuPeriod",
    350: "covuRecipients",
    351: "eventMessageTexts",
    352: "eventMessageTextsConfig",
    353: "eventDetectionEnable",
    354: "eventAlgorithmInhibit",
    355: "eventAlgorithmInhibitRef",
    356: "timeDelayNormal",
    357: "reliabilityEvaluationInhibit",
    358: "faultParameters",
    359: "faultType",
    360: "localForwardingOnly",
    361: "processIdentifierFilter",
    362: "subscribedRecipients",
    363: "portFilter",
    364: "authorizationExemptions",
    365: "allowGroupDelayInhibit",
    366: "channelNumber",
    367: "controlGroups",
    368: "executionDelay",
    369: "lastPriority",
    370: "writeStatus",
    371: "propertyList",
    372: "serialNumber",
    373: "blinkWarnEnable",
    374: "defaultFadeTime",
    375: "defaultRampRate",
    376: "defaultStepIncrement",
    377: "egressTime",
    378: "inProgress",
    379: "instantaneousPower",
    380: "lightingCommand",
    381: "lightingCommandDefaultPriority",
    382: "maxActualValue",
    383: "minActualValue",
    384: "power",
    385: "transition",
    386: "egressActive",
    387: "interfaceValue",
    388: "faultHighLimit",
    389: "faultLowLimit",
    390: "lowDiffLimit",
    391: "strikeCount",
    392: "timeOfStrikeCountReset",
    393: "defaultTimeout",
    394: "initialTimeout",
    395: "lastStateChange",
    396: "stateChangeValues",
    397: "timerRunning",
    398: "timerState",
    399: "apduLength",
    400: "ipAddress",
    401: "ipDefaultGateway",
    402: "ipDhcpEnable",
    403: "ipDhcpLeaseTime",
    404: "ipDhcpLeaseTimeRemaining",
    405: "ipDhcpServer",
    406: "ipDnsServer",
    407: "bacnetIpGlobalAddress",
    408: "bacnetIpMode",
    409: "bacnetIpMulticastAddress",
    410: "bacnetIpNatTraversal",
    411: "ipSubnetMask",
    412: "bacnetIpUdpPort",
    413: "bbmdAcceptFdRegistrations",
    414: "bbmdBroadcastDistributionTable",
    415: "bbmdForeignDeviceTable",
    416: "changesPending",
    417: "command",
    418: "fdBbmdAddress",
    419: "fdSubscriptionLifetime",
    420: "linkSpeed",
    421: "linkSpeeds",
    422: "linkSpeedAutonegotiate",
    423: "macAddress",
    424: "networkInterfaceName",
    425: "networkNumber",
    426: "networkNumberQuality",
    427: "networkType",
    428: "routingTable",
    429: "virtualMacAddressTable",
    430: "commandTimeArray",
    431: "currentCommandPriority",
    432: "lastCommandTime",
    433: "valueSource",
    434: "valueSourceArray",
    435: "bacnetIpv6Mode",
    436: "ipv6Address",
    437: "ipv6PrefixLength",
    438: "bacnetIpv6UdpPort",
    439: "ipv6DefaultGateway",
    440: "bacnetIpv6MulticastAddress",
    441: "ipv6DnsServer",
    442: "ipv6AutoAddressingEnable",
    443: "ipv6DhcpLeaseTime",
    444: "ipv6DhcpLeaseTimeRemaining",
    445: "ipv6DhcpServer",
    446: "ipv6ZoneIndex",
    447: "assignedLandingCalls",
    448: "carAssignedDirection",
    449: "carDoorCommand",
    450: "carDoorStatus",
    451: "carDoorText",
    452: "carDoorZone",
    453: "carDriveStatus",
    454: "carLoad",
    455: "carLoadUnits",
    456: "carMode",
    457: "carMovingDirection",
    458: "carPosition",
    459: "elevatorGroup",
    460: "energyMeter",
    461: "energyMeterRef",
    462: "escalatorMode",
    463: "faultSignals",
    464: "floorText",
    465: "groupId",
    467: "groupMode",
    468: "higherDeck",
    469: "installationId",
    470: "landingCalls",
    471: "landingCallControl",
    472: "landingDoorStatus",
    473: "lowerDeck",
    474: "machineRoomId",
    475: "makingCarCall",
    476: "nextStoppingFloor",
    477: "operationDirection",
    478: "passengerAlarm",
    479: "powerMode",
    480: "registeredCarCall",
    481: "activeCovMultipleSubscriptions",
    482: "protocolLevel",
    483: "referencePort",
    484: "deployedProfileLocation",
    485: "profileLocation",
    486: "tags",
    487: "subordinateNodeTypes",
    488: "subordinateTags",
    489: "subordinateRelationships",
    490: "defaultSubordinateRelationship",
    491: "represents"
}
