# Python3 client API for ConsurfDB 

[![https img shields io pypi v consurfdb client api logo python](https://img.shields.io/pypi/v/ConsurfDB-client-API?logo=python)](https://pypi.org/project/ConsurfDB-client-API)
[![https img shields io pypi pyversions consurfdb client api logo python](https://img.shields.io/pypi/pyversions/ConsurfDB-client-API?logo=python)](https://pypi.org/project/ConsurfDB-client-API)
[![https img shields io pypi wheel consurfdb client api logo python](https://img.shields.io/pypi/wheel/ConsurfDB-client-API?logo=python)](https://pypi.org/project/ConsurfDB-client-API)
[![https img shields io pypi format consurfdb client api logo python](https://img.shields.io/pypi/format/ConsurfDB-client-API?logo=python)](https://pypi.org/project/ConsurfDB-client-API)
[![https img shields io pypi status consurfdb client api logo python](https://img.shields.io/pypi/status/ConsurfDB-client-API?logo=python)](https://pypi.org/project/ConsurfDB-client-API)

[![https img shields io codeclimate maintainability matteoferla ConsurfDB client API logo codeclimate](https://img.shields.io/codeclimate/maintainability/matteoferla/ConsurfDB-client-API?logo=codeclimate)](https://codeclimate.com/github/matteoferla/ConsurfDB-client-API)
[![https img shields io codeclimate issues matteoferla ConsurfDB client API logo codeclimate](https://img.shields.io/codeclimate/issues/matteoferla/ConsurfDB-client-API?logo=codeclimate)](https://codeclimate.com/github/matteoferla/ConsurfDB-client-API)
[![https img shields io codeclimate tech debt matteoferla ConsurfDB client API logo codeclimate](https://img.shields.io/codeclimate/tech-debt/matteoferla/ConsurfDB-client-API?logo=codeclimate)](https://codeclimate.com/github/matteoferla/ConsurfDB-client-API)

[![https img shields io github forks matteoferla ConsurfDB client API label Fork style social logo github](https://img.shields.io/github/forks/matteoferla/ConsurfDB-client-API?label=Fork&style=social&logo=github)](https://github.com/matteoferla/ConsurfDB-client-API)
[![https img shields io github stars matteoferla ConsurfDB client API style social logo github](https://img.shields.io/github/stars/matteoferla/ConsurfDB-client-API?style=social&logo=github)](https://github.com/matteoferla/ConsurfDB-client-API)
[![https img shields io github watchers matteoferla ConsurfDB client API label Watch style social logo github](https://img.shields.io/github/watchers/matteoferla/ConsurfDB-client-API?label=Watch&style=social&logo=github)](https://github.com/matteoferla/ConsurfDB-client-API)

[![https img shields io github last commit matteoferla ConsurfDB client API logo github](https://img.shields.io/github/last-commit/matteoferla/ConsurfDB-client-API?logo=github)](https://github.com/matteoferla/ConsurfDB-client-API)
[![https img shields io github license matteoferla ConsurfDB client API logo github](https://img.shields.io/github/license/matteoferla/ConsurfDB-client-API?logo=github)](https://github.com/matteoferla/ConsurfDB-client-API/raw/main/LICENCE)
[![https img shields io github commit activity m matteoferla ConsurfDB client API logo github](https://img.shields.io/github/commit-activity/m/matteoferla/ConsurfDB-client-API?logo=github)](https://github.com/matteoferla/ConsurfDB-client-API)
[![https img shields io github issues matteoferla ConsurfDB client API logo github](https://img.shields.io/github/issues/matteoferla/ConsurfDB-client-API?logo=github)](https://github.com/matteoferla/ConsurfDB-client-API)
[![https img shields io github issues closed matteoferla ConsurfDB client API logo github](https://img.shields.io/github/issues-closed/matteoferla/ConsurfDB-client-API?logo=github)](https://github.com/matteoferla/ConsurfDB-client-API)

[Consurf-DB](https://consurfdb.tau.ac.il/) is a web server developed by the group of Prof. Nir Ben-Tal
which provides PDB structures with the b-factors remapped to residue conservation scores as determined
by their [rate4site](https://www.tau.ac.il/~itaymay/cp/rate4site.html).
[![https img shields io badge doi 10 1002 2Fpro 3779 fcb426](https://img.shields.io/badge/doi-10.1002%2Fpro.3779-fcb426)](https://doi.org/10.1002%2Fpro.3779)

This **unofficial** Python3 module queries this server and performs several operations.

This was formerly a part of the Venus backend ([:octocat: michelanglo-protein](https://github.com/matteoferla/MichelaNGLo-protein-analysis)),
but I (MF) moved it out as it may be useful for others.

PS. Like all APIs, especially the unofficial ones, do not abuse the server...

## Installation

    pip install ConsurfDB-client-API

## Usage

Get and parse consurfDB data.

```python3
from consurfDB import ConsurfDB
cp = ConsurfDB.from_web('1UBQ', 'A')
```
The `grades` file data is in `cp.data` and can be made into a pandas dataframe:
It takes ~1.7 seconds to fetch a grades file off the web.
Do simply ignore the unsafe SSL warning
(changing `ConsurfDB.REQUEST_VERIFY_SETTING` to `True`, will result in failure).

One can also run it from a grades file:

```python3
from consurfDB import ConsurfDB
cp = ConsurfDB.from_filename('grades.txt')
```

Data is in `self.data`, which is a dict of `MET1:A` to dict of values.
See the type dictionary `ResidueDataType` for details.

```python3
from consurfDB import ResidueDataType
help(ResidueDataType)
```

One can make a pandas dataframe from it.

```python3
grades : pd.DataFrame = cp.to_pandas()
```

If a residue appears in SEQPOS but no ATOM records are present, they will be like ``cp.data['___1:A']``.
The key is the ``3LATOM`` field, this is ATOM numbering, while POS is the SEQPOS numbering.
``apply_offset_from_swissmodel`` uses the latter and makes both Uniprot numbering.

Also can add a consurf conservation to a PyRosetta pose in place.

```python3
pose : pyrosetta.Pose = ... # noqa
cp.add_bfactor_to_pose(pose)
```

Or a pymol object

also, if chain number differs, e.g. V in consurf grades file and A in pose:

```python3
cp.remap_chains({'B': 'A'})
```

Likewise with offset.

If the Uniprot id is known, the offset can be taken from Swissmodel

```python3
cp.apply_offset_from_swissmodel(uniprot, code, chain)
```

Potentially support multi-chain operations, but not tested.

```python
cp = ConsurfDB.merge([cp1, cp2, cp3]) # noqa
```

Dump of attributes and methods:

* `Consurf.REQUEST_VERIFY_SETTING`
* `Consurf.ResidueDataType`
* `Consurf.add_bfactor_to_pose`
* `Consurf.add_bfactor_to_pymol`
* `Consurf.add_bfactor_via_pymol`
* `Consurf.align`
* `Consurf.apply_offset_by_alignment`
* `Consurf.apply_offset_from_swissmodel`
* `Consurf.assert_reply`
* `Consurf.fetch`
* `Consurf.from_filename`
* `Consurf.from_web`
* `Consurf.get_color`
* `Consurf.get_conscore`
* `Consurf.get_consurf_chain`
* `Consurf.get_key`
* `Consurf.get_offset_by_alignment`
* `Consurf.get_offset_from_swissmodel`
* `Consurf.get_offset_vector_by_alignment`
* `Consurf.get_residue_chain`
* `Consurf.get_residue_index`
* `Consurf.get_residue_name`
* `Consurf.get_variety`
* `Consurf.keys`
* `Consurf.log`
* `Consurf.merge`
* `Consurf.offset_atom`
* `Consurf.offset_seqpos`
* `Consurf.parse`
* `Consurf.read`
* `Consurf.remap_chains`
* `Consurf.sequence`
* `Consurf.to_pandas`

## Author

This package was written by Matteo Ferla
[![https img shields io badge orcid 0000 0002 5508 4673 a6ce39 logo orcid](https://img.shields.io/badge/orcid-0000--0002--5508--4673-a6ce39?logo=orcid)](https://orcid.org/0000--0002--5508--4673) [![https img shields io badge google scholar gF bp_cAAAAJ success logo googlescholar](https://img.shields.io/badge/google--scholar-gF--bp_cAAAAJ-success?logo=googlescholar)](https://scholar.google.com/citations?user=gF--bp_cAAAAJ&hl=en) [![https img shields io twitter follow matteoferla label Follow logo twitter](https://img.shields.io/twitter/follow/matteoferla?label=Follow&logo=twitter)](https://twitter.com/matteoferla) [![https img shields io stackexchange stackoverflow r 4625475 logo stackoverflow](https://img.shields.io/stackexchange/stackoverflow/r/4625475?logo=stackoverflow)](https://stackoverflow.com/users/4625475) [![https img shields io stackexchange bioinformatics r 6322 logo stackexchange](https://img.shields.io/stackexchange/bioinformatics/r/6322?logo=stackexchange)](https://bioinformatics.stackexchange.com/users/6322) [![https img shields io badge email gmail informational logo googlemail](https://img.shields.io/badge/email-gmail-informational&logo=googlemail)](https://mailhide.io/e/Ey3RNO2G) [![https img shields io badge email Oxford informational logo googlemail](https://img.shields.io/badge/email-Oxford-informational&logo=googlemail)](https://mailhide.io/e/Y1dbgyyE) |
