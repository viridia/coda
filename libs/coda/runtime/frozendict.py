import collections

class FrozenDict(collections.Mapping):
  '''Immutable dictionary class that can be hashed.'''

  def __init__(self, *args, **kwargs):
    self._d = dict(*args, **kwargs)
    self._hash = None

  def __iter__(self):
    return iter(self._d)

  def __len__(self):
    return len(self._d)

  def __getitem__(self, key):
    return self._d[key]

  def __str__(self):
    return str(self._d)

  def __hash__(self):
    if self._hash is None:
      self._hash = hash(frozenset(self._d.items()))
    return self._hash
