cmake_minimum_required(VERSION 3.8)
project(goat_vesc_ros LANGUAGES C CXX)

if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(ament_cmake REQUIRED)
find_package(builtin_interfaces REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(rosidl_default_runtime REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(goat_vesc CONFIG REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/VescControlCommand.msg"
  "msg/VescMotorState.msg"
  DEPENDENCIES builtin_interfaces std_msgs
)

add_library(vesc_node_lib STATIC
  src/vesc_node.cpp
)
target_include_directories(vesc_node_lib
  PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)
ament_target_dependencies(vesc_node_lib
  builtin_interfaces
  rclcpp
  sensor_msgs
  std_msgs
)
target_link_libraries(vesc_node_lib
  goat_vesc::goat_vesc
)
rosidl_get_typesupport_target(cpp_typesupport_target ${PROJECT_NAME} "rosidl_typesupport_cpp")
target_link_libraries(vesc_node_lib
  "${cpp_typesupport_target}"
)

add_executable(vesc_node
  src/main.cpp
)
target_link_libraries(vesc_node PRIVATE vesc_node_lib)

install(TARGETS
  vesc_node_lib
  EXPORT export_${PROJECT_NAME}
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION lib/${PROJECT_NAME}
)

install(TARGETS
  vesc_node
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
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_export_dependencies(
  builtin_interfaces
  goat_vesc
  rclcpp
  rosidl_default_runtime
  sensor_msgs
  std_msgs
)
ament_export_include_directories(include)
ament_export_targets(export_${PROJECT_NAME} HAS_LIBRARY_TARGET)

ament_package()
