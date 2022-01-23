from ..residue_type import ResidueDataType

import warnings
from typing import *
import re
import logging
import requests



class ConBase:
    log = logging.getLogger()

    # ----- init methods ---------

    REQUEST_VERIFY_SETTING = False  # False for now, but may be a risk of attack
    ResidueDataType = ResidueDataType
    keys: List[str] = list(ResidueDataType.__annotations__.keys())

    def __init__(self):
        self.req_session = requests.session()
        self.grades_block = ''
        self.data: Dict[str, ResidueDataType] = {}
        self.present_chain = 'A'  # fallback
        self.code = None


    # ----- inner methods: parse ---------

    def parse(self) -> Dict[str, ResidueDataType]:
        """
        parses a grades block and fills self.conscores
        """
        data: Dict[str, ResidueDataType] = {}
        assert len(self.grades_block), 'self.grades_block is empty'
        for row in self.grades_block.split('\n'):
            row = row.strip()
            # if pos is not a number it is not a row.
            if not len(row) or not row[0].isdigit():
                continue
            parts = dict(zip(self.keys, [v.strip() for v in row.split('\t') if len(v)]))
            name = parts['3LATOM'].strip()
            if name == '-':
                # missing density
                # note: uses fallback present_chain
                name = '___' + parts['POS'] + ':' + self.present_chain
            else:
                self.present_chain = name[-1]
            unstar = lambda value: value.replace('*', '') if isinstance(value, str) else value
            for key, anno_type in ResidueDataType.__annotations__.items():
                if key not in parts:
                    warnings.warn(f'{key} not in residue information of {name}')
                elif not hasattr(anno_type, '_name'):  # standard library
                    parts[key] = anno_type(unstar(parts[key])) if parts[key] else anno_type()
                elif anno_type._name == 'Tuple':  # its a typing.Tuple
                    subparts: List[str] = unstar(parts[key]).split(',')
                    subtypes: Tuple[type] = anno_type.__args__
                    parts[key] = tuple([subtype(subpart) for subtype, subpart in zip(subtypes, subparts)])
                else:
                    raise NotImplementedError('Dev changed TypedDict!')
            data[name] = ResidueDataType(parts)  # noqa
        return data

    # ----- dependent methods: web

    def fetch(self, code: str, chain: str) -> None:
        """Uses https://consurfdb.tau.ac.il/ so make sure you fall within its usage."""
        first = self._fetch_initial(code, chain)
        self.code = first
        self.grades_block = self._fetch_final(first)
        self.data: Dict[str, ResidueDataType] = self.parse()

    def _fetch_initial(self, code: str, chain: str) -> str:
        reply = self.req_session.get('https://consurfdb.tau.ac.il/scripts/chain_selection.php',
                                     params=dict(pdb_ID=code.upper()),
                                     verify=self.REQUEST_VERIFY_SETTING)
        self.assert_reply(reply, msg=f'matching {code}')
        mapping = dict(re.findall('option value="(\w) (\w{5})"', reply.text))
        if 'No chains found for' in reply.text:
            self.log.debug(f'Reply: {reply.text.strip()}')
            raise KeyError(f'The PDB {code} has no chains according to Consurf')
        elif len(mapping) == 1:
            return list(mapping.values())[0]
        elif chain not in mapping:
            self.log.debug(f'Reply: {reply.text.strip()}')
            raise KeyError(f'Chain {chain} is absent in {code} according to Consurf (SMTL changed the chain number)')
        else:
            return mapping[chain]

    def _fetch_final(self, final: str):
        url = f'https://consurfdb.tau.ac.il/DB/{final}/consurf_summary.txt'
        reply = self.req_session.get(url, verify=self.REQUEST_VERIFY_SETTING)
        self.assert_reply(reply, msg=f'retrieval of suggestion {final}')
        return reply.text

    def assert_reply(self, reply: requests.Response, msg: str) -> None:
        """
        A slightly more elegant `requests.raise_for_status`.
        The reason being there is some connectivity issues.
        """
        if 'The requested URL was rejected' in reply.text:
            requests.exceptions.ConnectionError(
                f'{msg} gave an error code 200 with Consurf.',
                request=reply.req_session,
                response=reply)
        if reply.status_code == 200:
            pass
        elif reply.status_code == 404:
            raise requests.exceptions.InvalidURL(f'{msg} could not be found in Consurf',
                                                 request=reply.req_session, # noqa ---it's a session response object
                                                 response=reply)
        else:
            raise requests.exceptions.ConnectionError(
                f'{msg} gave a code {reply.status_code} with Consurf ({reply.text})',
                request=reply.req_session,  # noqa ---it's a session response object
                response=reply)

    # ----- dependent methods: file

    def read(self, grades_filename: str) -> None:
        with open(grades_filename) as r:
            self.grades_block = r.read()
        self.data: Dict[str, ResidueDataType] = self.parse()
