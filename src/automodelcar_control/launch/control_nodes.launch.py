from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # PUENTE DE VELOCIDAD: Conecta ROS 2 (cmd_vel) con Gazebo (DiffDrive)
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=['/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist'],
            output='screen'
        ),
        
        # TUS NODOS DE C++
        Node(
            package='automodelcar_control',
            executable='sensores_node',
            name='sensores_node',
            output='screen'
        ),
        Node(
            package='automodelcar_control',
            executable='control_node',
            name='control_node',
            output='screen'
        )
    ])