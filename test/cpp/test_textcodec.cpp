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

#include <sstream>
#include <iostream>

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
  descriptors::StructType* st = decoder.read<descriptors::StructType>();
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
  source->write(&this->codec.encoder);
  BoolValue* actual = this->codec.decoder.template read<BoolValue>();
  ASSERT_THAT(actual, ::testing::NotNull());
  ASSERT_TRUE(IsA<BoolValue>(actual));
  EXPECT_EQ(&BoolValue::DESCRIPTOR, actual->descriptor());
  EXPECT_EQ(true, actual->isValue());
}

TYPED_TEST(CodecTest, TestEncodeDecodeInteger) {
  IntegerValue* source = new IntegerValue();
  source->setValue(77);
  source->write(&this->codec.encoder);
  IntegerValue* actual = this->codec.decoder.template read<IntegerValue>();
  ASSERT_THAT(actual, ::testing::NotNull());
  ASSERT_TRUE(IsA<IntegerValue>(actual));
  EXPECT_EQ(&IntegerValue::DESCRIPTOR, actual->descriptor());
  EXPECT_EQ(77, actual->getValue());
}

TYPED_TEST(CodecTest, TestEncodeDecodeString) {
  StringValue* source = new StringValue();
  source->setValue("foo");
  source->write(&this->codec.encoder);
  StringValue* actual = this->codec.decoder.template read<StringValue>();
  ASSERT_THAT(actual, ::testing::NotNull());
  ASSERT_TRUE(IsA<StringValue>(actual));
  EXPECT_EQ(&StringValue::DESCRIPTOR, actual->descriptor());
  EXPECT_EQ("foo", actual->getValue());
}

TYPED_TEST(CodecTest, TestEncodeDecodeEmptyListValue) {
  ListValue* source = new ListValue();
//  source->setValue("foo");
  source->write(&this->codec.encoder);
  ListValue* actual = this->codec.decoder.template read<ListValue>();
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
  source->write(&this->codec.encoder);
  ListValue* actual = this->codec.decoder.template read<ListValue>();
  ASSERT_THAT(actual, ::testing::NotNull());
  ASSERT_TRUE(IsA<ListValue>(actual));
  EXPECT_EQ(&ListValue::DESCRIPTOR, actual->descriptor());
  EXPECT_EQ(3, actual->getValue().size());
  ASSERT_TRUE(IsA<IntegerValue>(actual->getValue()[0]));
  EXPECT_EQ(11, ((IntegerValue*)actual->getValue()[0])->getValue());
  EXPECT_EQ(12, ((IntegerValue*)actual->getValue()[1])->getValue());
  EXPECT_EQ(13, ((IntegerValue*)actual->getValue()[2])->getValue());
}

}
