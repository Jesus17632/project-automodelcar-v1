#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from rclpy.qos import qos_profile_sensor_data

class NodoCamaraBase(Node):
    def __init__(self):
        super().__init__('nodo_camara_base')
        
        #Suscriptor
        self.subscription = self.create_subscription(
            Image,
            '/camara/imagen_cruda',
            self.procesar_fotograma,
            qos_profile_sensor_data)
            
        #Publicador
        self.publisher_imagen = self.create_publisher(
            Image, 
            '/vision/imagen_salida', 
            10)
            
        self.bridge = CvBridge()
        self.get_logger().info('Nodo de cámara iniciado (Sin filtros).')

    def procesar_fotograma(self, msg):
        try:
            #ROS a OpenCV
            frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
            
            
   
            #De OpenCV a ROS
            msg_salida = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
            self.publisher_imagen.publish(msg_salida)
            
        except Exception as e:
            self.get_logger().error(f'Error al procesar el fotograma: {e}')

def main(args=None):
    rclpy.init(args=args)
    nodo = NodoCamaraBase()
    try:
        rclpy.spin(nodo)
    except KeyboardInterrupt:
        pass
    finally:
        nodo.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()