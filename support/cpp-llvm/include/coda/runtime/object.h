// ============================================================================
// Coda Object
// ============================================================================

#ifndef CODA_RUNTIME_OBJECT_H
#define CODA_RUNTIME_OBJECT_H 1

#ifndef CODA_RUNTIME_HASHING_H
  #include "coda/runtime/hashing.h"
#endif

#include <stdexcept>

namespace coda {

namespace io {
class Encoder;
class Decoder;
}

namespace descriptors {
class StructDescriptor;
class EnumDescriptor;
class FileDescriptor;
class StaticFileDescriptor;
}

namespace runtime {
class Object;

/** Base class for exception hierarchy. */
class CodaError : public std::runtime_error {
public:
  CodaError(const std::string& what_arg) : std::runtime_error(what_arg) {}
};

/** Exception thrown when attempting to modify an immutable object. */
class IllegalMutationError : public CodaError {
public:
  IllegalMutationError(const Object* object);
};

/** Base class of coda objects. */
class Object : public Hashable {
public:
  virtual ~Object() {}

  /** Return the type descriptor for this object. */
  virtual coda::descriptors::StructDescriptor* descriptor() const = 0;

  /** Return the typeId of this object. Returns 0 if this object's type is not
      a subtype. */
  int32_t typeId() const;

  /** Return true if this object is mutable. */
  bool isMutable() const { return _mutable; }

  /** Make this object and any contained objects immutable. */
  void freeze();

  /** Return a mutable copy of this object. */
  virtual Object* clone() const = 0;

  /** Equality comparator. */
  virtual bool equals(const Object *other) const {
    return other != NULL && other->descriptor() == descriptor();
  }

  /** Equality operator. */
  friend bool operator==(const Object& lhs, const Object& rhs) {
    return lhs.equals(&rhs);
  }

  /** Inequality operator. */
  friend bool operator!=(const Object& lhs, const Object& rhs) {
    return !lhs.equals(&rhs);
  }

  /** Compute hash value. */
  virtual std::size_t hashValue() const;

protected:
  Object() : _mutable(true) {}

  /** Throw an exception if this object is not mutable. */
  void checkMutable() const throw(IllegalMutationError);

  /** Override to make fields immutable. */
  virtual void freezeImpl() {};

/*
  def __str__(self):
    fieldValues = []
    for field in self.descriptor().getAllFields():
      if field.isPresent(self):
        fieldValues.append(
            '{0}: {1}'.format(field.getName(), field.getValue(self)))
    return self.descriptor().getFullName() + ' {' + '; '.join(fieldValues) + '}'

  def _beginWrite(self, encoder):
    pass

  def _endWrite(self, encoder):
    pass

  @classmethod
  def newInstance(cls, **initArgs):
    desc = cls.__desc__
    result = cls()
    for fieldName, value in initArgs.items():
      field = desc.getField(fieldName)
      if not field:
        raise AssertionError('Class {0} has no field {1}'.format(
            desc.getName(), fieldName))
      setattr(result, '_' + fieldName, value)
      result._setPresent(fieldName)
    return result

  def mergeFrom(self, src):
    '''Merge the fields of 'src' with this object.'''
    self.checkMutable()
    assert type(self) is type(src)
    assert False and 'Implement'

  def write(self, encoder):
    self._beginWrite(encoder)
    self._endWrite(encoder)

  def readFrom(self, streamCodec):
    '''Read the fields of this object from a stream.'''
    pass
 */
private:
  bool _mutable;
};

}} // namespace

#endif /* CODA_OBJECT_H */
