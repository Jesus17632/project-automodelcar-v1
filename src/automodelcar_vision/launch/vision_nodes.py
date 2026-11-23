from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        #Simulación de vision en gazebo
        Node(
            package='ros_gz_image',
            executable='image_bridge',
            arguments=['/camara/imagen_cruda'],
            output='screen'
        ),
        
        # TUS NODOS DE VISIÓN
        Node(
            package='automodelcar_vision',
            executable='camara_node',
            name='camara_node',
            output='screen'
        ),
        Node(
            package='automodelcar_vision',
            executable='ipm_node',
            name='ipm_node',
            output='screen'
        ),
        Node(
            package='automodelcar_vision',
            executable='carril_node',
            name='carril_node',
            output='screen'
        ),
        Node(
            package='automodelcar_vision',
            executable='yolo_node',
            name='yolo_node',
            output='screen'
        )
    ])