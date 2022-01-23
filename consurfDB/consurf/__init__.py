from consurfDB.consurf.extras import ConExtra

# ## __mro__:
# (consurfDB.consurf.ConsurfDB,
#  consurfDB.consurf.extras.ConExtra,
#  consurfDB.consurf.alt.ConAlt,
#  consurfDB.consurf.base.ConBase,
#  object)


class ConsurfDB(ConExtra):
    """
    Get and parse consurf data.
    It takes 1.7 seconds to fetch a grades file off the web.
    I do not know 100% if this is within the T&Cs of Consurf, but I believe it is.
    It definitely isnt if commercial use though.

    Either from web

    >>> cp = ConsurfDB.from_web('1UBQ', 'A')

    or filename

    >>> cp = ConsurfDB.from_filename('grades.txt')

    Data is in self.data (dict of ``MET1:A`` to dict of values (see ``ConsurfDB.keys`` class attribute))
    and can be converted to pandas:

    >>> cp = ConsurfDB.from_web('1UBQ', 'A')
    >>> cp.to_pandas()

    If a residue appears in SEQPOS but no ATOM records are present, they will be like ``cp.data['___1:A']``.
    The key is the ``3LATOM`` field, this is ATOM numbering, while POS is the SEQPOS numbering.
    ``apply_offset_from_swissmodel`` uses the latter and makes both Uniprot numbering.

    Also can add a consurf conservation to a PyRosetta pose in place.

    >>> pose : pyrosetta.Pose = ... # noqa
    >>> cp.add_bfactor_to_pose(pose)

    Or a pymol object

    also, if chain number differs, e.g. V in consurf grades file and A in pose:

    >>> cp.remap_chains({'B': 'A'})

    Likewise with offset.

    If the Uniprot id is known, the offset can be taken from Swissmodel

    >>> cp.apply_offset_from_swissmodel(uniprot, code, chain) # noqa

    Potentially support multi-chain operations, but not tested.

    >>> cp = ConsurfDB.merge([cp1, cp2, cp3]) # noqa

    """
