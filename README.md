# Python DDS Static Analysis Scripts


## dds_analyze.py

### Dependencies:

#### openpyxl
`pip install openpyxl`

### Overview:
This script will parse through an Admin Console discovery export file and create an  
XMLS spreadsheet with aggregated devices/participants/endpoints/topics.
It will also create an analysis tab that provides high level insigth into DDS Topics/Endpoints

### Usage

`python dds_analyze.py ./adminconsole.xml`


## dds_analyze_v3.py

### Dependencies:

#### pandas
`pip install pandas`


### Overview: 
This script will parse through an Admin Console discovery export file and output csv files for the following:  
- Participants per domain
- All Devices
- Inconsistent Types
- Mismatch Reliable Readers
- Potential Multicast Readers
- Writers with no Readers
- Readers with no Writers

### Usage

`python dds_analyze_v3.py ./adminconsole.xml`



## dds_capture.py

### Dependencies:

#### Connext Python API
- RTI Connext Python API modules

### Overview:
- Captures all discovered participants (IP address and Name)
- Captures all discovered readers/writers
- Adds related Participant info to readers/writers
- Generates edge "matches" based on Topic and Type name match
- Exports all to csv's.

### Usage:

`python dds_capture.py`

Let run for a few minutes. CTRL-C will stop capture and export entities discovered

