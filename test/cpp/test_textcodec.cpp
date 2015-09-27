/* ================================================================== *
 * Address classes unit test
 * ================================================================== */

#include "gtest/gtest.h"
#include "gmock/gmock.h"
#include "coda/descriptors.h"
#include "coda/io/textencoder.h"
#include "coda/io/textdecoder.h"
#include "coda/runtime/typeregistry.h"
#include "coda/types.h"
#include "sample.h"

extern char* test_data_dir;

#include <sstream>
#include <iostream>
#include <fstream>

namespace coda {
using namespace coda::descriptors;

/*
TEST(TextCodecTest, TestEncodeDecode) {
  std::stringstream strm;
  coda::io::TextEncoder encoder(strm);
  descriptors::StructType::DESCRIPTOR.write(&encoder);
  coda::io::TextEncoder encoder2(std::cerr);
  descriptors::StructType::DESCRIPTOR.write(&encoder2);
  std::string sourcePath("test");
  coda::io::TextDecoder decoder(strm, &runtime::TypeRegistry::getInstance(), sourcePath);
  descriptors::StructType* st = decoder.decode<descriptors::StructType>();
  EXPECT_TRUE(isa<descriptors::StructType>(st));
//  self.assertEqual(st.getFullName(), descriptors.StructType.DESCRIPTOR.getFullName())
}*/

template<typename Type>
::testing::AssertionResult IsA(coda::runtime::Object* actual) {
  if (actual == NULL) {
    return ::testing::AssertionFailure() << "expected type " << Type::DESCRIPTOR.getName() <<
        ", got NULL";
  } if (isa<Type>(actual)) {
    return ::testing::AssertionSuccess() << "type is " << Type::DESCRIPTOR.getName();
  } else {
    return ::testing::AssertionFailure() << "expected type " << Type::DESCRIPTOR.getName() <<
        ", got type " << actual->descriptor()->getName();
  }
}


class TextCodec {
public:
  std::stringstream strm;
  std::string sourcePath;
  coda::io::TextEncoder encoder;
  coda::io::TextDecoder decoder;

  TextCodec()
    : sourcePath("test")
    , encoder(strm)
    , decoder(strm, &runtime::TypeRegistry::getInstance(), sourcePath)
  {
  }

  void dumpStream() {
    strm.flush();
    std::cout.flush();
    std::cerr.flush();
    std::cerr << "Stream contents: <<<";
    std::cerr << strm.str();
    std::cerr << ">>>\n";
  }
};

template <typename Codec>
class CodecTest : public ::testing::Test {
public:
  Codec codec;

  virtual ~CodecTest() {
    if (HasFailure()) {
      codec.dumpStream();
    }
  }
};

typedef ::testing::Types<TextCodec> CodecTypes;
TYPED_TEST_CASE(CodecTest, CodecTypes);

TYPED_TEST(CodecTest, TestEncodeDecodeBool) {
  BoolValue* source = new BoolValue();
  source->setValue(true);
  source->encode(&this->codec.encoder);
  BoolValue* actual = this->codec.decoder.template decode<BoolValue>();
  ASSERT_THAT(actual, ::testing::NotNull());
  ASSERT_TRUE(IsA<BoolValue>(actual));
  EXPECT_EQ(&BoolValue::DESCRIPTOR, actual->descriptor());
  EXPECT_EQ(true, actual->isValue());
}

TYPED_TEST(CodecTest, TestEncodeDecodeInteger) {
  IntegerValue* source = new IntegerValue();
  source->setValue(77);
  source->encode(&this->codec.encoder);
  IntegerValue* actual = this->codec.decoder.template decode<IntegerValue>();
  ASSERT_THAT(actual, ::testing::NotNull());
  ASSERT_TRUE(IsA<IntegerValue>(actual));
  EXPECT_EQ(&IntegerValue::DESCRIPTOR, actual->descriptor());
  EXPECT_EQ(77, actual->getValue());
}

TYPED_TEST(CodecTest, TestEncodeDecodeString) {
  StringValue* source = new StringValue();
  source->setValue("foo");
  source->encode(&this->codec.encoder);
  StringValue* actual = this->codec.decoder.template decode<StringValue>();
  ASSERT_THAT(actual, ::testing::NotNull());
  ASSERT_TRUE(IsA<StringValue>(actual));
  EXPECT_EQ(&StringValue::DESCRIPTOR, actual->descriptor());
  EXPECT_EQ("foo", actual->getValue());
}

TYPED_TEST(CodecTest, TestEncodeDecodeEmptyListValue) {
  ListValue* source = new ListValue();
//  source->setValue("foo");
  source->encode(&this->codec.encoder);
  ListValue* actual = this->codec.decoder.template decode<ListValue>();
  ASSERT_THAT(actual, ::testing::NotNull());
  ASSERT_TRUE(IsA<ListValue>(actual));
  EXPECT_EQ(&ListValue::DESCRIPTOR, actual->descriptor());
  EXPECT_EQ(0, actual->getValue().size());
//  EXPECT_EQ("foo", actual->getValue());
}

TYPED_TEST(CodecTest, TestEncodeDecodeListValue) {
  ListValue* source = new ListValue();
  source->getMutableValue().push_back(&(new IntegerValue())->setValue(11));
  source->getMutableValue().push_back(&(new IntegerValue())->setValue(12));
  source->getMutableValue().push_back(&(new IntegerValue())->setValue(13));
  source->encode(&this->codec.encoder);
  ListValue* actual = this->codec.decoder.template decode<ListValue>();
  ASSERT_THAT(actual, ::testing::NotNull());
  ASSERT_TRUE(IsA<ListValue>(actual));
  EXPECT_EQ(&ListValue::DESCRIPTOR, actual->descriptor());
  ASSERT_EQ(3, actual->getValue().size());
  ASSERT_TRUE(IsA<IntegerValue>(actual->getValue()[0]));
  EXPECT_EQ(11, ((IntegerValue*)actual->getValue()[0])->getValue());
  EXPECT_EQ(12, ((IntegerValue*)actual->getValue()[1])->getValue());
  EXPECT_EQ(13, ((IntegerValue*)actual->getValue()[2])->getValue());
}

TYPED_TEST(CodecTest, TestDecodeSample) {
  std::string sourcePath(test_data_dir);
  sourcePath.append("/sample.txt");
  std::cout << sourcePath << '\n';
  std::ifstream strm(sourcePath.c_str());
  ASSERT_TRUE(strm.good());
  coda::io::TextDecoder decoder(strm, &runtime::TypeRegistry::getInstance(), sourcePath);
  sample::S2* result = decoder.template decode<sample::S2>();
  ASSERT_THAT(result, ::testing::NotNull());
  ASSERT_TRUE(result->hasLeft());

  const sample::S1* s1 = result->getLeft();
  ASSERT_THAT(s1, ::testing::NotNull());

  // scalarBoolean
  ASSERT_TRUE(s1->hasScalarBoolean());
  ASSERT_TRUE(s1->isScalarBoolean());

  // scalarBoolean
  ASSERT_TRUE(s1->hasScalarBoolean());
  ASSERT_TRUE(s1->isScalarBoolean());

  // scalarI16
  ASSERT_TRUE(s1->hasScalarI16());
  ASSERT_EQ(11, s1->getScalarI16());

  // scalarI32
  ASSERT_TRUE(s1->hasScalarI32());
  ASSERT_EQ(12, s1->getScalarI32());

  // scalarI64
  ASSERT_TRUE(s1->hasScalarI64());
  ASSERT_EQ(13, s1->getScalarI64());

  // scalarFixedI16
  ASSERT_TRUE(s1->hasScalarFixedI16());
  ASSERT_EQ(14, s1->getScalarFixedI16());

  // scalarFixedI32
  ASSERT_TRUE(s1->hasScalarFixedI32());
  ASSERT_EQ(15, s1->getScalarFixedI32());

  // scalarFixedI64
  ASSERT_TRUE(s1->hasScalarFixedI64());
  ASSERT_EQ(16, s1->getScalarFixedI64());

  // scalarFloat
  ASSERT_TRUE(s1->hasScalarFloat());
  ASSERT_EQ(55.0, s1->getScalarFloat());

  // scalarDouble
  ASSERT_TRUE(s1->hasScalarDouble());
  ASSERT_EQ(56.0, s1->getScalarDouble());

  // scalarString
  ASSERT_TRUE(s1->hasScalarString());
  ASSERT_EQ("alpha\n\t", s1->getScalarString());

  // scalarBytes
  ASSERT_TRUE(s1->hasScalarBytes());
  ASSERT_EQ("beta", s1->getScalarBytes());

  // scalarEnum
  ASSERT_TRUE(s1->hasScalarEnum());
  ASSERT_EQ(sample::E_E1, s1->getScalarEnum());

  // Lists
  ASSERT_THAT(s1->getListBoolean(), testing::ElementsAre(true, false, true));
  ASSERT_THAT(s1->getListInt(), testing::ElementsAre(100, 101, 102));
  ASSERT_THAT(s1->getListFloat(), testing::ElementsAre(110.0, 110.1, 110.2));
// The decoder actually works correctly, but the embedded null in the string below doesn't.
//  ASSERT_THAT(s1->getListString(), testing::ElementsAre("beta", "delta\0", "yin-yan: ☯"));
  ASSERT_THAT(s1->getListEnum(), testing::ElementsAre(sample::E_E1, sample::E_E2, sample::E_E1));

  // Sets
  ASSERT_THAT(s1->getSetInt(), testing::UnorderedElementsAre(200, 201, 202));
  ASSERT_THAT(s1->getSetString(),
      testing::UnorderedElementsAre("gamma", "\'single-quoted\'", "\"double-quoted\""));
  ASSERT_THAT(s1->getSetEnum(), testing::UnorderedElementsAre(sample::E_E1, sample::E_E2));

  // Maps
  ASSERT_EQ(2, s1->getMapIntString().size());
  ASSERT_THAT(s1->getMapIntString().at(300), testing::Eq("three_oh_oh"));
  ASSERT_THAT(s1->getMapIntString().at(301), testing::Eq("three_oh_one"));
  ASSERT_EQ(2, s1->getMapStringInt().size());
  ASSERT_THAT(s1->getMapStringInt().at("three_oh_oh"), testing::Eq(300));
  ASSERT_THAT(s1->getMapStringInt().at("three_oh_one"), testing::Eq(301));
  ASSERT_EQ(2, s1->getMapEnumStruct().size());
  ASSERT_THAT(s1->getMapEnumStruct().at(sample::E_E1), ::testing::NotNull());
  ASSERT_THAT(s1->getMapEnumStruct().at(sample::E_E2), ::testing::NotNull());

  // Unused
  ASSERT_FALSE(s1->hasUnused());

  result->deleteRecursive();
}

}
