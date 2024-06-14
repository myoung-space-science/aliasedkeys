import operator
import typing
import itertools

import pytest

import aliasedkeys


def test_set():
    """Test the object that represents a set-like group of aliases."""
    assert len(aliasedkeys.Set('t0')) == 1
    assert len(aliasedkeys.Set(('t0', 't1', 't2'))) == 3
    assert len(aliasedkeys.Set(['t0', 't1', 't2'])) == 3
    assert len(aliasedkeys.Set({'t0', 't1', 't2'})) == 3
    assert len(aliasedkeys.Set('t0', 't1', 't2')) == 3
    key = aliasedkeys.Set('t0', 't1', 't2')
    assert key | 't3' == aliasedkeys.Set('t0', 't1', 't2', 't3')
    assert key - 't2' == aliasedkeys.Set('t0', 't1')
    assert aliasedkeys.Set('a', 'b') == aliasedkeys.Set('b', 'a')
    assert aliasedkeys.Set('')
    with pytest.raises(TypeError):
        aliasedkeys.Set()
    assert key == ('t0', 't1', 't2')
    assert key == ['t0', 't1', 't2']
    assert aliasedkeys.Set('2') == '2'
    assert aliasedkeys.Set(2) == 2


def test_setmap():
    """Test the collection that groups aliases."""
    init = [('a', 'A'), 'b', ['c', 'C'], ['d0', 'd1', 'd2']]
    setmap = aliasedkeys.SetMap(*init)
    test = {
        'a': aliasedkeys.Set('a', 'A'),
        'A': aliasedkeys.Set('a', 'A'),
        'b': aliasedkeys.Set('b'),
        'c': aliasedkeys.Set('c', 'C'),
        'C': aliasedkeys.Set('c', 'C'),
        'd0': aliasedkeys.Set('d0', 'd1', 'd2'),
        'd1': aliasedkeys.Set('d0', 'd1', 'd2'),
        'd2': aliasedkeys.Set('d0', 'd1', 'd2'),
    }
    for key, value in test.items():
        assert setmap.get(key) == value
        assert setmap[key] == value
    assert setmap.get('B') is None
    with pytest.raises(KeyError):
        setmap['B']


def test_setmap_set_operations():
    """Test set operations on aliased key sets."""
    # Create the test sets.
    a, b, c, d = {('a', 'A')}, {'b'}, {('c', 'C')}, {('d0', 'd1', 'd2')}
    # Define some set unions for convenience.
    abcd = a | b | c | d
    abc = a | b | c
    ab = a | b
    cd = c | d
    ac = a | c
    bd = b | d
    # Arrange the test cases.
    cases = {
        operator.or_: (ab, cd, abcd),
        operator.or_: (ac, bd, abcd),
        operator.and_: (ab, bd, b),
        operator.and_: (ac, cd, c),
        operator.sub : (ab, a, b),
        operator.sub : (abc, b, ac),
    }
    for f, (x, y, r) in cases.items():
        # Create the equivalent instances.
        sx = aliasedkeys.SetMap(*x)
        sy = aliasedkeys.SetMap(*y)
        # Make sure we have the correct set-wise result.
        assert f(x, y) == r
        # Test the setmap-wise operation.
        assert f(sx, sy) == aliasedkeys.SetMap(*r)


def test_setmap_update():
    """Test the ability to update a collection of sets (in-place merge)."""
    original = [('a', 'A'), 'b', ['c', 'C'], ['d0', 'd1', 'd2']]
    modified = {
        ('a', 'A'): ['a', 'A', 'a1'],
        ('b',): None,
        ('c', 'C'): None,
        ('d0', 'd1', 'd2'): None,
    }
    inserted = {
        ('this', 'that'),
    }
    targets = [('a', 'a1'), ['this', 'that']]
    update_setmap(original, modified, inserted, *targets)
    update_setmap(original, modified, inserted, aliasedkeys.SetMap(*targets))


def update_setmap(
    original,
    modified: typing.Dict[tuple, typing.Optional[list]],
    inserted: typing.Set[tuple],
    *others,
) -> None:
    """Helper for testing `aliasedkeys.Sets.update`."""
    setmap = aliasedkeys.SetMap(*original)
    setmap.update(*others)
    for old, new in modified.items():
        keys = new or old
        for key in keys:
            assert setmap.get(key) == aliasedkeys.Set(*keys)
    for keys in inserted:
        for key in keys:
            assert setmap.get(key) == aliasedkeys.Set(*keys)


def test_setmap_merge():
    """Test the ability to create a merged collection of key sets."""
    original = [('a', 'A'), 'b', ['c', 'C'], ['d0', 'd1', 'd2']]
    modified = {
        ('a', 'A'): ['a', 'A', 'a1'],
        ('b',): None,
        ('c', 'C'): None,
        ('d0', 'd1', 'd2'): None,
    }
    inserted = {
        ('this', 'that'),
    }
    targets = [('a', 'a1'), ['this', 'that']]
    merge_setmap(original, modified, inserted, *targets)
    merge_setmap(original, modified, inserted, aliasedkeys.SetMap(*targets))


def merge_setmap(
    original,
    modified: typing.Dict[tuple, typing.Optional[list]],
    inserted: typing.Set[tuple],
    *others,
) -> None:
    """Helper for testing `aliasedkeys.Sets.merge`."""
    setmap = aliasedkeys.SetMap(*original)
    merged = setmap.merge(*others)
    for old, new in modified.items():
        keys = new or old
        for key in keys:
            assert merged.get(key) == aliasedkeys.Set(*keys)
        for key in old:
            assert setmap.get(key) == aliasedkeys.Set(*old)
    for keys in inserted:
        assert all(key not in setmap for key in keys)


def test_setmap_without():
    """Test the ability to exclude key sets from a collection."""
    init = [('a', 'A'), 'b', ['c', 'C'], ['d0', 'd1', 'd2']]
    setmap = aliasedkeys.SetMap(*init)
    splits = {
        'a': ['b', ('c', 'C'), ('d0', 'd1', 'd2')],
        ('a', 'd1'): ['b', ('c', 'C')],
        ('d1', 'a'): ['b', ('c', 'C')],
        (aliasedkeys.Set('c', 'C'), 'd0'): [('a', 'A'), 'b'],
        (aliasedkeys.Set('C'), 'd0'): [('a', 'A'), 'b', ('c', 'C')],
        ('T', 'd0'): [('a', 'A'), 'b', ('c', 'C')],
    }
    for r, k in splits.items():
        assert setmap.without(*r) == aliasedkeys.SetMap(*k)


def test_mapping():
    """Test the object that represents a mapping with aliased keys."""
    # Set up mappings.
    _standard = {
        'this': 1,
        'that': 2,
        'the other': 3,
    }
    _basic = {
        ('this', 'first'): 1,
        ('that', 'second'): 2,
        ('the other', 'third'): 3,
    }
    _mixed = {
        'this': 1,
        ('that', 'second'): 2,
        ('the other',): 3,
    }
    standard = aliasedkeys.Mapping(_standard)
    basic = aliasedkeys.Mapping(_basic)
    mixed = aliasedkeys.Mapping(_mixed)

    # Use the common keys to check values.
    for key, value in standard.items():
        assert value == basic[key]
        assert value == mixed[key]

    # Check values by using aliases where they exist.
    for keys in _basic:
        assert standard[keys[0]] == basic[keys[1]]
        assert keys[1] not in standard
        assert mixed[keys[0]] == basic[keys[1]]

    # Test aliased-key look-up.
    for key, value in basic.items(aliased=True):
        assert basic[key] == value

    # Containment checks should support strings and aliased keys.
    assert 'the other' in mixed and ('the other',) not in mixed
    assert aliasedkeys.Set('that', 'second') in mixed

    # Check lengths of keys, values, and items.
    for mapping, n_keys in zip([standard, basic, mixed], [3, 6, 4]):
        _check_aliased_keys(mapping, n_keys)

    # Key lists should be flat lists of strings.
    assert sorted(standard) == sorted(['this', 'that', 'the other'])
    assert sorted(basic) == sorted([
        'this', 'first', 'that', 'second', 'the other', 'third'
    ])
    assert sorted(mixed) == sorted(['this', 'that', 'second', 'the other'])

    # The caller should be able to get the de-aliased mapping.
    dealiased = {
        'this': 1,
        'first': 1,
        'that': 2,
        'second': 2,
        'the other': 3,
        'third': 3,
    }
    assert basic.flat == dealiased

    # The caller should be able to get known aliases but not set them.
    assert mixed.alias('that') == ('second',)
    assert mixed.alias('that', include=True) == ('that', 'second')
    with pytest.raises(TypeError):
        mixed.alias('this', 'THIS')


def _check_aliased_keys(mapping: aliasedkeys.Mapping, n_keys: int):
    """Helper function for `test_mapping`."""
    assert len(mapping) == n_keys
    assert len(mapping.keys()) == n_keys
    assert len(mapping.values()) == n_keys
    assert len(mapping.items()) == n_keys
    assert len(list(mapping.keys(aliased=True))) == 3
    assert len(list(mapping.values(aliased=True))) == 3
    assert len(list(mapping.items(aliased=True))) == 3


def test_repeated_key():
    """Repeating an existing alias in a new key should overwrite the value."""
    mapping = {
        ('a', 'A'): 1,
        ('b', 'B'): 2,
        'b': 3,
    }
    amap = aliasedkeys.Mapping(mapping)
    flat = {
        'a': 1,
        'A': 1,
        'b': 3,
        'B': 3,
    }
    assert sorted(amap) == sorted(flat)
    for key, value in flat.items():
        assert amap[key] == value
    aliased_keys = [
        aliasedkeys.Set('a', 'A'),
        aliasedkeys.Set('b', 'B'),
    ]
    assert sorted(amap.keys(aliased=True)) == aliased_keys


def test_mutable_mapping():
    """Test the mutable version of an aliased mapping."""
    # Set up mappings.
    _basic = {
        ('this', 'first'): 1,
        ('that', 'second'): 2,
        ('the other', 'third'): 3,
    }
    _mixed = {
        'this': 1,
        ('that', 'second'): 2,
        ('the other',): 3,
    }
    basic = aliasedkeys.MutableMapping(_basic)
    mixed = aliasedkeys.MutableMapping(_mixed)

    # Item assignment and updates should apply to all aliases.
    basic['this'] = -10
    assert basic['first'] == -10
    basic.update({'this': 2, 'second': '2nd', 'new': -9.9})
    for key in ('this', 'first'):
        assert basic[key] == 2
    for key in ('that', 'second'):
        assert basic[key] == '2nd'
    assert basic['new'] == -9.9

    # Assigning to a non-existant key should create a new item.
    with pytest.raises(KeyError):
        basic['unused']
    basic['unused'] = 1.234
    assert basic['unused'] == 1.234

    # Removing an item by one alias should remove the value and all aliases.
    del basic['this']
    for key in ('this', 'first'):
        assert key not in basic

    # The caller should be able to register new aliases.
    mixed.alias('this', 'THIS')
    mixed.alias('this', 'a0', 'a1')
    for alias in ('THIS', 'a0', 'a1'):
        assert alias in mixed and mixed['this'] == mixed[alias]

    # Attempting to assign an existing alias should be an error.
    with pytest.raises(KeyError):
        mixed.alias('this', 'that')


def test_mapping_label():
    """Test the ability to assign a single key to multiple values."""
    base = {'a': 1, 'b': 2, 'c': 3}
    mapping = aliasedkeys.MutableMapping(base)
    assert sorted(mapping) == ['a', 'b', 'c']
    mapping.label('G', 'a', 'b')
    assert sorted(mapping) == ['a', 'b', 'c']
    for key, value in mapping.items():
        assert base[key] == value
    assert mapping['a'] == 1
    assert tuple(mapping['G']) == (1, 2)
    assert mapping.label('G') == ('a', 'b')
    with pytest.raises(KeyError):
        mapping.label('H')


def test_immutable_from_mutable():
    """Test creating an immutable aliased mapping from a mutable one."""
    _mapping = {
        ('this', 'first'): 1,
        ('that', 'second'): 2,
        ('the other', 'third'): 3,
    }
    mutable = aliasedkeys.MutableMapping(_mapping)
    immutable = aliasedkeys.Mapping(mutable)
    assert isinstance(immutable, aliasedkeys.Mapping)
    assert not hasattr(immutable, 'update')
    for key, value in mutable.items():
        assert immutable[key] == value
    with pytest.raises(TypeError):
        immutable['this'] = -10
    with pytest.raises(TypeError):
        del immutable['this']


def test_mutable_mapping_freeze():
    """Test the `freeze` method of a mutable aliased mapping."""
    _mapping = {
        ('this', 'first'): 1,
        ('that', 'second'): 2,
        ('the other', 'third'): 3,
    }
    mutable = aliasedkeys.MutableMapping(_mapping)
    immutable = mutable.freeze()
    assert isinstance(immutable, aliasedkeys.Mapping)
    assert not hasattr(immutable, 'update')
    for key, value in mutable.items():
        assert immutable[key] == value
    with pytest.raises(TypeError):
        immutable['this'] = -10
    with pytest.raises(TypeError):
        del immutable['this']
    mutable.label('G', 'this', 'that')
    grouped = mutable.freeze(groups=True)
    for key, value in mutable.items():
        assert grouped[key] == value
    assert grouped['G'] == (1, 2)


def test_mapping_idempotence():
    """Make sure we can create an aliased mapping from an aliased mapping."""
    user = {
        ('this', 'first'): 1,
        ('that', 'second'): 2,
        ('the other', 'third'): 3,
    }
    original = aliasedkeys.Mapping(user)
    from_aliased = aliasedkeys.Mapping(original)
    assert from_aliased == original
    for key in original:
        assert original.alias(key) == from_aliased.alias(key)
    from_aliased = aliasedkeys.Mapping(original)
    assert from_aliased == original
    from_aliased = aliasedkeys.Mapping.fromkeys(original)
    assert from_aliased.keys() == original.keys()


def test_declared_aliases():
    """Initialize an instance with explicit aliases."""
    this = {
        'a': {'aliases': ('A', 'a0'), 'name': 'Annabez', 'k': ['Ka']},
        'b': {'aliases': 'B', 'name': 'Borb', 'k': ('Kb', 'KB')},
        'C': {'aliases': ('c',), 'name': 'Chrunk'}
    }
    mapping = aliasedkeys.Mapping(this)
    expected = {
        'a': {'name': 'Annabez', 'k': ['Ka']},
        'A': {'name': 'Annabez', 'k': ['Ka']},
        'a0': {'name': 'Annabez', 'k': ['Ka']},
        'b': {'name': 'Borb', 'k': ('Kb', 'KB')},
        'B': {'name': 'Borb', 'k': ('Kb', 'KB')},
        'C': {'name': 'Chrunk'},
        'c': {'name': 'Chrunk'},
    }
    assert mapping.flat == expected
    mapping = aliasedkeys.Mapping(this, aliases='k')
    expected = {
        'a': {'name': 'Annabez', 'aliases': ('A', 'a0')},
        'Ka': {'name': 'Annabez', 'aliases': ('A', 'a0')},
        'b': {'name': 'Borb', 'aliases': 'B'},
        'Kb': {'name': 'Borb', 'aliases': 'B'},
        'KB': {'name': 'Borb', 'aliases': 'B'},
        'C': {'name': 'Chrunk', 'aliases': ('c',)},
    }
    assert mapping.flat == expected


def test_mapping_squeeze():
    """Test the option to reduce singleton inner mappings to values."""
    this = {
        'a': {'aliases': ('A', 'a0'), 'name': 'Annabez'},
        'b': {'aliases': 'B', 'nombre': 'Borb'},
        'C': {'aliases': ('c',), 'name': 'Chrunk'}
    }
    mapping = aliasedkeys.Mapping(this)
    expected = {
        'a': {'name': 'Annabez'},
        'A': {'name': 'Annabez'},
        'a0': {'name': 'Annabez'},
        'b': {'nombre': 'Borb'},
        'B': {'nombre': 'Borb'},
        'C': {'name': 'Chrunk'},
        'c': {'name': 'Chrunk'},
    }
    assert mapping.flat == expected
    squeezed = mapping.copy().squeeze()
    expected = {
        'a': 'Annabez',
        'A': 'Annabez',
        'a0': 'Annabez',
        'b': 'Borb',
        'B': 'Borb',
        'C': 'Chrunk',
        'c': 'Chrunk',
    }
    assert squeezed.flat == expected
    with pytest.raises(aliasedkeys.ValuesTypeError):
        mapping.copy().squeeze(strict=True)
    invalid = aliasedkeys.Mapping({'a': {'name': 'Annabez'}, 'b': 1})
    with pytest.raises(aliasedkeys.ValuesTypeError):
        invalid.squeeze()



def test_mapping_fromkeys():
    """Test the class method that creates an aliased mapping from keys."""
    this = {
        'a': {'aliases': ('A', 'a0'), 'name': 'Annabez', 'k': ['Ka']},
        'b': {'aliases': 'B', 'name': 'Borb', 'k': ('Kb', 'KB')},
        'C': {'aliases': ('c',), 'name': 'Chrunk'},
        'D': {'name': 'Dilk'},
    }
    mapping = aliasedkeys.Mapping.fromkeys(this, key='aliases', value=None)
    expected = {
        'a': None,
        'A': None,
        'a0': None,
        'b': None,
        'B': None,
        'C': None,
        'c': None,
        'D': None,
    }
    assert mapping.flat == expected
    keys = aliasedkeys.SetMap(('a', 'A', 'a0'), ('b', 'B'), ('c', 'C'), 'D')
    mapping = aliasedkeys.Mapping.fromkeys(keys)
    assert mapping.flat == expected
    keys = [('a', 'A', 'a0'), ('b', 'B'), ('c', 'C'), 'D']
    mapping = aliasedkeys.Mapping.fromkeys(keys)
    assert mapping.flat == expected
    mapping = aliasedkeys.Mapping.fromkeys(this, key='aliases', value=-4.5)
    expected = {
        'a': -4.5,
        'A': -4.5,
        'a0': -4.5,
        'b': -4.5,
        'B': -4.5,
        'C': -4.5,
        'c': -4.5,
        'D': -4.5,
    }
    assert mapping.flat == expected


def test_mapping_from_setmap():
    """Initialize an aliased mapping with aliased key sets."""
    init = {
        'a': {'name': 'Annabez', 'k': ['Ka']},
        'b': {'name': 'Borb', 'k': ('Kb', 'KB')},
        'C': {'name': 'Chrunk'},
        'D': {'name': 'Dilk'},
    }
    keymap = aliasedkeys.SetMap(('a', 'A', 'a0'), ('b', 'B'), ('c', 'C'), 'D')
    mapping = aliasedkeys.Mapping(init, aliases=keymap)
    expected = {
        'a': {'name': 'Annabez', 'k': ['Ka']},
        'A': {'name': 'Annabez', 'k': ['Ka']},
        'a0': {'name': 'Annabez', 'k': ['Ka']},
        'b': {'name': 'Borb', 'k': ('Kb', 'KB')},
        'B': {'name': 'Borb', 'k': ('Kb', 'KB')},
        'C': {'name': 'Chrunk'},
        'c': {'name': 'Chrunk'},
        'D': {'name': 'Dilk'},
    }
    assert mapping.flat == expected


def test_mapping_from_mapped_aliases():
    """Initialize an aliased mapping with a mapping of aliases."""
    init = {
        'a': {'name': 'Annabez', 'k': ['Ka']},
        'b': {'name': 'Borb', 'k': ('Kb', 'KB')},
        'C': {'name': 'Chrunk'},
        'D': {'name': 'Dilk'},
    }
    keymap = {
        'a': ['A', 'a0'],
        'b': ['B'],
        'C': ['c'],
    }
    mapping = aliasedkeys.Mapping(init, aliases=keymap)
    expected = {
        'a': {'name': 'Annabez', 'k': ['Ka']},
        'A': {'name': 'Annabez', 'k': ['Ka']},
        'a0': {'name': 'Annabez', 'k': ['Ka']},
        'b': {'name': 'Borb', 'k': ('Kb', 'KB')},
        'B': {'name': 'Borb', 'k': ('Kb', 'KB')},
        'C': {'name': 'Chrunk'},
        'c': {'name': 'Chrunk'},
        'D': {'name': 'Dilk'},
    }
    assert mapping.flat == expected


def test_mapping_as_keymap():
    """Use an aliased mapping as a key map to initialize another mapping."""
    base = {
        'a': {'aliases': ('A', 'a0'), 'name': 'Annabez'},
        'b': {'aliases': 'B', 'name': 'Borb'},
        'C': {'aliases': ('c',), 'name': 'Chrunk'},
        'D': {'name': 'Dilk'},
    }
    keymap = aliasedkeys.Mapping(base)
    init = {
        'a': {'name': 'Annabez', 'k': ['Ka']},
        'b': {'name': 'Borb', 'k': ('Kb', 'KB')},
        'C': {'name': 'Chrunk'},
        'D': {'name': 'Dilk'},
    }
    mapping = aliasedkeys.Mapping(init, aliases=keymap)
    expected = {
        'a': {'name': 'Annabez', 'k': ['Ka']},
        'A': {'name': 'Annabez', 'k': ['Ka']},
        'a0': {'name': 'Annabez', 'k': ['Ka']},
        'b': {'name': 'Borb', 'k': ('Kb', 'KB')},
        'B': {'name': 'Borb', 'k': ('Kb', 'KB')},
        'C': {'name': 'Chrunk'},
        'c': {'name': 'Chrunk'},
        'D': {'name': 'Dilk'},
    }
    assert mapping.flat == expected


def test_module_keysfrom():
    """Test the module function that extracts aliased keys."""
    this = {
        'a': {'aliases': ('A', 'a0'), 'name': 'Annabez', 'k': ['Ka']},
        'b': {'aliases': 'B', 'name': 'Borb', 'k': ('Kb', 'KB')},
        'C': {'aliases': ('c',), 'name': 'Chrunk'}
    }
    groups = [
        ['a', 'A', 'a0'],
        ['b', 'B'],
        ['C', 'c'],
    ]
    keys = aliasedkeys.keysfrom(this)
    expected = [aliasedkeys.Set(k) for k in this.keys()]
    assert keys == expected
    keys = aliasedkeys.keysfrom(this, aliases='aliases')
    expected = [aliasedkeys.Set(k) for k in groups]
    assert keys == expected


def test_keysview():
    """Test the custom keys view for aliased mappings."""
    d1 = {
        ('this', 'first'): 1,
        ('that', 'second'): 2,
        ('the other', 'third'): 3,
    }
    d2 = d1.copy()
    d2[('that', 'second')] = -20
    assert d1 != d2
    a1 = aliasedkeys.Mapping(d1)
    a2 = aliasedkeys.Mapping(d2)
    assert a1 != a2
    # NOTE: There used to be `assert a1.keys(aliased=True) == d1.keys()` -- the
    # justification being that the formally aliased keys in `a1` should be
    # equivalent to the alias-like keys in `d1`. However, aliased keys treat the
    # given aliases as a `set`, which does not preserve their input order, so
    # later comparisons to the original `tuple`, which does preserve order, will
    # be unpredictable.
    assert a1.keys() == a2.keys()
    assert a1.keys(aliased=True) == a2.keys(aliased=True)
    expected = [k for key in d1 for k in key]
    assert sorted(a1.keys()) == sorted(expected)
    for key in d1:
        assert aliasedkeys.Set(key) in a1.keys(aliased=True)
    key = ('a', 'b', 'c')
    a3 = aliasedkeys.Mapping({key: 1})
    for permutation in itertools.permutations(key, len(key)):
        aliased_key = aliasedkeys.Set(permutation)
        assert aliased_key in a3
        assert aliased_key in a3.keys(aliased=True)


def test_itemsview():
    """Test the custom items view for aliased mappings."""
    d1 = {
        ('this', 'first'): 1,
        ('that', 'second'): 2,
        ('the other', 'third'): 3,
    }
    d2 = d1.copy()
    a1 = aliasedkeys.Mapping(d1)
    a2 = aliasedkeys.Mapping(d2)
    assert a1 is not a2
    assert a1.items() == a2.items()
    assert a1.items(aliased=True) == a1.items(aliased=True)
    for key, value in d1.items():
        aliases = aliasedkeys.Set(key)
        assert (aliases, value) in a1.items(aliased=True)
        assert aliases in a1.keys(aliased=True)
        assert value in a1.values(aliased=True)


def test_mapping_copy():
    """Test the copy method of an aliased mapping."""
    d1 = {
        ('this', 'first'): 1,
        ('that', 'second'): 2,
        ('the other', 'third'): 3,
    }
    a1 = aliasedkeys.Mapping(d1)
    a2 = a1.copy()
    assert a1 == a2
    assert a1 is not a2


def test_mapping_merge():
    """Test the merge operator on aliased mappings."""
    d1 = {
        ('this', 'first'): 1,
        ('that', 'second'): 2,
    }
    d2 = {
        ('the other', 'third'): 3,
        ('another', 'fourth'): 4,
    }
    a1 = aliasedkeys.Mapping(d1)
    a2 = aliasedkeys.Mapping(d2)
    merged = a1 | a2
    expected = sorted(list(a1.keys()) + list(a2.keys()))
    assert sorted(merged.keys()) == expected
    expected = sorted(list(a1.values()) + list(a2.values()))
    assert sorted(merged.values()) == expected
    assert merged != a1
    assert merged != a2


def test_namemap():
    """Test the object that maps aliases to names."""
    references = [
        ['a', 'b', 'c'],
        {'a': 1, 'b': 2, 'c': 3},
    ]
    cases = [
        # Iterable of aliased keys
        [['b', 'b0'], ['c', 'c0', 'C']],
        # Mapping from name to aliases
        {'b': 'b0', 'c': ['c0', 'C']},
        # Mapping from name to mapping with default alias key
        {'b': {'aliases': 'b0'}, 'c': {'aliases': ['c0', 'C']}},
    ]
    n_aliases = 6 # Non-trivial to compute for an arbitrary case in cases
    for aliases in cases:
        if isinstance(aliases, typing.Mapping):
            namemap = aliasedkeys.NameMap(aliases)
            check_namemap_defs_only(namemap)
        else:
            with pytest.raises(TypeError):
                namemap = aliasedkeys.NameMap(aliases)
        for names in references:
            namemap = aliasedkeys.NameMap(aliases, refs=names)
            check_namemap_with_refs(namemap, n_aliases, names)


def check_namemap_defs_only(namemap):
    """Helper for `test_namemap` without given `refs`."""
    for alias in ['b', 'b0']:
        assert namemap[alias] == 'b'
    for alias in ['c', 'C', 'c0']:
        assert namemap[alias] == 'c'


def check_namemap_with_refs(namemap, n_aliases, names):
    """Helper for `test_namemap` with given `refs`."""
    check_namemap_defs_only(namemap)
    assert namemap['a'] == 'a'
    assert len(namemap) == n_aliases
    assert all(name in namemap for name in names)


def test_namemap_copy():
    """Test the copy method of the alias -> name mapping."""
    names = ['a', 'b', 'c']
    aliases = {'b': {'alt': 'B'}, 'c': {'alt': ['c0', 'C']}}
    namemap = aliasedkeys.NameMap(aliases, names, key='alt')
    copied = namemap.copy()
    assert copied.keys() == namemap.keys()
    assert list(copied.values()) == list(namemap.values())
    assert copied is not namemap


def test_namemap_key():
    """Test the alias -> name mapping with non-default alias key"""
    names = ['a', 'b', 'c']
    aliases = {'b': {'alt': 'B'}, 'c': {'alt': ['c0', 'C']}}
    namemap = aliasedkeys.NameMap(aliases, names, key='alt')
    assert namemap['a'] == 'a'
    for alias in ['b', 'B']:
        assert namemap[alias] == 'b'
    for alias in ['c', 'C', 'c0']:
        assert namemap[alias] == 'c'

