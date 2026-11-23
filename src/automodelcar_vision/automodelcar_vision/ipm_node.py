#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from rclpy.qos import qos_profile_sensor_data

class NodoVisionIPM(Node):
    def __init__(self):
        super().__init__('vision_ipm_node')
        
        self.subscription = self.create_subscription(
            Image, '/camara/imagen_cruda', self.procesar_fotograma, qos_profile_sensor_data)
            
        self.publisher_ipm = self.create_publisher(Image, '/vision/imagen_ipm', 10)
        self.publisher_debug = self.create_publisher(Image, '/vision/debug_ipm', 10)
            
        self.bridge = CvBridge()
        self.get_logger().info('Nodo IPM (Vacío/Passthrough) iniciado. No aplica transformación.')

    def procesar_fotograma(self, msg):
        try:
            #Imagen original de la cámara
            frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
            
            # SIN TRANSFORMACIÓN IPM
            # Simplemente copiamos la imagen cruda
            frame_ipm = frame.copy()
            frame_debug = frame.copy()
            
            # Y la publicamos en los canales que espera el nodo de carril
            self.publisher_ipm.publish(self.bridge.cv2_to_imgmsg(frame_ipm, encoding='bgr8'))
            self.publisher_debug.publish(self.bridge.cv2_to_imgmsg(frame_debug, encoding='bgr8'))
            
        except Exception as e:
            self.get_logger().error(f'Error IPM: {e}')

def main(args=None):
    rclpy.init(args=args)
    nodo = NodoVisionIPM()
    try:
        rclpy.spin(nodo)
    except KeyboardInterrupt:
        pass
    finally:
        nodo.destroy_node()
        if rclpy.ok(): rclpy.shutdown()

if __name__ == '__main__':
    main()