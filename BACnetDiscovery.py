import sys
import BAC0
import requests

from utils import utilClass, propertyNameForId, ConfigManager, protocolServices
from patterns import *

def getArgs(args):
    pathConfig = None
    if "-pathConfig" in args:
        pathConfig = args[args.index("-pathConfig") + 1]
    configManager = ConfigManager(pathConfig)

    wantedBacnetDevices = []
    if "-bacnetDevices" in args:
        try:
            var9 = args[args.index("-bacnetDevices") + 1]
            if not var9.isdigit():
                if not var9[0].isdigit():
                    var9 = var9[1:]
                if not var9[-1].isdigit():
                    var9 = var9[:-1]

                if "," in var9:
                    var11 = var9.replace(" ", "").split(",")
                else:
                    var11 = var9.split(" ")

                for deviceId in var11:
                    if deviceId.isdigit():
                        wantedBacnetDevices.append(int(deviceId))
                    else:
                        utilClass.doPrint(f"Provided DeviceId '{deviceId}' is invalid and therefor ignored.")
            else:
                wantedBacnetDevices.append(int(var9))
        except IndexError:
            pass
    else:
        wantedBacnetDevices = configManager.getDevicesList()

    if len(wantedBacnetDevices) == 0:
        utilClass.doPrint("Looking for all BACnet devices\n", newline=True)
    else:
        utilClass.doPrint(f"DeviceIds to look for: {str(wantedBacnetDevices)}\n", newline=True)

    return pathConfig, wantedBacnetDevices, configManager

def getServicesSupported(ipAddress, deviceId):
    try:
        servicesSupported = bacnet.read(f"{ipAddress} device {deviceId} 97")
        return [protocolServices[i] for i in range(len(servicesSupported)) if
                                  servicesSupported[i] == 1]
    except BAC0.core.io.IOExceptions.UnknownPropertyError as e:
        return []

def main():
    global bacnet, configManager
    args = sys.argv[1:]
    pathConfig, wantedBacnetDevices, configManager = getArgs(args)

    urlServer = configManager.getServerUrl()

    bacnet = BAC0.connect()
    bacnet.whois()
    deviceIdsFound = [device[3] for device in bacnet.devices]
    utilClass.doPrint(f"Devices found: {str(deviceIdsFound)}\n", newline=True)

    for deviceId in wantedBacnetDevices:
        if deviceId not in deviceIdsFound:
            utilClass.doPrint(f"Missing wanted device: {deviceId}")

    utilClass.doPrint(f"AAS-server: {urlServer}")

    for device in bacnet.devices:
        deviceName = device[0]
        ipAddress = device[2]
        deviceId = device[3]
        if deviceId not in wantedBacnetDevices and len(wantedBacnetDevices) > 0:
            continue

        utilClass.doPrint(f"Starting to browse device {deviceId}({deviceName})", newline=True)
        objectList = bacnet.read(f"{ipAddress} device {deviceId} objectList")
        utilClass.doPrint(f"Found {str(len(objectList))} objects")

        aasIdFull = configManager.getIdAAS(deviceName, deviceId)
        aasId = aasIdFull["id"]
        idTypeAas = aasIdFull["idType"]

        servicesSupported = getServicesSupported(ipAddress, deviceId)

        submodels = []

        aid, objectPropMap = buildAidSubmodel(ipAddress, objectList, servicesSupported, deviceName, deviceId)
        submodels.append(aid)
        liveData = buildLiveDataSubmodel(objectPropMap, deviceName, deviceId)
        submodels.append(liveData)

        aimc = buildAIMCSubmodel(
            idAAS=aasId,
            idAID=aid["identification"]["id"],
            idLiveDataSubmodel=liveData["identification"]["id"],
            objectList=list(objectPropMap.keys()),
            idTypeAAS=idTypeAas,
            idTypeAID=aid["identification"]["idType"],
            idTypeLiveDataSubmodel=liveData["identification"]["idType"],
            deviceId=deviceId,
            deviceName=deviceName
        )
        submodels.append(aimc)

        addAAS(aasId, idTypeAas, deviceName, deviceId, submodels, urlServer)


def buildLiveDataSubmodel(objectPropMap: dict, deviceName, deviceId):
    idLiveData = configManager.getIdLiveData(deviceName, deviceId)
    submodelBuilder = SubmodelBuilder(idLiveData["id"], "BACnetDatapointsInformation", idType=idLiveData["idType"])
    submodelBuilder.setSemanticId(configManager.getSemanticIdLiveData())
    submodel = submodelBuilder.build()

    for objectIdentifier, propList in objectPropMap.items():
        if objectIdentifier.isnumeric():
            objectIdentifier = "proprietary_" + objectIdentifier
        object_smc = SubmodelElementCollectionBuilder(objectIdentifier).build()
        for prop in propList:
            object_smc["value"].append(PropertyBuilder(idShort=str(prop)).build())

        submodel["submodelElements"].append(object_smc)

    return submodel


def buildAIMCSubmodel(idAAS: str,
                      idAID: str,
                      idLiveDataSubmodel: str,
                      objectList: list,
                      deviceName: str,
                      deviceId,
                      idTypeAAS: str,
                      idTypeAID: str,
                      idTypeLiveDataSubmodel):
    relationshipBuilder = RelationshipsBuilder(
        idAAS,
        idAID,
        idLiveDataSubmodel,
        objectList,
        idTypeAAS,
        idTypeAID,
        idTypeLiveDataSubmodel)
    relations = relationshipBuilder.getElements()

    idAIMC = configManager.getIdAIMC(deviceName, deviceId)
    aimcBuilder = AssetInterfaceMappingConfigurationBuilder(idAIMC["id"], idAAS, idAID, idAIMC["idType"], idTypeAAS, idTypeAID,
                                                            configManager.getIdShortAIMC(deviceName, deviceId))
    semanticIdAimc = configManager.getSemanticIdAIMC()
    aimcBuilder.setSemanticId(semanticIdAimc)
    aimcBuilder.addRelationshipElements(relations)
    return aimcBuilder.build()

def tryAllProperties(ipAddress, object):
    propertyList = []
    for propIndex, propName in propertyNameForId.items():
        try:
            bacnet.read(f'{ipAddress} {object[0]} {object[1]} {propIndex}')
            propertyList.append(propName)
        except:
            continue
    return propertyList

def getObjectProperties(ipAddress, object):
    counter = 0

    try:
        propertyList = bacnet.read(f'{ipAddress} {object[0]} {object[1]} propertyList')

    except BAC0.core.io.IOExceptions.UnknownPropertyError as e:
        try:
            propertyList = []
            propertyTuples = bacnet.readMultiple(f'{ipAddress} {object[0]} {object[1]} all', show_property_name=True)
            for propertyTuple in propertyTuples:
                try:
                    propertyList.append(str(propertyTuple[1]))
                except:
                    continue
            if len(propertyList) < 2:
                propertyList = tryAllProperties(ipAddress, object)
        except KeyError as e:
            propertyList = tryAllProperties(ipAddress, object)

    counter += 1
    return propertyList


def buildAidSubmodel(ipAddress, objectList, servicesSupported, deviceName, deviceId):
    idAidSM = configManager.getIdAID(deviceName, deviceId)
    idShortAid = configManager.getIdShortAID(deviceName, deviceId)
    submodelBuilder = SubmodelBuilder(idAidSM["id"], idShortAid, idType=idAidSM["idType"])
    semanticIdAid = configManager.getSemanticIdAID()
    submodelBuilder.setSemanticId(semanticIdAid)
    submodel = submodelBuilder.build()

    endpointMetadata = SubmodelElementCollectionBuilder("EndpointMetadata").build()
    interfaceMetadata = SubmodelElementCollectionBuilder("InterfaceMetadata").build()
    aid_properties = SubmodelElementCollectionBuilder("Properties").build()
    operations = SubmodelElementCollectionBuilder("Operations").build()
    events = SubmodelElementCollectionBuilder("Events").build()

    objectPropMap = {}
    object_counter = 0
    nr_objects = len(objectList)
    for object in objectList:
        utilClass.doPrint(f"Objects browsed: {str(object_counter)}/{str(nr_objects)}", end="\r")

        objectIdentifier = str(object[0]) + "_" + str(object[1])
        if objectIdentifier[0].isdigit():
            var3 = SubmodelElementCollectionBuilder("proprietary_" + objectIdentifier).build()
        else:
            var3 = SubmodelElementCollectionBuilder(objectIdentifier).build()

        var3["value"].append(PropertyBuilder(idShort="bacnet:ObjectType", value=object[0]).build())
        var3["value"].append(PropertyBuilder(idShort="bacnet:InstanceNumber", value=str(object[1])).build())
        var3["value"].append(PropertyBuilder(idShort="bacnet:service", value=str(servicesSupported)).build())
        var3["value"].append(SubmodelElementCollectionBuilder(idShort="dataMapping").build())

        propertyList = getObjectProperties(ipAddress, object)
        objectPropMap[objectIdentifier] = propertyList
        var3["value"].append(PropertyBuilder(idShort="bacnet:PropertyList", value=str(propertyList)).build())

        aid_properties["value"].append(var3)

        object_counter += 1

        if object_counter == nr_objects:
            utilClass.doPrint(f"Objects browsed: {str(object_counter)}/{str(nr_objects)}", end="\n")

    interfaceMetadata["value"].append(aid_properties)
    interfaceMetadata["value"].append(operations)
    interfaceMetadata["value"].append(events)

    endpointMetadata["value"].append(PropertyBuilder(idShort="base", value=f"bacnet:{ipAddress}").build())
    endpointMetadata["value"].append(PropertyBuilder(idShort="contentType").build())
    endpointMetadata["value"].append(SubmodelElementCollectionBuilder(idShort="securityDefinition").build())
    endpointMetadata["value"].append(SubmodelElementCollectionBuilder(idShort="alternativeEndpointMetadata").build())

    BACnetInterface = SubmodelElementCollectionBuilder("BACnetInterface").build()
    BACnetInterface["value"].append(endpointMetadata)
    BACnetInterface["value"].append(interfaceMetadata)

    submodel["submodelElements"].append(BACnetInterface)

    return submodel, objectPropMap


def putElement(url, element):
    tries = 0
    while tries < 5:
        try:
            r = requests.put(url, str(element))
            if r.status_code != 200:
                utilClass.doPrint(r.status_code)
                utilClass.doPrint(r.text)
                if type(element) == dict:
                    if "idShort" in element.keys():
                        utilClass.doPrint(element["idShort"])
            return r.status_code
        except:
            if tries == 5:
                utilClass.doPrint(
                    f"Failed to publish element: idShort: '{element['idShort']}', id: '{element['identification']['id']}'")
                return 400

            tries += 1


def addAAS(aasId, idTypeAas, deviceName, deviceId, submodels, urlServer):
    assetId = configManager.getAssetId(deviceName, deviceId)
    aasShortId = configManager.getIdShortAAS(deviceName, deviceId)

    aas = AssetAdministrationShellBuilder(aasId, aasShortId, assetId, idType=idTypeAas).build()

    response_code = putElement(urlServer + aasId, str(aas))
    if response_code == 200:
        utilClass.doPrint(f"Published AAS '{aasId}' for device '{deviceId}({deviceName})'")



    for submodel in submodels:
        response_code = putElement(urlServer + aasId + "/aas/submodels/" + submodel["idShort"], str(submodel))
        if response_code == 200:
            idShortSM = submodel['idShort']
            utilClass.doPrint(f"Added Submodel '{idShortSM}' to AAS '{aasId}'")

    return aas


if __name__ == "__main__":
    main()
