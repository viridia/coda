// ============================================================================
// Coda text format encoder
// ============================================================================

#include "coda/io/textencoder.h"

#include <assert.h>
#include <algorithm>
#include <iostream>
#include <iterator>

namespace coda {
namespace io {

Encoder& TextEncoder::writeFieldHeader(const char* name, int32_t fieldId) {
  assert(!fieldHeader);
  assert(state == CLEAR || state == STRUCT);
  if (!first) {
    strm << "\n";
    indent();
  } else if (state != CLEAR) {
    strm << '\n';
    indent();
  }
  strm << name << ": ";
  fieldHeader = true;
  state = STRUCT;
  return *this;
}

Encoder& TextEncoder::writeFieldHeader(const std::string& name, int32_t fieldId) {
  return *this;
}

Encoder& TextEncoder::writeBoolean(bool value) {
  beginValue();
  if (value) {
    strm << "true";
  } else {
    strm << "false";
  }
  return *this;
}

Encoder& TextEncoder::writeInteger(int32_t value) {
  beginValue();
  strm << value;
  return *this;
}

Encoder& TextEncoder::writeInteger(int64_t value) {
  return *this;
}

Encoder& TextEncoder::writeFixed16(int16_t value) {
  beginValue();
  strm << value;
  return *this;
}

Encoder& TextEncoder::writeFixed32(int32_t value) {
  beginValue();
  strm << value;
  return *this;
}

Encoder& TextEncoder::writeFixed64(int64_t value) {
  beginValue();
  strm << value;
  return *this;
}

Encoder& TextEncoder::writeFloat(float value) {
  beginValue();
  strm << value;
  return *this;
}

Encoder& TextEncoder::writeDouble(double value) {
  beginValue();
  strm << value;
  return *this;
}

Encoder& TextEncoder::writeString(const std::string& value) {
  beginValue();
  strm << "'";
  strm << value; // TODO: Escapes
  strm << "'";
  return *this;
}

Encoder& TextEncoder::writeBytes(const std::string& value) {
  beginValue();
  strm << "<[";
  strm << "]>";
  return *this;
}

Encoder& TextEncoder::writeBeginList(
    coda::descriptors::TypeKind elementKind, size_t length, bool fixed) {
  if (states.size() > maxDepth) {
    throw EncodingError("Maximum recursion depth exceeded");
  }
  states.push_back(state);
  beginValue();
  strm << '[';
  indentLevel += 2;
  state = CONTAINER;
  first = true;
  return *this;
}

Encoder& TextEncoder::writeEndList() {
  indentLevel -= 2;
  if (!first) {
    strm << '\n';
    indent();
  }
  strm << ']';
  state = states.back();
  states.pop_back();
  first = false;
  return *this;
}

Encoder& TextEncoder::writeBeginSet(
    coda::descriptors::TypeKind elementKind, size_t length, bool fixed) {
  if (states.size() > maxDepth) {
    throw EncodingError("Maximum recursion depth exceeded");
  }
  states.push_back(state);
  beginValue();
  strm << '[';
  indentLevel += 2;
  state = CONTAINER;
  first = true;
  return *this;
}

Encoder& TextEncoder::writeEndSet() {
  indentLevel -= 2;
  if (!first) {
    strm << '\n';
    indent();
  }
  strm << ']';
  state = states.back();
  states.pop_back();
  first = false;
  return *this;
}

Encoder& TextEncoder::writeBeginMap(
    coda::descriptors::TypeKind keyKind,
    coda::descriptors::TypeKind valueKind,
    size_t length) {
  if (states.size() > maxDepth) {
    throw EncodingError("Maximum recursion depth exceeded");
  }
  states.push_back(state);
  beginValue();
  strm << '{';
  indentLevel += 2;
  state = MAP_KEY;
  first = true;
  return *this;
}

Encoder& TextEncoder::writeEndMap() {
  indentLevel -= 2;
  if (!first) {
    strm << '\n';
    indent();
  }
  strm << '}';
  state = states.back();
  states.pop_back();
  first = false;
  return *this;
}

Encoder& TextEncoder::writeStruct(const coda::runtime::Object* value) {
  size_t stackLen = states.size();
  beginValue();
  if (value == NULL) {
    strm << "null";
  } else {
    void* sid = (void*) value;
    if (inProgress.find(sid) != inProgress.end()) {
      throw EncodingError("Already serializing object of type " + value->descriptor()->getFullName());
    }
    inProgress.insert(sid);
    writeBeginStruct();
    int32_t index = getSharedIndex(value);
    assert(index != 0);
    if (index >= 0) {
      strm << " #" << index;
    }
    value->encode(this);
    writeEndStruct();
    inProgress.erase(sid);
  }
  assert(stackLen == states.size());
  return *this;
}

Encoder& TextEncoder::writeSharedStruct(const coda::runtime::Object* value) {
  if (value == NULL) {
    writeStruct(value);
  } else {
    int32_t index = addShared(value);
    if (index >= 0) {
      beginValue();
      strm << '%' << index;
    } else {
      writeStruct(value);
    }
  }
  return *this;
}

Encoder& TextEncoder::writeBeginSubtype(const std::string& name, int32_t subtypeId) {
  states.push_back(state);
  beginValue();
  strm << '$' << subtypeId << " (" << name << "): {";
  indentLevel += 2;
  first = true;
  state = STRUCT;
  return *this;
}

Encoder& TextEncoder::writeEndSubtype() {
  writeEndStruct();
  return *this;
}

void TextEncoder::writeBeginStruct() {
  if (states.size() > maxDepth) {
    throw EncodingError("Maximum recursion depth exceeded");
  }
  states.push_back(state);
  strm << '{';
  indentLevel += 2;
  state = STRUCT;
  first = true;
}

void TextEncoder::writeEndStruct() {
  indentLevel -= 2;
  if (!first) {
    strm << '\n';
    indent();
  }
  strm << '}';
  state = states.back();
  states.pop_back();
  first = false;
}

void TextEncoder::indent() {
  std::fill_n(std::ostream_iterator<char>(strm, ""), indentLevel, ' ');
}

void TextEncoder::beginValue() {
  if (fieldHeader) {
    fieldHeader = false;
  } else if (state != CLEAR) {
    if (first) {
      strm << '\n';
      indent();
    } else if (state == MAP_KEY) {
      strm << ": ";
      state = MAP_VALUE;
    } else if (state == MAP_VALUE) {
      strm << "\n";
      indent();
      state = MAP_KEY;
    } else {
      strm << "\n";
      indent();
    }
  }
  first = false;
}


}} // namespace
