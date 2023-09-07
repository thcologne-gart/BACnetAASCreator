import copy


class RelationshipsBuilder:
    def __init__(self,
                 idAAS: str,
                 idAID: str,
                 idLiveDataSubmodel: str,
                 objectList: list,
                 idTypeAAS: str = "IRI",
                 idTypeAID: str = "IRI",
                 idTypeLiveDataSubmodel: str = "IRI"
                 ):
        self.elements = []
        self.prepareElements(
            idAAS,
            idAID,
            idLiveDataSubmodel,
            idTypeAAS,
            idTypeAID,
            idTypeLiveDataSubmodel
        )
        for objectIdentifier in objectList:
            self.addElement(
                f"SourceSinkRelation_{len(self.elements)}",
                objectIdentifier
            )

    def addElement(self,
                   idShort: str,
                   objectIdentifier: str):
        first, second = self.buildFirstAndSecond(objectIdentifier)
        self.elements.append({
            "idShort": idShort,
            "modelType": {
                "name": "RelationshipElement"
            },
            "first": first,
            "second": second
        })

    def buildFirstAndSecond(self, objectIdentifier):
        if objectIdentifier[0].isdigit():
            objectIdentifier = "proprietary_" + objectIdentifier
        var1 = {"type": "SubmodelElementCollection",
                "idType": "IdShort",
                "value": objectIdentifier,
                "local": True}
        first = copy.deepcopy(self.first)
        second = copy.deepcopy(self.second)
        first["keys"].append(var1)
        second["keys"].append(var1)
        return first, second

    def getElements(self):
        return self.elements

    def prepareElements(self,
                        idAAS: str,
                        idAID: str,
                        idLiveDataSubmodel: str,
                        idTypeAAS: str = "IRI",
                        idTypeAID: str = "IRI",
                        idTypeLiveDataSubmodel: str = "IRI"):
        self.first = {
            "keys": [
                {
                    "type": "AssetAdministrationShell",
                    "idType": idTypeAAS,
                    "value": idAAS,
                    "local": True
                },
                {
                    "type": "Submodel",
                    "idType": idTypeAID,
                    "value": idAID,
                    "local": True
                },
                {
                    "type": "SubmodelElementCollection",
                    "idType": "IdShort",
                    "value": "BACnetInterface",
                    "local": True
                },
                {
                    "type": "SubmodelElementCollection",
                    "idType": "IdShort",
                    "value": "InterfaceMetadata",
                    "local": True
                },
                {
                    "type": "SubmodelElementCollection",
                    "idType": "IdShort",
                    "value": "Properties",
                    "local": True
                }
            ]
        }
        self.second = {
            "keys": [
                {
                    "type": "AssetAdministrationShell",
                    "idType": idTypeAAS,
                    "value": idAAS,
                    "local": True
                },
                {
                    "type": "Submodel",
                    "idType": idTypeLiveDataSubmodel,
                    "value": idLiveDataSubmodel,
                    "local": True
                }
            ]
        }


class AssetInterfaceMappingConfigurationBuilder:
    def __init__(self,
                 id: str,
                 idAAS: str,
                 idAID: str,
                 idType: str = "IRI",
                 idTypeAAS: str = "IRI",
                 idTypeAID: str = "IRI",
                 idShort: str = "AssetInterfaceMappingConfiguration"):
        self.asset_interface_mapping_configuration = {"idShort": idShort,
                                                      "modelType": {
                                                          "name": "Submodel"
                                                      },
                                                      "identification": {
                                                          "id": id,
                                                          "idType": idType
                                                      },
                                                      "semanticId": {"keys": []},
                                                      "submodelElements": [
                                                          {
                                                              "idShort": "Configurations",
                                                              "modelType": {
                                                                  "name": "SubmodelElementCollection"
                                                              },
                                                              "value": [
                                                                  {
                                                                      "idShort": "BacnetMappingConfiguration",
                                                                      "modelType": {
                                                                          "name": "SubmodelElementCollection"
                                                                      },
                                                                      "value": [
                                                                          {
                                                                              "idShort": "ConnectionDescription",
                                                                              "modelType": {
                                                                                  "name": "SubmodelElementCollection"
                                                                              },
                                                                              "value": [
                                                                                  {
                                                                                      "idShort": "Connection",
                                                                                      "modelType": {
                                                                                          "name": "ReferenceElement"
                                                                                      },
                                                                                      "value": {
                                                                                          "keys": [
                                                                                              {
                                                                                                  "type": "AssetAdministrationShell",
                                                                                                  "idType": idTypeAAS,
                                                                                                  "value": idAAS,
                                                                                                  "local": True
                                                                                              },
                                                                                              {
                                                                                                  "type": "Submodel",
                                                                                                  "idType": idTypeAID,
                                                                                                  "value": idAID,
                                                                                                  "local": True
                                                                                              },
                                                                                              {
                                                                                                  "type": "SubmodelElementCollection",
                                                                                                  "idType": "IdShort",
                                                                                                  "value": "BACnetInterface",
                                                                                                  "local": True
                                                                                              }
                                                                                          ]
                                                                                      }
                                                                                  },
                                                                                  {
                                                                                      "idShort": "Security",
                                                                                      "modelType": {
                                                                                          "name": "SubmodelElementCollection"
                                                                                      },
                                                                                      "ordered": False,
                                                                                      "value": []
                                                                                  },
                                                                                  {
                                                                                      "idShort": "ConnectionParameters",
                                                                                      "modelType": {
                                                                                          "name": "SubmodelElementCollection"
                                                                                      },
                                                                                      "ordered": False,
                                                                                      "value": []
                                                                                  }
                                                                              ],
                                                                              "ordered": True
                                                                          },
                                                                          {
                                                                              "idShort": "Mappings",
                                                                              "modelType": {
                                                                                  "name": "SubmodelElementCollection"
                                                                              },
                                                                              "value": [],
                                                                              "ordered": True
                                                                          }
                                                                      ],
                                                                      "ordered": True
                                                                  }
                                                              ],
                                                              "ordered": True
                                                          }
                                                      ],
                                                      "parent": {
                                                          "keys": [
                                                              {
                                                                  "type": "AssetAdministrationShell",
                                                                  "local": False,
                                                                  "value": idAAS,
                                                                  "idType": idTypeAAS
                                                              }
                                                          ]
                                                      }
                                                      }

    def setSemanticId(self, semanticId: dict):
        if "keys" in semanticId.keys():
            self.asset_interface_mapping_configuration["semanticId"] = semanticId
        else:
            self.asset_interface_mapping_configuration["semanticId"]["keys"] = []
            self.asset_interface_mapping_configuration["semanticId"]["keys"].append(semanticId)

    def addRelationshipElement(self, relationshipElement):
        for smc in self.asset_interface_mapping_configuration["submodelElements"][0]["value"][0]["value"]:
            if smc["idShort"] == "Mappings":
                smc["value"].append(relationshipElement)
                break

    def addRelationshipElements(self, relationshipElements: list):
        for smc in self.asset_interface_mapping_configuration["submodelElements"][0]["value"][0]["value"]:
            if smc["idShort"] == "Mappings":
                for relationshipElement in relationshipElements:
                    smc["value"].append(relationshipElement)
                break

    def build(self):
        return self.asset_interface_mapping_configuration


class AssetAdministrationShellBuilder:
    def __init__(self, id: str, idShort: str, assetId: str, submodels: list = [], idType: str = "Custom"):
        self.aas = {
            "modelType": {
                "name": "AssetAdministrationShell"
            },
            "idShort": idShort,
            "identification": {
                "idType": idType,
                "id": id
            },
            "dataSpecification": [

            ],
            "embeddedDataSpecifications": [

            ],
            "submodels": submodels,
            "asset": {
                "keys": [
                    {
                        "type": "Asset",
                        "local": True,
                        "value": assetId,
                        "idType": "Custom"
                    }
                ],
                "modelType": {
                    "name": "Asset"
                },
                "dataSpecification": [

                ],
                "embeddedDataSpecifications": [

                ],
                "idShort": "",
                "identification": {
                    "idType": "IRDI",
                    "id": assetId
                },
                "kind": "Instance"
            },
            "views": [

            ],
            "conceptDictionary": [

            ],
            "category": "CONSTANT",
            "assetRef": {
                "keys": []
            }
        }

    def addSubmodel(self, submodel: dict):
        self.aas["submodels"].append(submodel)

    def addSubmodels(self, submodels: list[dict]):
        for submodel in submodels:
            self.addSubmodel(submodel)

    def build(self):
        return self.aas


class SubmodelBuilder:
    def __init__(self, id: str, idShort: str, idType: str = "Custom", kind: str = "Instance"):
        self.submodel = {
            "semanticId": {"keys": []},
            "identification": {"idType": idType, "id": id},
            "idShort": idShort,
            "kind": kind,
            "dataSpecification": [],
            "qualifiers": [],
            "modelType": {"name": "Submodel"},
            "embeddedDataSpecifications": [],
            "submodelElements": []
        }

    def addSubmodelElement(self, submodelElement: dict):
        self.submodel["submodelElements"].append(submodelElement)

    def addSubmodelElements(self, submodelElements: list[dict]):
        for submodelElement in submodelElements:
            self.addSubmodelElement(submodelElement)

    def setSemanticId(self, semanticId: dict):
        if "keys" in semanticId.keys():
            self.submodel["semanticId"] = semanticId
        else:
            self.submodel["semanticId"]["keys"] = []
            self.submodel["semanticId"]["keys"].append(semanticId)

    def build(self):
        return self.submodel


class SubmodelElementCollectionBuilder:
    def __init__(self, idShort: str, kind: str = "Instance", ordered: bool = False, allowDuplicates: bool = False):
        self.submodel_element_collection = {
            "ordered": ordered,
            "parent": {"keys": []},
            "semanticId": {"keys": []},
            "idShort": idShort,
            "kind": kind,
            "qualifiers": [],
            "modelType": {"name": "SubmodelElementCollection"},
            "value": [],
            "allowDuplicates": allowDuplicates
        }

    def addElement(self, element: dict):
        self.submodel_element_collection["value"].append(element)

    def build(self):
        return self.submodel_element_collection

class PropertyBuilder:
    def __init__(self, idShort: str, kind: str = "Instance", valueType: str = "string", value: str = ""):
        self.property = {
            "semanticId": {"keys": []},
            "idShort": idShort,
            "kind": kind,
            "valueType": valueType,
            "qualifiers": [],
            "modelType": {"name": "Property"},
            "value": value
        }

    def setValue(self, value: str):
        self.property["value"] = value

    def build(self):
        return self.property

