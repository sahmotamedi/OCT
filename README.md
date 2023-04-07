### Optical Coherence Tomography .vol Format

A library to work (e.g. read, write) with optical coherence tomography .vol raw files from Heidelberg Engineering Spectralis device.

For more information please refer to docstrings in the modules. 

For other file formats from different OCT manufacturers there is an excellent package written by Mark Graham from King's College London [PyPi](https://pypi.org/project/oct-converter/)

The _open_vol method of the OCTVol class was extensively tested for different types of OCT vol files but unfortunately were not implemented in a structured test file.

### Requirements
python &geq; 3.7
numpy
datetime
os
copy
glob
pytest

### Usage
from OCT.formats.OCTVol import OCTVol <br />
oct_vol = OCTVol("/path/to/your/vol/file")

### Contact
Please contact Amir Motamedi (seyedamirhosein.motamedi(at)charite.de) for any inquires about this software.

### License
Please read LICENSE.txt.