# Python DDS Static Analysis Scripts


## dds_analyze.py

### Dependencies:

#### openpyxl
`pip install openpyxl`

This script will parse through an Admin Console discovery export file and create an  
XMLS spreadsheet with aggregated devices/participants/endpoints/topics.
It will also create an analysis tab that provides high level insigth into DDS Topics/Endpoints

### Example

`python dds_analyze.py ./adminconsole.xml`


## dds_analyze_v3.py

### Dependencies:

#### pandas
`pip install pandas`

This script will parse through an Admin Console discovery export file and output csv files for the following:  
- Participants per domain
- All Devices
- Inconsistent Types
- Mismatch Reliable Readers
- Potential Multicast Readers
- Writers with no Readers
- Readers with no Writers

### Example

`python dds_analyze_v3.py ./adminconsole.xml`