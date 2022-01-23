import sys
from typing import Tuple

if sys.version_info < (3, 8):
    from typing_extensions import TypedDict
else:
    from typing import TypedDict

ResidueDataType = TypedDict('ResidueDataType',
                            {'POS':                 int,
                             'SEQ':                 str,
                             '3LATOM':              str,
                             'SCORE':               float,
                             'COLOR':               int,
                             'CONFIDENCE INTERVAL': Tuple[float, float],
                             'CONFIDENCE COLORS':   Tuple[int, int],
                             'MSA DATA':            str,
                             'RESIDUE VARIETY':     str,
                             })

ResidueDataType.__doc__ = '''the value in `.data` is a `Dict[str, ResidueDataType]`

'MET1:A': {   'POS': '1',
              'SEQ': 'M',
              '3LATOM': 'MET1:A',
              'SCORE': '-1.610',
              'COLOR': '9',
              'CONFIDENCE INTERVAL': '-1.838,-1.537',
              'CONFIDENCE COLORS': '9,9',
              'MSA DATA': '94/300',
              'RESIDUE VARIETY': 'M,L,V,I'
           }
'''
