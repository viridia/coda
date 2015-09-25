// ============================================================================
// Coda text format encoder
// ============================================================================

#include "coda/io/binaryencoder.h"
#include "coda/io/binaryformat.h"

#include <assert.h>
#include <algorithm>
#include <iostream>
#include <iterator>

namespace coda {
namespace io {

static uint8_t KIND_TO_DTYPE[coda::descriptors::TYPE_KIND_DECL];

std::ostream& operator<<(std::ostream& os, const runtime::StringRef& str) {
  os.write(str.begin(), str.size());
  return os;
}

BinaryEncoder::BinaryEncoder(std::ostream& str)
  : strm(str)
  , state(CLEAR)
  , subtypeId(-1)
  , fieldId(-1)
  , lastFieldId(-1)
{
  // Initialize the global kind-to-dataType conversion table.
  KIND_TO_DTYPE[coda::descriptors::TYPE_KIND_BOOL] = DT_ONE;
  KIND_TO_DTYPE[coda::descriptors::TYPE_KIND_INTEGER] = DT_VARINT;
  KIND_TO_DTYPE[coda::descriptors::TYPE_KIND_FLOAT] = DT_FLOAT;
  KIND_TO_DTYPE[coda::descriptors::TYPE_KIND_DOUBLE] = DT_DOUBLE;
  KIND_TO_DTYPE[coda::descriptors::TYPE_KIND_STRING] = DT_BYTES;
  KIND_TO_DTYPE[coda::descriptors::TYPE_KIND_BYTES] = DT_BYTES;
  KIND_TO_DTYPE[coda::descriptors::TYPE_KIND_LIST] = DT_LIST;
  KIND_TO_DTYPE[coda::descriptors::TYPE_KIND_SET] = DT_LIST;
  KIND_TO_DTYPE[coda::descriptors::TYPE_KIND_MAP] = DT_MAP;
  KIND_TO_DTYPE[coda::descriptors::TYPE_KIND_STRUCT] = DT_STRUCT;
}

#if 0
  def fileBegin(self):
    self.__state = self.State.STRUCT

  def fileEnd(self):
    self.__state = self.State.CLEAR
#endif

Encoder& BinaryEncoder::writeSubtypeHeader(const runtime::StringRef& subtypeName, int32_t sid) {
  assert(state == STRUCT || state == SUBTYPE || state == CLEAR);
  subtypeId = sid;
  if (state == STRUCT) {
    beginSubtype();
  }
  return *this;
}

Encoder& BinaryEncoder::writeFieldHeader(const runtime::StringRef& fieldName, int32_t fid) {
  assert(fieldId < 0);
  assert(state == CLEAR || state == STRUCT || state == SUBTYPE);
  fieldId = fid;
  if (state == CLEAR) {
    state = STRUCT;
  }
  return *this;
}

Encoder& BinaryEncoder::writeBoolean(bool value) {
  if (fieldId >= 0) {
    beginValue(value ? DT_ONE : DT_ZERO);
  } else if (value) {
    writeUByte(1);
  } else {
    writeUByte(0);
  }
  return *this;
}

Encoder& BinaryEncoder::writeInteger(int32_t value) {
  if (value == 0) {
    beginValue(DT_ZERO);
  } else if (value == 1) {
    beginValue(DT_ONE);
  } else {
    beginValue(DT_VARINT);
    writeVarInt(zigZagEncode(value));
  }
  return *this;
}

Encoder& BinaryEncoder::writeInteger(int64_t value) {
  if (value == 0) {
    beginValue(DT_ZERO);
  } else if (value == 1) {
    beginValue(DT_ONE);
  } else {
    beginValue(DT_VARINT);
    writeVarInt(zigZagEncode(value));
  }
  return *this;
}

Encoder& BinaryEncoder::writeFixed16(int16_t value) {
  beginValue(DT_FIXED16);
  #if !CODA_BIG_ENDIAN
    #if CODA_HAVE_GCC_BYTESWAP_16
      value = __builtin_bswap16(value);
    #else
      #error "No 16-bit byte-swap function defined."
    #endif
  #endif
  strm.write((char *)&value, sizeof(value));
  return *this;
}

Encoder& BinaryEncoder::writeFixed32(int32_t value) {
  beginValue(DT_FIXED32);
  #if !CODA_BIG_ENDIAN
    #if CODA_HAVE_GCC_BYTESWAP_32
      value = __builtin_bswap32(value);
    #else
      #error "No 32-bit byte-swap function defined."
    #endif
  #endif
  strm.write((char *)&value, sizeof(value));
  return *this;
}

Encoder& BinaryEncoder::writeFixed64(int64_t value) {
  beginValue(DT_FIXED64);
  #if !CODA_BIG_ENDIAN
    #if CODA_HAVE_GCC_BYTESWAP_64
      value = __builtin_bswap64(value);
    #else
      #error "No 64-bit byte-swap function defined."
    #endif
  #endif
  strm.write((char *)&value, sizeof(value));
  return *this;
}

Encoder& BinaryEncoder::writeFloat(float value) {
  beginValue(DT_FLOAT);
  int32_t intVal = *reinterpret_cast<int32_t*>(&value);
  #if !CODA_BIG_ENDIAN
    #if CODA_HAVE_GCC_BYTESWAP_32
      intVal = __builtin_bswap32(intVal);
    #else
      #error "No 32-bit byte-swap function defined."
    #endif
  #endif
  strm.write((char *)&intVal, sizeof(intVal));
  return *this;
}

Encoder& BinaryEncoder::writeDouble(double value) {
  beginValue(DT_DOUBLE);
  int64_t intVal = *reinterpret_cast<int64_t*>(&value);
  #if !CODA_BIG_ENDIAN
    #if CODA_HAVE_GCC_BYTESWAP_64
      intVal = __builtin_bswap64(intVal);
    #else
      #error "No 64-bit byte-swap function defined."
    #endif
  #endif
  strm.write((char *)&intVal, sizeof(intVal));
  return *this;
}

Encoder& BinaryEncoder::writeString(const runtime::StringRef& value) {
  beginValue(DT_BYTES);
  writeVarInt(value.size());
  strm << value;
  return *this;
}

Encoder& BinaryEncoder::writeBytes(const runtime::StringRef& value) {
  beginValue(DT_BYTES);
  writeVarInt(value.size());
  strm << value;
  return *this;
}

Encoder& BinaryEncoder::writeBeginList(
    coda::descriptors::TypeKind elementKind, size_t length, bool fixed ) {
  if (fixed) {
    beginValue(DT_PLIST);
  } else {
    beginValue(DT_LIST);
  }
  writeUByte(KIND_TO_DTYPE[elementKind]);
  writeVarInt(length);
  return *this;
}

Encoder& BinaryEncoder::writeEndList() {
  return *this;
}

Encoder& BinaryEncoder::writeBeginSet(
    coda::descriptors::TypeKind elementKind, size_t length, bool fixed ) {
  return writeBeginList(elementKind, length, fixed);
}

Encoder& BinaryEncoder::writeEndSet() {
  return *this;
}

Encoder& BinaryEncoder::writeBeginMap(
    coda::descriptors::TypeKind keyKind,
    coda::descriptors::TypeKind valueKind,
    size_t length) {
  beginValue(DT_MAP);
  writeUByte(
      (KIND_TO_DTYPE[keyKind] << 4) | KIND_TO_DTYPE[valueKind]);
  writeVarInt(length);
  return *this;
}

Encoder& BinaryEncoder::writeEndMap() {
  return *this;
}

Encoder& BinaryEncoder::writeStruct(const coda::runtime::Object* value, bool shared) {
  if (value == NULL) {
    // NULL object is written as zero.
    beginValue(DT_ZERO);
  } else {
    if (shared) {
      int32_t index = addShared(value);
      if (index >= 0) {
        if (fieldId < 0) {
          writeUByte(DT_SHARED_REF);
        }
        writeInteger(index);
        return *this;
      }
    }

    void* sid = (void*) value;
    if (inProgress.find(sid) != inProgress.end()) {
      throw EncodingError("Already serializing object of type " +
          value->descriptor()->getFullName());
    }
    inProgress.insert(sid);
    State savedState = state;
    if (fieldId < 0 && shared) {
      writeUByte(DT_SHARED_DEF);
    }
    beginValue(shared ? DT_SSTRUCT : DT_STRUCT);
    int32_t savedFieldId = lastFieldId;
    lastFieldId = 0;
    state = STRUCT;
    value->encode(this);
    writeUByte(DT_END);
    subtypeId = -1;
    state = savedState;
    lastFieldId = savedFieldId;
    inProgress.erase(sid);
  }
  return *this;
}

void BinaryEncoder::beginSubtype() {
  if (subtypeId > 0 and subtypeId <= 15) {
    writeUByte((subtypeId << 4) | DT_SUBTYPE);
  } else {
    writeUByte(DT_SUBTYPE);
    writeVarInt((uint32_t) subtypeId);
  }
  lastFieldId = 0;
  subtypeId = -1;
  state = SUBTYPE;
}

void BinaryEncoder::beginValue(DataType dataType) {
  if (subtypeId >= 0) {
    beginSubtype();
  }
  if (fieldId >= 0) {
    assert(state == CLEAR || state == STRUCT || state == SUBTYPE);
    assert(dataType != DT_END);
    int32_t delta = fieldId - lastFieldId;
    if (delta <= 0) {
//      print(self.__lastFieldId, self.__fieldId)
      throw EncodingError("Fields should be serialized in monotonically increasing order");
    }
    if (delta <= 15) {
      writeUByte((delta << 4) | dataType);
    } else {
      writeUByte(dataType);
      writeVarInt((uint32_t) fieldId);
    }
    lastFieldId = fieldId;
    fieldId = -1;
  } else if (state == MAP_KEY) {
    state = MAP_VALUE;
  } else if (state == MAP_VALUE) {
    state = MAP_KEY;
  }
}

void BinaryEncoder::writeUByte(uint8_t byte) {
  strm.put(byte);
}

void BinaryEncoder::writeVarInt(uint32_t i) {
  char b[8];
  size_t pos = 0;
  while (i > 0x7f) {
    b[pos++] = (i & 0xff) | 0x80;
    i = i >> 7;
  }
  b[pos++] = i;
  strm.write(b, pos);
}

void BinaryEncoder::writeVarInt(uint64_t i) {
  char b[16];
  size_t pos = 0;
  while (i > 0x7f) {
    b[pos++] = (i & 0xff) | 0x80;
    i = i >> 7;
  }
  b[pos++] = i;
  strm.write(b, pos);
}

uint32_t BinaryEncoder::zigZagEncode(int32_t value) {
  if (value >= 0) {
    return uint32_t(value) << 1;
  } else {
    return uint32_t(-1 - (int32_t(value) << 1));
  }
}

uint64_t BinaryEncoder::zigZagEncode(int64_t value) {
  if (value >= 0) {
    return uint64_t(value) << 1;
  } else {
    return uint64_t(-1 - (int64_t(value) << 1));
  }
}

}} // namespace
