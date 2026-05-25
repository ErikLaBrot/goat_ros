cmake_minimum_required(VERSION 3.8)
project(goat_ros_laser LANGUAGES CXX)

if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(ament_cmake REQUIRED)
find_package(ld19 CONFIG REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)

add_library(goat_laser_node_lib
  src/laser_node.cpp
  src/laser_scan_conversion.cpp
)
target_include_directories(goat_laser_node_lib
  PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)
ament_target_dependencies(goat_laser_node_lib
  rclcpp
  sensor_msgs
)
target_link_libraries(goat_laser_node_lib
  ld19::ld19
)
target_compile_options(goat_laser_node_lib PRIVATE -Wall -Wextra -Wpedantic)

add_executable(goat_laser_node
  src/main.cpp
)
target_link_libraries(goat_laser_node goat_laser_node_lib)
ament_target_dependencies(goat_laser_node
  rclcpp
)

install(TARGETS
  goat_laser_node_lib
  goat_laser_node
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY include/
  DESTINATION include
)

install(DIRECTORY config launch
  DESTINATION share/${PROJECT_NAME}
)

install(FILES package.xml
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_cmake_gtest REQUIRED)

  ament_add_gtest(test_laser_scan_conversion
    test/test_laser_scan_conversion.cpp
  )
  target_include_directories(test_laser_scan_conversion
    PRIVATE
      $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  )
  target_link_libraries(test_laser_scan_conversion
    goat_laser_node_lib
    ld19::ld19
  )
  ament_target_dependencies(test_laser_scan_conversion
    rclcpp
    sensor_msgs
  )
endif()

ament_export_dependencies(
  ld19
  rclcpp
  sensor_msgs
)
ament_export_include_directories(include)

ament_package()
