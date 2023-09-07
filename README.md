# BACnetAASCreator

This code provides a simple possibility to discover a BACnet network and create an Asset Administration Shell for each of them automaticly. The AAS will contain the submodels AssetInterfacesDescription (BACnet), AssetInterfaceMappingConfiguration and BACnetDatapointsInformation.

The config.json must contain the target AAS server url, the other options are optional. You can specify the device ids you want to be looked for instead of a whole discovery and specify the AAS ids.

The only external dependency is <a href="https://github.com/ChristianTremblay/BAC0">BAC0</a>.
