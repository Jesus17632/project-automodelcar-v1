cmake_minimum_required(VERSION 3.8)
project(automodelcar_control)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# ==========================================
# 1. DEPENDENCIAS
# ==========================================
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)

# ==========================================
# 2. NODOS C++ (COMPILACIÓN)
# ==========================================
add_executable(sensores_node src/sensores_node.cpp)
ament_target_dependencies(sensores_node rclcpp std_msgs)

add_executable(control_node src/control_node.cpp)
ament_target_dependencies(control_node rclcpp std_msgs geometry_msgs)

# ==========================================
# 3. INSTALACIÓN DE BINARIOS C++
# ==========================================
install(TARGETS
  sensores_node
  control_node
  DESTINATION lib/${PROJECT_NAME}
)

# ==========================================
# 4. INSTALACIÓN DE DIRECTORIOS (Launch)
# ==========================================
install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()