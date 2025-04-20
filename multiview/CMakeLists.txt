cmake_minimum_required(VERSION 3.25.1)
include(FetchContent)

project(multiview)

set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD 17)

find_package(OpenCV REQUIRED)

find_package(Qt6 REQUIRED COMPONENTS Core Qml Multimedia)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)

find_package(zenohc REQUIRED)
find_package(zenohcxx REQUIRED)

FetchContent_Declare(cli11
    GIT_REPOSITORY https://github.com/CLIUtils/CLI11.git
    GIT_TAG v2.5.0
)
FetchContent_MakeAvailable(cli11)

qt_add_resources(QML_RESOURCES qml/qml.qrc)

add_executable(${PROJECT_NAME}
    src/main.cpp
    src/z_session.cpp
    src/z_video_player.cpp
    ${QML_RESOURCES}
)
target_compile_definitions(${PROJECT_NAME}
    PRIVATE
    ZENOHCXX_ZENOHC
)
target_link_libraries(${PROJECT_NAME}
    PRIVATE
    zenohcxx::zenohc
    Qt6::Core
    Qt6::Qml
    Qt6::Multimedia
    ${OpenCV_LIBS}
    CLI11::CLI11
)

install(
    TARGETS ${PROJECT_NAME} 
    RUNTIME_DEPENDENCY_SET ${PROJECT_NAME}_DEPS
)
# install(
#     RUNTIME_DEPENDENCY_SET ${PROJECT_NAME}_DEPS
# )
