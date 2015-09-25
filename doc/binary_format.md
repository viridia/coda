# Binary Encoding Format

## Structs

A struct starts with a struct header, followrd by an optional subtype record, followed by zero
or more fields, and ending with a DATA_END byte (0).

```
Struct ::= StructHeader Subtype? Field* DATA_END
```

The struct header indicates the class of the object. If the typeId of the class is in the range
(1..15), then the struct header consists of a single byte, where the bottom 4 bits are the constant
DATA_SUBTYPE and the upper 4 bits are the subtype ID. Otherwise, if the typeId of the class is
not in that range, then the upper 4 bits are 0 and the typeId immediately follows, encoded as a
VarInt.

```
StructHeader ::= (subTypeId << 4 | DATA_SUBTYPE)
StructHeader ::= DATA_SUBTYPE VarInt
```

The fields contain only data for fields defined in the type given in the struct header, not for
inherited fields.

## Subtypes

Subtypes are encoded as nested structs. The format of a subtype record is exactly the same as for
a struct, except that the type id is the id of the subtype - you can think of the subtype record
as a special "field" that contains all of field data for the subtype. The subtype record must always
precede other fields.

If there are several levels of inheritance, then there will be multiple nested subtype records. The
outermost struct record will represent the type that is highest in the inheritance hierarchy, and
the innermost will represent the 'actual' type of the object.

Note that subtype records may be omitted if there are no fields to encode (either because the
subtype has no fields, or because the fields are all unset). However, the subtype id for the actual
type of the object must not be omitted.

For example, suppose type A is the supertype of B which is the supertype of C. Then the encoded
stream would look like this:

```
StructHeader_A SubtypeHeader_B SubtypeHeader_C <fields_of_C> END <fields_of_B> END<fields_of_A> END
```

Note that because the actual type is stored in the innermost subtype record, the decoder cannot
construct the object until it has read all of the subtype headers. Fortunately, the logic for this
is very simple: the first time the decode sees either a field record or an END marker, then the
most recent subtype header represents the actual type of the object.

If the decoder doesn't have an implementation for a subtype, it may choose any of the earlier
subtypes to use as the runtime type, as long as all of the information for all subtypes is
preserved. Referring to the example above, if the decoder did not have an implementation for C, it
could instantiate the object as type B, but it would have to store all of the data in the 'C'
record (both field data and subtype id) for subsequent serialization of the object.

## Fields

Each field consists of a prefix byte, followed optionally by a field index, followed by the field
data. Fields are written to the stream in ascending order by index.

The lower 4 bits of the prefix byte represent the field's data type (int, float, list, set, etc.)

If the delta between a field's index and its predecessor's index is in the range (1..15), then
the delta is stored in the upper 4 bits of the prefix byte. Otherwise, the upper 4 bits will be
zero, and the prefix byte will be followed by the field index (absolute, not relative) encoded
as a VarInt.

```
Field ::= FieldHeader FieldData?
FieldHeader ::= ((field_id - prev_field_id) << 4 | field_type)
FieldHeader ::= field_type VarInt
```

The encoding of the field data depends on the field type:

**boolean types** have no field data, instead the value is encoded in the field type. DATA_ZERO
is used to encode false values, and DATA_ONE encodes true values.

**integer types** are encoded as VarInts using zig-zag encoding to convert signed integers to an
unsigned representation. However, if an integer field contains either a 0 or 1, then there is
no field data, and the DATA_ZERO or DATA_ONE field type will be used.

Thus, a field containing an integer zero can be encoded into a single byte.

**fixed-length integers, floats, and doubles** are stored literally with no encoding, except that
they are converted to network byte order.

**string and bytes fields** are represented by a length (encoded as a VarInt) followed by the
contents of the string or bytes object.

**structs** The struct data is encoded exactly as described in the previous sections.

**shared structs** For structs that are shared, the first occurrance of the struct is encoded
exactly like a regular struct. Any subsequent occurrance, however, is encoded as an integer that
represents a shared object index. This index represents the number of unique shared structs seen
so far, and is increased whenever a shared struct is seen for the first time.

The shared object index is encoded exactly like a normal integer. 

**lists and sets** Lists and sets are both encoded as lists. A list consists of an element type
code, followed by the length of the list, followed by the list elements themselves.

```
List ::= ElementType VarInt Element*
```

Individual elements are stored using mostly the same encoding as fields, but without the field
header. (No field header is needed because there's no field index and no per-element data type
since all elements are the same type.)

There are a few cases where the field data is encoded differently due to the lack of a field
header:

* For boolean and integer types, the DATA_ONE / DATA_ZERO optimization is not used, and the values
  are always encoded as VarInts.
* For shared structs that have been seen previously, the shared object index will be preceded by
  a special DATA_SHARED byte. If the decoder sees this byte when it would normally expect a
  DATA_SUBTYPE byte, it will know that the subsequent bytes contain the shared object id.

**maps** Are encoded as an alternating sequence of keys and values using the same techniques as
for lists. The element type byte contains both the key type (in the upper 4 bits) and the value
type (in the lower 4 bits).

## VarInts

## Zig-Zag encoding
