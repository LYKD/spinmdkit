cmake_minimum_required(VERSION 3.18...4.2)
project(spinmdkit LANGUAGES NONE)

option(SPINMDKIT_BUILD_NATIVE "Build the C++17 acceleration module" ON)
set(SPINMDKIT_VERSION "0.1.0a1")

if(SPINMDKIT_BUILD_NATIVE)
  enable_language(CXX)
  find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)
  find_package(pybind11 CONFIG REQUIRED)

  pybind11_add_module(_core MODULE cpp/core.cpp)
  target_compile_features(_core PRIVATE cxx_std_17)
  target_compile_definitions(_core PRIVATE VERSION_INFO="${SPINMDKIT_VERSION}")

  if(MSVC)
    target_compile_options(_core PRIVATE /W4 /permissive-)
  else()
    target_compile_options(_core PRIVATE -Wall -Wextra -Wpedantic)
  endif()

  install(TARGETS _core DESTINATION spinmdkit)
endif()
