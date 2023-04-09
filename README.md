### Optical Coherence Tomography .vol Format

This library provides a set of tools to work with optical coherence tomography .vol raw files from Heidelberg Engineering Spectralis devices, such as reading and writing.

Please refer to the docstrings in the modules for more information.

For working with other file formats from different OCT manufacturers, we recommend the excellent [PyPi](https://pypi.org/project/oct-converter/) package written by Mark Graham from King's College London.

Note that the `_open_vol` method of the `OCTVol` class was extensively tested for different types of OCT vol files but unfortunately was not implemented in a structured test file.

### Requirements
To use this library, you will need the following:

- python &geq; 3.7
- numpy
- pytest

### Usage
To use the `OCTVol` class, simply import it and create an instance of it, providing the path to your vol file as an argument, like so:

```python
from OCT.formats.OCTVol import OCTVol
oct_vol = OCTVol("/path/to/your/vol/file")
```

### Contact
If you have any questions or inquiries about this software, please contact Amir Motamedi at seyedamirhosein.motamedi(at)charite.de.

### License
Please refer to the `LICENSE.txt` file for licensing information.
