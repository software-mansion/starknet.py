#!/bin/bash

cd crypto-cpp
mkdir -p build/Release

CMAKE_CXX_COMPILER="g++"
IFS='-' read -r -a TARGET_ARR_WRONG_ORDER <<< "$PLAT"
SYS_V="${TARGET_ARR_WRONG_ORDER[1]}"
TARGET_ARCH="${TARGET_ARR_WRONG_ORDER[2]}"

if [ "$(uname)" == "Darwin" ]; then
    TARGET_TRIPLET="${TARGET_ARCH}-apple-macos${SYS_V}"

    if [[ "$(uname -m)" != "$TARGET_ARCH" ]]; then
      echo "Crosscompiling enabled"
      export CMAKE_CROSSCOMPILING="1"
    fi
    if [[ "$TARGET_ARCH" == *"arm"* ]]; then
      echo "Compiling for arm architecture"
      export CMAKE_SYSTEM_PROCESSOR="arm"
    fi

    echo "Targeting ${TARGET_TRIPLET}"
    export MACOSX_DEPLOYMENT_TARGET="${SYS_V}"
    export MACOSX_VERSION_MIN="${SYS_V}"

    sed -i'.original' "s/\${CMAKE_CXX_FLAGS} -std=c++17 -Werror -Wall -Wextra -fno-strict-aliasing -fPIC/-std=c++17 -Werror -Wall -Wextra -fno-strict-aliasing -fPIC \${CMAKE_CXX_FLAGS} -target ${TARGET_TRIPLET}/" CMakeLists.txt
    CMAKE_CXX_COMPILER="clang++"
  else
    sed -i'.original' "s/\${CMAKE_CXX_FLAGS} -std=c++17 -Werror -Wall -Wextra -fno-strict-aliasing -fPIC/-std=c++17 -Werror -Wall -Wextra -fno-strict-aliasing -fPIC \${CMAKE_CXX_FLAGS}/" CMakeLists.txt
fi

cat CMakeLists.txt
(cd build/Release; cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_COMPILER="${CMAKE_CXX_COMPILER}" -DCMAKE_CXX_FLAGS="-Wno-type-limits -Wno-range-loop-analysis -Wno-unused-parameter" ../..)

if [ "$(uname)" == "Darwin" ]; then
  TARGET_TRIPLET="${TARGET_ARCH}-apple-macos${SYS_V}"
  sed -i'.original' "s/#Note that googlemock target already builds googletest/set(CMAKE_CXX_FLAGS \"-target ${TARGET_TRIPLET}\")/" build/Release/_deps/googletest-src/CMakeLists.txt
fi

make -C build/Release
if [ $? -ne 0 ]; then
  exit 1
fi
cp build/Release/src/starkware/crypto/ffi/libcrypto_c_exports.* ../starknet_py/utils/crypto
