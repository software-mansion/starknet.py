cd crypto-cpp
mkdir build/Release
(Get-content CMakeLists.txt) | Foreach-Object {$_ -replace '${CMAKE_CXX_FLAGS} -std=c++17 -Werror -Wall -Wextra -fno-strict-aliasing -fPIC', '-std=c++17 -Werror -Wall -Wextra -fno-strict-aliasing -fPIC ${CMAKE_CXX_FLAGS}'} | Set-Content CMakeLists.txt
cd build\Release
cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_COMPILER="g++" -DCMAKE_CXX_FLAGS="-Wno-type-limits -Wno-range-loop-analysis -Wno-unused-parameter" ..\..
make -C build\Release
if errorlevel neq 0 (
   exit /b %errorlevel%
)
copy build/Release/src/starkware/crypto/ffi/libcrypto_c_exports.* ../starknet_py/utils/crypto