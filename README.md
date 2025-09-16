# Python DDS Example Scripts


- Admin Console Discovery Export XML analysis to Excel file [ddsanalyze](#dds_analyzepy)
- Admin Console Discovery Export XML csv export of DDS entities using Pandas [ddsanalyzev3](#dds_analyze_v3py)
- Live DDS system capture of endpoints and export to CSV for analysis [ddscapture](#dds_capturepy)
- Live DDS System terminal UI to discover endpoints and subscribe for debugging [ddspy](#dds_spypy)


*Tested with Python 3.8.10*


## dds_analyze.py

### Dependencies:
- RTI Python API
- OpenPyXL

#### Connext Python API
- [RTI Connext Python API modules](#https://community.rti.com/static/documentation/connext-dds/current/doc/manuals/connext_dds_professional/installation_guide/installing.html#installing-python-c-or-ada-packages)

#### OpenPyXL
`pip install openpyxl`

### Overview:
This script will parse through an Admin Console discovery export file and create an  
XMLS spreadsheet with aggregated devices/participants/endpoints/topics.
It will also create an analysis tab that provides high level insight into DDS Topics/Endpoints

### Usage

`python dds_analyze.py ./adminconsole.xml`


## dds_analyze_v3.py

### Dependencies:
- RTI Python API
- Pandas

#### Connext Python API
- [RTI Connext Python API modules](https://community.rti.com/static/documentation/connext-dds/current/doc/manuals/connext_dds_professional/installation_guide/installing.html#installing-python-c-or-ada-packages)

#### Pandas
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
- RTI Python API


#### Connext Python API
- [RTI Connext Python API modules](https://community.rti.com/static/documentation/connext-dds/current/doc/manuals/connext_dds_professional/installation_guide/installing.html#installing-python-c-or-ada-packages)

### Overview:
- Captures all discovered participants (IP address and Name)
- Captures all discovered readers/writers
- Adds related Participant info to readers/writers
- Generates edge "matches" based on Topic and Type name match
- Exports all to csv's.

### Usage:

`python dds_capture.py`

Let run for a few minutes. CTRL-C will stop capture and export entities discovered


## dds_spy.py

### Dependencies:
- RTI Python API
- Textual

#### Connext Python API
- [RTI Connext Python API modules](https://community.rti.com/static/documentation/connext-dds/current/doc/manuals/connext_dds_professional/installation_guide/installing.html#installing-python-c-or-ada-packages)

### Textual
`pip install textual textual-dev`

### Overview
Example tool to deploy onto systems for use in integration debugging without a license  
as it uses the Python libraries.

Implements a terminal based UI navigation to allow for headless/ssh use cases.


### Usage:
`python rtispy.py --domain 1`
