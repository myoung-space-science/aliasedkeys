# Support for Objects with Aliased Keys

This package provides objects based on sets of aliased keys.

# Example Usage

## Mapping

The core object in this package is the `Mapping` class, which is similar to `collections.abc.Mapping` except that multiple aliased keys may point to the same value.

It is possible to create an instance of `Mapping` from a variety of standard
mapping objects. A common use case is to create an instance from a built-in
`dict` with strings or tuples of strings as keys.

```python
>>> from aliasedkeys import Mapping
>>> mapping = {'a': 1, ('b', 'B'): 2, ('c', 'C', 'c0'): -9}
>>> aliased = Mapping(mapping)
>>> aliased
Mapping('a': 1, 'b = B': 2, 'c = C = c0': -9)
```

Another possible use case is to create an instance from a `dict` that maps
individual keys to `dict` values that contain the corresponding aliases under a
particular key. The default alias key is `aliases`.

```python
>>> mapping = {
...     'a': {'rank': 2},
...     'b': {'aliases': ('B',), 'rank': 1},
...     'C': {'aliases': ('c', 'c0'), 'rank': 0},
... }
>>> aliased = Mapping(mapping)
>>> aliased
Mapping('a': {'rank': 2}, 'B' = 'b': {'rank': 1}, 'C' = 'c' = 'c0': {'rank': 0})
```

It is possible to use a different key for aliases by passing the value to `aliases`.

```python
>>> mapping = {
...     'a': {'rank': 2},
...     'b': {'other names': ('B',), 'rank': 1},
...     'C': {'other names': ('c', 'c0'), 'rank': 0},
... }
>>> aliased = Mapping(mapping, aliases='other names')
>>> aliased
Mapping('a': {'rank': 2}, 'B' = 'b': {'rank': 1}, 'C' = 'c' = 'c0': {'rank': 0})
```

The user may access an individual item by any one (but only one) of its valid
aliases.

```python
>>> aliased['a']
1
>>> aliased['b']
2
>>> aliased['B']
2
>>> aliased[('b', 'B')]
...
KeyError: ('b', 'B')
```

Aliased items are identical.

```python
>>> aliased['b'] is aliased['B']
True
```

The representation of keys, values, and items reflect the internal grouping
by alias, but iterating over each produces de-aliased members. This behavior
naturally supports loops and comprehensions, since access is only valid for
individual items.

```python
>>> aliased.keys()
AliasedKeys(['a', 'b = B', 'c = C = c0'])
>>> aliased.values()
AliasedValues([1, 2, -9])
>>> aliased.items()
AliasedItems([('a', 1), ('b = B', 2), ('c = C = c0', -9)])
>>> list(aliased.keys())
['a', 'b', 'B', 'c', 'C', 'c0']
>>> list(aliased.values())
[1, 2, 2, -9, -9, -9]
>>> list(aliased.items())
[('a', 1), ('b', 2), ('B', 2), ('c', -9), ('C', -9), ('c0', -9)]
>>> for k, v in aliased.items():
...     print(f"{k!r}: {v}")
... 
'a': 1
'b': 2
'B': 2
'c0': -9
'C': -9
'c': -9
```

Passing `aliased=True` to a `keys`, `values`, or `items` allows iteration over
aliased groups.

```python
>>> for k, v in aliased.items(aliased=True):
...     print(f"{k}: {v}")
... 
'a': 1
'B' = 'b': 2
'c' = 'c0' = 'C': -9
```

It is always possible to access the equivalent de-aliased `dict`.

```python
>>> aliased.flat
{'a': 1, 'b': 2, 'B': 2, 'c': -9, 'C': -9, 'c0': -9}
```

Updates and deletions apply to all associated aliases.

```python
>>> aliased['c'] = 5.6
>>> list(aliased.items())
[('a', 1), ('b', 2), ('B', 2), ('c', 5.6), ('C', 5.6), ('c0', 5.6)]
>>> del aliased['c']
>>> list(aliased.items())
[('a', 1), ('b', 2), ('B', 2)]
```

Users may access all aliases for a given key via the `alias` method.

```python
>>> aliased.alias('c')
MappingKey('c0', 'C')
>>> aliased.alias('c', include=True)
MappingKey('c', 'c0', 'C')
```

The `squeeze` method replaces single-valued interior mappings (i.e., mapping
that are values of the aliased mapping) with their corresponding value.

```python
>>> this = {('a', 'A'): {'score': 3}, ('b', 'B'): {'score': 10}} 
>>> from aliasedkeys import Mapping
>>> mapping = Mapping(this)
>>> mapping
Mapping('a' = 'A': {'score': 3}, 'B' = 'b': {'score': 10})
>>> mapping.squeeze()
Mapping('a' = 'A': 3, 'B' = 'b': 10)
```

The singular interior mappings need not have the same key unless the `strict`
keyword is set to a truthy value.

```python
>>> this = {('a', 'A'): {'score': 3}, ('b', 'B'): {'value': 10}} 
>>> Mapping(this).squeeze()
Mapping('a' = 'A': 3, 'B' = 'b': 10)
>>> Mapping(that).squeeze(strict=True)
...
aliasedkeys.ValuesTypeError: Cannot squeeze interior mappings with different keys when strict == True
```

The `fromkeys` class method creates an aliased mapping with keys taken from a
pre-defined object and all values set to a fixed value (default: `None`). The predefined object may be an instance of `dict`, an iterable type containing grouped and individual keys, or `Set`.

```python
>>> mapping = {
...     'a': {'aliases': ('A', 'a0'), 'n': 1, 'm': 'foo'},
...     'b': {'aliases': 'B', 'n': -4},
...     'c': {'n': 42},
... }
>>> aliased = Mapping.fromkeys(mapping, value=-1.0)
>>> aliased
Mapping('a0 | a | A': -1.0, 'B | b': -1.0, 'c': -1.0)
>>> keys = [('a', 'A', 'a0'), ('B', 'b'), 'c']
>>> aliased = Mapping.fromkeys(keys, value=-1.0)
>>> aliased
Mapping('a0 | a | A': -1.0, 'B | b': -1.0, 'c': -1.0)
>>> keys = Groups(*keys)
>>> aliased = Mapping.fromkeys(keys, value=-1.0)
>>> aliased
Mapping('a0 | a | A': -1.0, 'B | b': -1.0, 'c': -1.0)
```


## MutableMapping

A mutable aliased mapping is an aliased mapping that supports updates. It is more similar to the built-in `dict` type. The following examples build on the examples shown for `Mapping`.

It is possible to create an instance of `MutableMapping` from any object that can initialize `Mapping`, as well as from an instance of `Mapping` itself.

```python
>>> from aliasedkeys import MutableMapping
>>> MutableMapping(aliased) == MutableMapping(mapping)
True
```

Updates and deletions apply to all associated aliases.

```python
>>> mutable = MutableMapping(aliased)
>>> mutable['c'] = 5.6
>>> list(mutable.items())
[('a', 1), ('b', 2), ('B', 2), ('c', 5.6), ('C', 5.6), ('c0', 5.6)]
>>> del mutable['c']
>>> list(mutable.items())
[('a', 1), ('b', 2), ('B', 2)]
```

Users may additionally register new aliases via the `alias` method inherited
from `Mapping`. Attempting to register an alias will raise a `KeyError` if it is
already an alias for a different key.

```python
>>> mutable.alias('b', 'my B')
>>> mutable.alias('b')
Set('B | my B')
>>> mutable
MutableMapping('a': 1, 'b | my B | B': 2)
```

Attempting to register an alias will raise a `KeyError` if it exists as a
stand-alone key or an alias for one or more other keys.

```python
>>> mutable.alias('a', 'b')
...
KeyError: "'b' is already an alias for '(B, my B)'"
>>> mutable.alias('b', 'a')
...
KeyError: "'a' is an existing key"
```

The `label` method maps a new key to one or more values that are already
associated with existing keys.

```python
>>> mutable.label('b, c', 'b', 'c')
```

It does not alter the existing keys &mdash; it simply provides a convenient way
to access multiple values.

```python
>>> sorted(mutable)
['B', 'C', 'a', 'b', 'c', 'c0']
>>> mutable['b, c']
>>> (2, -9)
```

Since all aliased keys map to the same value, it is only necessary to provide
one alias from a group of aliased keys.

```python
>>> mutable.label('B and C', 'B', 'C')
>>> mutable['B and C'] == mutable['b, c']
True
```

Passing only the assigned label returns all associated keys.

```python
>>> mutable.label('B and C')
('B', 'b', 'c', 'C', 'c0')
```

Attempting to access an unknown label raises a `KeyError`.

```python
>>> mutable.label('B and Q')
...
KeyError: "No values assigned to 'B and Q'"
```

Attempting to assign the value of an unknown key also raises a `KeyError`.
```python
>>> mutable.label('A and B', 'A', 'B')
KeyError: 'A'

The above exception was the direct cause of the following exception:

...
KeyError: "Cannot assign value of 'A' to 'A and B'"
```

A more complex example may clarify the utility of this method:

```python
>>> scores = MutableMapping(
...     {
...         ('Isabelle', 'Izzy'): 8.6,
...         ('Michael', 'Mike', 'Mikey'): 3.2,
...         ('Anthony', 'Tony', 'T-Bone'): 5.0,
...         ('Gabriela', 'Gabby', 'The Kid'): 7.1,
...     }
... )
>>> scores.label('Team A', 'Izzy', 'Tony')
>>> scores.label('Team B', 'Mike', 'Gabby')
>>> scores.label('Girls', 'Izzy', 'Gabby')
>>> scores.label('Boys', 'Tony', 'Mike')
>>> sum(scores['Team A'])
13.6
>>> sum(scores['Team B'])
10.3
>>> sum(scores['Girls'])
15.7
>>> sum(scores['Boys'])
8.2
```

The `freeze` method creates a new immutable mapping from the current mutable
mapping. The default behavior is to not include any assigned groups. Passing a
truthy value via the `groups` parameter causes the new immutable mapping to
include all groups as standard key-value pairs.

```python
>>> scores.freeze()
Mapping('Izzy' = 'Isabelle': 8.6, 'Michael' = 'Mike' = 'Mikey': 3.2, 'T-Bone' = 'Anthony' = 'Tony': 5.0, 'Gabriela' = 'Gabby' = 'The Kid': 7.1)
>>> scores.freeze(groups=True)
Mapping('Izzy' = 'Isabelle': 8.6, 'Michael' = 'Mike' = 'Mikey': 3.2, 'T-Bone' = 'Anthony' = 'Tony': 5.0, 'Gabriela' = 'Gabby' = 'The Kid': 7.1, 'Team A': (8.6, 5.0), 'Team B': (3.2, 7.1), 'Girls': (8.6, 7.1), 'Boys': (5.0, 3.2))
```

## Set

Aliased key sets are set-like collections of associated keys.

```python
>>> from aliasedkeys import Set
>>> x = Set('a', 'A')
>>> y = Set('b')
>>> x
Set('A' = 'a')
>>> y
Set('b')
>>> x | y
Set('A' = 'b' = 'a')
```

The major difference between a set of aliased keys and a standard set is that it is not possible to create an empty set of aliased keys.

```python
>>> Set()
...
TypeError: At least one alias is required
```

## Sets

Instances of the `Sets` class are collections of aliased key sets. They
implement the standard `MutableSet` protocol, and provide some additional
methods.

```python
>>> from aliasedkeys import Sets
>>> sets = Sets(('a', 'A'), 'b', ['c', 'C'], ['d0', 'd1', 'd2'])
```

Subscription behaves similarly to that of standard sets, except that the
returned value is the aliased key set containing the given key.

```python
>>> sets['a']
Set('A' = 'a')
>>> sets['X']
...
KeyError: "No group containing 'X'"
```

The `get` method behaves similarly to the standard `Mapping.get` method. It
retrieves the aliased key set that contains a given key, if available, and a
default value otherwise. The default value defaults to `None`.

```python
>>> sets.get('a')
Set('A' = 'a')
>>> sets.get('X')
```

The `merge` method creates a new instance after applying a set-wise OR operation
to each pair of key sets with a common key.

```python
>>> updates = [('a', 'first'), ('second', 'b'), ('this', 'that')]
>>> merged = sets.merge(*updates)
>>> merged
Sets('c' = 'C', 'd1' = 'd2' = 'd0', 'A' = 'first' = 'a', 'second' = 'b', 'this' = 'that')
```

The `update` method is equivalent to an in-place `merge`.

```python
>>> sets.update(*updates)
>>> sets
Sets('c' = 'C', 'd1' = 'd2' = 'd0', 'A' = 'first' = 'a', 'second' = 'b', 'this' = 'that')
```

The `without` method creates a new instance after discarding any aliased key set
that contains one of the given keys. It will ignore unrecognized and redundant keys.

```python
>>> sets.without('C')
Sets('A' = 'a', 'b', 'd2' = 'd1' = 'd0')
>>> sets.without('d')
Sets('A' = 'a', 'b', 'C' = 'c', 'd2' = 'd1' = 'd0')
>>> sets.without('C', 'c')
Sets('A' = 'a', 'b', 'd2' = 'd1' = 'd0')
```

## NameMap

Instances of the `NameMap` class map one or more aliased keys to a canonical key.

```python
>>> from aliasedkeys import NameMap
>>> namemap = NameMap({'a': (1, -9), 'b': ['B', 'other']})
>>> namemap[1]
'a'
>>> namemap[-9] is namemap[1]
True
>>> namemap['other']
'b'
>>> namemap['other'] is namemap['b']
True
```

