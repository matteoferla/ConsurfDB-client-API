# Python3 client API for ConsurfDB 
[Consurf-DB](https://consurfdb.tau.ac.il/) is a web server developed by the group of Prof. Nir Ben-Tal
which provides PDB structures with the b-factors remapped to residue conservation scores as determined
by their [rate4site](https://www.tau.ac.il/~itaymay/cp/rate4site.html).

This **unofficial** Python3 module queries this server and performs several operations.

This was formerly a part of the Venus backend ([:octocat: michelanglo-protein](https://github.com/matteoferla/MichelaNGLo-protein-analysis)),
but I (MF) moved it out as it may be useful for others.

PS. Like all APIs, especially the unofficial ones, do not abuse the server...

## Usage

```python3
from consurfDB import ConsurfDB
cp = ConsurfDB.from_web('1UBQ', 'A')
```
The `grades` file data is in `cp.data` and can be made into a pandas dataframe:

```python3
import pandas as pd
grades :pd.DataFrame = cp.to_pandas()
```