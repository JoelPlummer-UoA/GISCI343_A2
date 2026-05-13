## 1. Motivation and Audience

### 1.1 What problem does your dashboard address?

[Where are cyclist crashes concentrated, and how does this align with the cycle facility network?]




### 1.2 Who is it for?

<!-- Describe one or two realistic users — their role and the decision this dashboard informs. -->

[The first user it could be for is a cyclist. They might use this dashboard to understand where cycle crashes are concentrated, in order to possibly avoid or take extra care of any locations where cycle crashes are concentrated. Another user could be someone from a transport company such as AT. They could use this dashboard to see where cycle crashes are concentrated, then if this is not in the cycle network, it would show them places they need to make safer for cyclists. Otherwise if it is in the cycle network, it could let them know that part needs upgrading or the community needs some educating about the cycle network.]

### 1.3 What insight does it enable?

<!-- One sentence: the single most important thing a user should take away. -->
<!-- This sentence might become the title or subtitle of your app. -->

[THe most important thing the user should take away is where the locations are the have a concentration of cycle crashes, and even possibly why that is the case.]


## 2. Data and Preparation

### 2.1 Datasets used

| Dataset | Source URL | Format | Rows (approx.) | Key variables |
|---------|------------|--------|----------------|---------------|
| Crash Analysis System | AT GIS open data | shapefile | ~6,409 | bicycle, crashYear, fatalCount, minorInjur, speedLimit, weatherA, crashLoc_1, crashSever|
| Cycle Facility Network | AT GIS open data | shapefile | ~2,086 | LOCALBOARD, TYPEOFFACI, Construction Year, Road Name|

### 2.2 Cleaning and preparation steps

<!-- List the steps needed to get each dataset ready. One line each. -->

1. [Drop columns 'advisorySp', 'areaUnitID', 'bridge', 'bus', 'carStation', 'cliffBank', 'crashDirec', 'crashFinan', 'crashLocat', 'crashRoadS', 'crashSHDes', 'debris', 'directionR', 'ditch', 'fence', 'flatHill', 'guardRail', 'holiday', 'houseOrBui', 'intersecti', 'kerb', 'light', 'meshblockI', 'moped', 'motorcycle', 'NumberOfLa', 'objectThro', 'otherObjec', 'otherVehic', 'overBank', 'parkedVehi', 'pedestrian', 'phoneBoxEt', 'postOrPole', 'region', 'roadCharac', 'roadLane', 'roadSurfac', 'roadworks', 'schoolBus', 'seriousInj', 'slipOrFloo', 'strayAnima', 'streetLigh', 'suv', 'taxi', 'temporaryS', 'tlaId', 'tlaName', 'trafficCon', 'trafficIsl', 'trafficSig', 'train', 'tree', 'truck', 'unknownVeh', 'urban', 'vanOrUtili', 'vehicle', 'waterRiver', 'weatherB' - from the CAS dataset - they are not needed]
2. [Drop columns 'IDENTIFIER', 'ROUTEFUNCT', 'STATUS', 'VEHICLESPE', 'TRAFFICAAD', 'JOURNEYCOR', 'Shape__Len' from the Cycle Facility Network Dataset - they are not needed.]
3. [Read and eproject the CAS dataset from EPSG:2193 (NZTM) to EPSG:4326 for ipyleaflet.]
4. [Repeat the same for the Cycle Facility network data set]
5. [e.g. Aggregate monthly boardings by mode and year.]
6. ...

### 2.3 Limitations

<!-- Every dataset has gaps. Note at least two. -->

- [e.g. Patronage data is monthly, so weekly patterns are not visible.]
- [e.g. The crash dataset does not distinguish cyclists from e-scooter riders.]