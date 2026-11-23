import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, AppendEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_name = 'automodelcar_design'
    pkg_dir = get_package_share_directory(pkg_name)
    urdf_file = os.path.join(pkg_dir, 'urdf', 'automodelcar.urdf')

    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()

    # --- INICIO DE LA SOLUCIÓN ---
    # Obtenemos la carpeta 'share' general de tu workspace para que Gazebo encuentre los .STL
    ws_share_dir = os.path.dirname(pkg_dir)
    set_env = AppendEnvironmentVariable('GZ_SIM_RESOURCE_PATH', ws_share_dir)
    # --- FIN DE LA SOLUCIÓN ---

    # 1. Nodo Publicador de estado del robot
    rsp_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc}]
    )

    # 2. Ruta a tu pista
    ruta_pista = os.path.join(
        os.path.expanduser('~'), 
        'Documents', 'Robótica', 'ROS2', 'cancha_simulacion', 
        'cancha_automodel.world' # <-- Verifica que este sea tu nombre correcto
    )

    # 3. Iniciar el nuevo Gazebo (gz) y cargar tu pista
    ros_gz_sim_pkg = get_package_share_directory('ros_gz_sim')
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim_pkg, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'-r {ruta_pista}'}.items()
    )

    # 4. Hacer spawn del coche
    spawn_node = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-string', robot_desc,
            '-name', 'automodelcar',
            '-z', '0.3'
        ],
        output='screen'
    )

    return LaunchDescription([
        set_env,      
        rsp_node,
        gazebo_launch,
        spawn_node
    ])