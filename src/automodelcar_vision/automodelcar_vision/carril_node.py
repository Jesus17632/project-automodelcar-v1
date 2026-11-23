#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Vector3 
from cv_bridge import CvBridge
import cv2
import numpy as np

class CarrilHoughNode(Node):
    def __init__(self):
        super().__init__('carril_hough_node')
        
        # Suscriptor
        self.subscription = self.create_subscription(
            Image, '/vision/imagen_ipm', self.image_callback, 10)
            
        # Publicadores
        self.pub_debug = self.create_publisher(Image, '/vision/debug_carril', 10)
        self.pub_error = self.create_publisher(Vector3, '/vision/error_carril', 10) 
        
        self.bridge = CvBridge()
        
        self.get_logger().info('Nodo Hough: ROI (Mitad inferior) + Zona Muerta Central activados.')

    def image_callback(self, msg):
        try:
            # Convertir imagen
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            alto, ancho = frame.shape[:2]
            centro_camara = ancho // 2  
            debug_img = frame.copy()

            # Filtros básicos
            gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gris, (5, 5), 0)
            bordes = cv2.Canny(blur, 50, 150) 

            # -----------------------------------------------------------------
            # 1. ZONA DE INTERÉS (ROI): IGNORAR LA MITAD SUPERIOR
            # -----------------------------------------------------------------
            mitad_alto = alto // 2
            bordes[0:mitad_alto, :] = 0 
            cv2.line(debug_img, (0, mitad_alto), (ancho, mitad_alto), (0, 255, 255), 2) # Línea amarilla

            # -----------------------------------------------------------------
            # 2. ZONA MUERTA CENTRAL: IGNORAR LÍNEAS PUNTEADAS
            # -----------------------------------------------------------------
            # Define qué tan ancha será la zona ciega (25% del ancho total de la pantalla)
            ancho_zona_muerta = int(ancho * 0.25)
            
            x_inicio_muerta = centro_camara - (ancho_zona_muerta // 2)
            x_fin_muerta = centro_camara + (ancho_zona_muerta // 2)
            
            # Apagamos los píxeles de esa columna central
            bordes[:, x_inicio_muerta:x_fin_muerta] = 0

            # Dibujamos líneas celestes para ver la zona muerta en el debug
            cv2.line(debug_img, (x_inicio_muerta, mitad_alto), (x_inicio_muerta, alto), (255, 255, 0), 2)
            cv2.line(debug_img, (x_fin_muerta, mitad_alto), (x_fin_muerta, alto), (255, 255, 0), 2)
            # -----------------------------------------------------------------

            # Transformada de Hough
            lineas = cv2.HoughLinesP(
                bordes, 
                rho=1,              
                theta=np.pi/180,    
                threshold=15,       
                minLineLength=10,   
                maxLineGap=5        
            )

            posiciones_izq_x = []
            posiciones_der_x = []

            # Clasificar las líneas en Izquierda o Derecha
            if lineas is not None:
                for linea in lineas:
                    x1, y1, x2, y2 = linea[0]
                    if x2 == x1: continue 
                    
                    m = (y2 - y1) / (x2 - x1)
                    if abs(m) < 0.1: continue 
                    
                    x_medio = (x1 + x2) // 2

                    if m < 0 and x_medio < centro_camara:
                        posiciones_izq_x.append(x_medio)
                        cv2.line(debug_img, (x1, y1), (x2, y2), (255, 0, 0), 2) # Azul (Izq)
                    elif m > 0 and x_medio > centro_camara:
                        posiciones_der_x.append(x_medio)
                        cv2.line(debug_img, (x1, y1), (x2, y2), (0, 0, 255), 2) # Rojo (Der)

            # -----------------------------------------------------------------
            # 3. CÁLCULO DE DISTANCIAS
            # -----------------------------------------------------------------
            promedio_izq = int(np.mean(posiciones_izq_x)) if len(posiciones_izq_x) > 0 else None
            promedio_der = int(np.mean(posiciones_der_x)) if len(posiciones_der_x) > 0 else None
            
            distancia_izq = (centro_camara - promedio_izq) if promedio_izq is not None else 0
            distancia_der = (promedio_der - centro_camara) if promedio_der is not None else 0

            # -----------------------------------------------------------------
            # 4. CÁLCULO DEL CENTRO
            # -----------------------------------------------------------------
            centro_carril = centro_camara 

            if promedio_izq is not None and promedio_der is not None:
                centro_carril = (promedio_izq + promedio_der) // 2
            elif promedio_izq is not None:
                centro_carril = promedio_izq + 200
            elif promedio_der is not None:
                centro_carril = promedio_der - 200

            error_pixeles = float(centro_camara - centro_carril)

            # -----------------------------------------------------------------
            # 5. DIAGNÓSTICO VISUAL Y PUBLICACIÓN
            # -----------------------------------------------------------------
            cv2.line(debug_img, (centro_camara, 0), (centro_camara, alto), (255, 255, 255), 1) 
            cv2.line(debug_img, (int(centro_carril), 0), (int(centro_carril), alto), (0, 255, 0), 2) 

            texto_izq = f"Dist Izq: {distancia_izq} px" if promedio_izq else "Dist Izq: --"
            texto_der = f"Dist Der: {distancia_der} px" if promedio_der else "Dist Der: --"
            texto_err = f"Error Centro: {error_pixeles:.1f}"

            cv2.putText(debug_img, texto_izq, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            cv2.putText(debug_img, texto_der, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(debug_img, texto_err, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            self.pub_debug.publish(self.bridge.cv2_to_imgmsg(debug_img, encoding='bgr8'))
            
            # -----------------------------------------------------------------
            # 6. ENVIAR MENSAJE AL CONTROLADOR PD
            # -----------------------------------------------------------------
            msg_error = Vector3()
            msg_error.x = float(error_pixeles)
            msg_error.y = float(distancia_izq) if promedio_izq is not None else -1.0
            msg_error.z = float(distancia_der) if promedio_der is not None else -1.0
            
            self.pub_error.publish(msg_error)
            
        except Exception as e:
            self.get_logger().error(f'Error procesando Hough: {e}')

def main(args=None):
    rclpy.init(args=args)
    nodo = CarrilHoughNode()
    try:
        rclpy.spin(nodo)
    except KeyboardInterrupt:
        pass
    finally:
        nodo.destroy_node()
        if rclpy.ok(): rclpy.shutdown()

if __name__ == '__main__':
    main()