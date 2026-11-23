#!/usr/bin/env python3

import sys
import os
# Forzamos al nodo a leer la carpeta de IA antes que el sistema
sys.path.insert(0, os.path.expanduser('~/yolo_env/lib/python3.12/site-packages'))
import traceback

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
from ultralytics import YOLO

class YoloNode(Node):
    def __init__(self):
        super().__init__('yolo_node')
        
        self.subscription = self.create_subscription(Image, '/camara/imagen_cruda', self.image_callback, 10)
        # Tópico corregido sin la 'ñ'
        self.pub_senales = self.create_publisher(String, '/vision/senales_semanticas', 10)
        self.pub_debug = self.create_publisher(Image, '/vision/imagen_yolo', 10)
        self.bridge = CvBridge()
        
        self.get_logger().info('Cargando modelo YOLO Nano...')
        self.model = YOLO('yolov8n.pt') 
        self.get_logger().info('Nodo YOLO iniciado. Buscando objetos...')

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            resultados = self.model(frame, conf=0.5, verbose=False)
            
            detecciones_texto = []
            for r in resultados:
                cajas = r.boxes
                for caja in cajas:
                    clase_id = int(caja.cls[0])
                    nombre_clase = self.model.names[clase_id]
                    confianza = float(caja.conf[0])
                    detecciones_texto.append(f"{nombre_clase}:{confianza:.2f}")

            if detecciones_texto:
                msg_senal = String()
                msg_senal.data = ",".join(detecciones_texto)
                self.pub_senales.publish(msg_senal)
            
            frame_anotado = resultados[0].plot()
            msg_debug = self.bridge.cv2_to_imgmsg(frame_anotado, encoding='bgr8')
            self.pub_debug.publish(msg_debug)
            
        except Exception as e:
            # Imprime la ruta completa del error en lugar de solo un número
            self.get_logger().error(f'Error fatal en YOLO:\n{traceback.format_exc()}')

def main(args=None):
    rclpy.init(args=args)
    nodo = YoloNode()
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