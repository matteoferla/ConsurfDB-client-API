from __future__ import annotations
from collections import Counter
from typing import *

if TYPE_CHECKING:
    import pandas as pd
    import pyrosetta

from .alt import ConAlt
import warnings


class ConExtra(ConAlt):

    # ----- inner methods: getters ---------

    def get_conscore(self, key) -> float:
        """
        Key is the ATOM resn resi : Chain
        """
        if key in self.data:
            return float(self.data[key]['SCORE'])
        else:
            return float('nan')

    def get_residue_chain(self, res: str) -> str:  # noqa
        return res[-1]

    def get_residue_name(self, res: str) -> str: # noqa
        return res[:3]

    def get_residue_index(self, res: str) -> int: # noqa
        return int(res[3:-2])

    def get_color(self, res: str) -> float: # noqa
        """
        COLOR is an integer... A wee more resolution can be had with confidence range
        """
        conf_colors = self.data[res]['CONFIDENCE COLORS']
        if isinstance(conf_colors, str):  # self.data was not run through parse!
            warnings.warn('Please use `.parse` for `.data`')
            return sum(map(int, conf_colors.strip().split(','))) / 2
        else:
            return sum(conf_colors) / 2

    def get_key(self, index: int, chain: Optional[str] = None) -> str:
        for entry in self.data:
            if int(index) != self.get_residue_index(entry):
                continue
            elif chain is None or chain == self.get_residue_chain(entry):
                return entry
            else:
                continue
        else:
            raise ValueError(f'Absent {index}:{chain}')

    def get_variety(self, res: str) -> List[str]:
        return self.data[res]['RESIDUE VARIETY'].split(',')

    # ----- inner methods: utils ---------

    def to_pandas(self) -> pd.DataFrame:
        import pandas as pd  # noqa not shadowing. That's typehint checking only
        return pd.DataFrame(self.data).transpose()

    def add_bfactor_to_pose(self, pose: pyrosetta.Pose, strict: bool = True):
        """
        Adds the conscores dictionary to bfactor in place.

        If ``strict`` is True, an error is raised if a residue mismatches.
        """
        pdb_info = pose.pdb_info()
        assert not pdb_info.obsolete(), 'The pdb_info is obsolete'
        pdb2pose = pdb_info.pdb2pose
        for con_res in self.data:
            chain = self.get_residue_chain(con_res)
            resi = self.get_residue_index(con_res)
            resn = self.get_residue_name(con_res)
            pose_res = pdb2pose(res=resi, chain=chain)
            if pose_res == 0:
                continue
            residue = pose.residue(pose_res)
            if strict:
                assert residue.name3() == resn, f'{residue.name3()} ≠ {resn}'
            for i in range(residue.natoms()):
                pdb_info.bfactor(pose_res, i, self.get_conscore(con_res))

    def add_bfactor_to_pymol(self, pymol, add_score: bool = False, missing: float = 1.):
        """
        pymol is a pymol2.PyMOL object.

        >>> with pymol2.PyMOL() as pymol: # noqa
        >>>     pymol.cmd.fetch('3CMD', 'model')
        >>>     cp.offset_pymol() # noqa
        >>>     pymol.cmd.save('test.pse')

        ``add_score`` True adds the score (zero centered), else the 10-1 color
        """
        pymol.cmd.alter(f'*', f'b={missing}')
        for key, values in self.data.items():  #: Tuple[str, ResidueDataType]
            resi = self.get_residue_index(key)
            chain = self.get_residue_chain(key)
            # COLOR is an integer... A wee more resolution can be had with confidence range
            # hence `.get_color`

            # 9 is conserved 1 is not.
            if add_score:
                anticolor: float = self.get_conscore(key)
            else:
                # 9 is conserved 1 is not.
                anticolor: float = 10 - self.get_color(key)
            pymol.cmd.alter(f'resi {resi} and chain {chain}', f'b={anticolor}')
        pymol.cmd.sort()

    def add_bfactor_via_pymol(self, coordinates: str, add_score: bool = False):
        import pymol2
        with pymol2.PyMOL() as pymol:
            pymol.cmd.read_pdbstr(coordinates, 'model')
            self.add_bfactor_to_pymol(pymol, add_score=add_score)
            return pymol.cmd.get_pdbstr()

    # ---- offset correction

    def remap_chains(self, chain_map: Dict[str, str]) -> None:
        """
        Say conscores is chain A based, but the model is not.
        """
        new_data = {}
        for res, values in list(self.data.items()):
            old_chain = self.get_residue_chain(res)
            if old_chain in chain_map:
                new_name = res[:-2] + ':' + chain_map[old_chain]
                new_data[new_name] = values
            else:
                new_data[res] = values
        if self.present_chain in chain_map:
            self.present_chain = chain_map[self.present_chain]
        self.data = new_data

    def get_consurf_chain(self) -> str:
        # corrects self.present_chain
        chains = [self.get_residue_chain(res) for res in self.data]
        self.present_chain = Counter(chains).most_common(1)[0][0]
        return self.present_chain

    def offset_atom(self, offset_map: Dict[str, int]) -> None:
        """
        offset the index (the ATOM record numbering)
        """
        new_data = {}
        for res, values in list(self.data.items()):
            chain = self.get_residue_chain(res)
            resi = self.get_residue_index(res)
            resn = self.get_residue_name(res)
            if chain in offset_map:
                offset = offset_map[chain]
                new_name = f'{resn}{resi + offset}:{chain}'
                new_data[new_name] = values
            else:
                new_data[res] = values
        self.data = new_data

    def offset_seqpos(self, offset_map: Dict[str, Union[int, List[int]]]) -> None:
        """
        Offset the index (the SEQPOS record numbering and use that.
        """
        new_data = {}
        for ri, (res, values) in enumerate(list(self.data.items())):
            chain = self.get_residue_chain(res)
            # resi = self.get_residue_index(res)
            resn = self.get_residue_name(res)
            if chain in offset_map:
                if isinstance(offset_map[chain], int):
                    offset = offset_map[chain]
                elif isinstance(offset_map[chain], list):
                    offset = offset_map[chain][ri]
                else:
                    raise TypeError
                if isinstance(values['POS'], str):
                    values['POS'] = int(values['POS'].strip())
                if offset is None:
                    continue
                new_resi = values['POS'] + offset
                if new_resi < 1:
                    continue
                values['POS'] = new_resi
                new_name = f'{resn}{new_resi}:{chain}'
                new_data[new_name] = values
            else:
                new_data[res] = values
        self.data = new_data

    def get_offset_from_swissmodel(self, uniprot, code, chain) -> int:
        """
        Swissmodel has the offset from the SEQPOS, SIFTS from the ATOM,
        but if there is no ATOM, it is none, so this is safe.
        """
        sm_data = self.req_session.get(f'https://swissmodel.expasy.org/repository/uniprot/{uniprot}.json').json()
        segs_data = [structure['chains'] for structure in sm_data['result']['structures'] if
                     structure['template'].upper() == code]
        chain_data = [seg for seg in segs_data[0] if seg['id'] == chain][0]['segments'][0]
        pdb_from = chain_data['pdb']['from']
        uniprot_from = chain_data['uniprot']['from']
        return uniprot_from - pdb_from

    def apply_offset_from_swissmodel(self, uniprot, code, chain) -> int:
        offset = self.get_offset_from_swissmodel(uniprot, code, chain)
        self.offset_seqpos({chain: offset})
        return offset

    @property
    def sequence(self):
        return ''.join(row['SEQ'].strip() for row in self.data.values())

    def align(self, ref_sequence: str) -> Tuple[str, str]:
        from Bio import pairwise2
        # alignment = pairwise2.align.globalxx(ref_sequence, data_sequence)[0]
        # 3 sequential mismatches make a gap favourable:
        alignment = pairwise2.align.globalms(ref_sequence, self.sequence,
                                             2,  # match
                                             -.5,  # mismatch
                                             -1,  # open
                                             0  # extend
                                             )[0]
        ref_al, con_al, _, _, _ = alignment
        self.log.debug('ref al ' + ref_al)
        self.log.debug('con al ' + con_al)
        return ref_al, con_al

    def get_offset_by_alignment(self, ref_sequence: str) -> int:
        """
        Offset iteger determined by alignment (SEQPOS sequence)
        Assumed there are no internal gaps in the sequence only at the N-terminus

        cf. get_offset_vector_by_alignment for -> List[int]
        """
        warnings.warn('Use get_offset_vector_by_alignment', category=DeprecationWarning)
        ref_al, con_al = self.align(ref_sequence)
        offset = 0
        for r, c in zip(ref_al, con_al):
            if r == '-':
                offset += 1  # number added to con numbering.
            elif c == '-':
                offset -= 1  # number added to con numbering.
            else:
                break
        return -offset

    def get_offset_vector_by_alignment(self, ref_sequence: str) -> List[int]:
        """
        Offset list determined by alignment (SEQPOS sequence)
        cf. get_offset_by_alignment for -> int
        """
        ref_al, con_al = self.align(ref_sequence)
        c2r = []
        ri = 0
        for r, c in zip(ref_al, con_al):
            if c == '-' and r == '-':
                raise ValueError('Impossible at ``get_offset_map_by_alignment``')
            elif c != '-' and r != '-':
                c2r.append(ri)
                ri += 1
            elif c != '-' and r == '-':
                c2r.append(None)  # no match.
            elif c == '-' and r != '-':
                ri += 1  # no match for R.
        return [ri - ci if ri is not None else None for ci, ri in enumerate(c2r)]

    def apply_offset_by_alignment(self, ref_sequence: str, chain: Optional[str] = None) -> List[int]:
        if chain is None:
            chain = self.present_chain
        offset_vector: List[int] = self.get_offset_vector_by_alignment(ref_sequence)
        self.log.debug(f'offset vector {offset_vector}')
        self.offset_seqpos({chain: offset_vector})
        return offset_vector
