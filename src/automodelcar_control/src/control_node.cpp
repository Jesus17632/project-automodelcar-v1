#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/vector3.hpp> 
#include <geometry_msgs/msg/twist.hpp>
#include <cmath>
#include <algorithm>

class ControlNodeBasico : public rclcpp::Node {
public:
    ControlNodeBasico() : Node("control_node") {
        pub_cmd_vel_ = this->create_publisher<geometry_msgs::msg::Twist>("/cmd_vel", 10);
        
        sub_error_ = this->create_subscription<geometry_msgs::msg::Vector3>(
            "/vision/error_carril", 10,
            std::bind(&ControlNodeBasico::error_callback, this, std::placeholders::_1));

        tiempo_anterior_ = this->now();
        RCLCPP_INFO(this->get_logger(), "Control Iniciado: PD con Prevención y Modo Rescate");
    }

private:
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr pub_cmd_vel_;
    rclcpp::Subscription<geometry_msgs::msg::Vector3>::SharedPtr sub_error_;

    rclcpp::Time tiempo_anterior_;
    double error_anterior_ = 0.0;

    // ==========================================
    // 1. PARÁMETROS DEL PD (Rectas y Curvas)
    // ==========================================
    const double kp_suave_ = 0.0015; 
    const double kd_suave_ = 0.0150; 
    
    const double kp_agresivo_ = 0.007; 
    const double kd_agresivo_ = 0.005; 

    const double umbral_curva_ = 60.0; 
    const double zona_muerta_ = 15.0; 
    const double inversor_giro_ = 1.0; 
    
    // ==========================================
    // 2. PARÁMETROS DE COMPENSACIÓN Y RESCATE
    // ==========================================
    const double umbral_peligro_ = 60.0; // Píxeles. Si se acerca más que esto, lo repele.
    const double fuerza_repulsion_ = 0.8; // rad/s. Empuje máximo preventivo.
    const double giro_rescate_ = 1.8; // rad/s. Volantazo fuerte si pierde la línea por completo.
    
    const double velocidad_base_ = 0.15; 
    const double limite_direccion_ = 3.0; 

    void error_callback(const geometry_msgs::msg::Vector3::SharedPtr msg) {
        rclcpp::Time tiempo_actual = this->now();
        double dt = (tiempo_actual - tiempo_anterior_).seconds();

        if (dt <= 0.001) return; 

        // Leer datos
        double error_actual = msg->x * inversor_giro_; 
        double dist_izq = msg->y;                      
        double dist_der = msg->z;                      

        // Detectar si falta algún lado (Python manda -1.0)
        bool falta_izq = (dist_izq < 0.0);
        bool falta_der = (dist_der < 0.0);

        // Derivada cruda
        double derivada = (error_actual - error_anterior_) / dt;

        double angulo_giro = 0.0;

        // ==========================================
        // 3. LÓGICA DE DIRECCIÓN
        // ==========================================
        
        if (falta_izq && !falta_der) {
            // ¡EMERGENCIA! Perdimos la izquierda. Significa que nos fuimos muy a la derecha.
            // Ignoramos el PD y damos el volantazo a la izquierda.
            angulo_giro = giro_rescate_;
            RCLCPP_INFO_THROTTLE(this->get_logger(), *this->get_clock(), 500, "¡PERDIDA IZQ! Rescatando hacia la Izquierda.");
        } 
        else if (falta_der && !falta_izq) {
            // ¡EMERGENCIA! Perdimos la derecha.
            // Ignoramos el PD y damos el volantazo a la derecha.
            angulo_giro = -giro_rescate_;
            RCLCPP_INFO_THROTTLE(this->get_logger(), *this->get_clock(), 500, "¡PERDIDA DER! Rescatando hacia la Derecha.");
        } 
        else {
            // ESTADO NORMAL: Vemos ambos carriles (O perdimos ambos)
            
            // Aplicar zona muerta solo si estamos a salvo en el centro
            if (!falta_izq && !falta_der && std::abs(error_actual) < zona_muerta_) {
                error_actual = 0.0;
                derivada = 0.0;
            }

            // A. Control PD Dinámico
            double kp_actual = (std::abs(error_actual) > umbral_curva_) ? kp_agresivo_ : kp_suave_;
            double kd_actual = (std::abs(error_actual) > umbral_curva_) ? kd_agresivo_ : kd_suave_;
            angulo_giro = (kp_actual * error_actual) + (kd_actual * derivada);

            // B. Compensación Preventiva (Repelente)
            // Si te pegas mucho a la izquierda, te empuja a la derecha (-)
            if (!falta_izq && dist_izq < umbral_peligro_) {
                double deficit = (umbral_peligro_ - dist_izq) / umbral_peligro_;
                angulo_giro -= fuerza_repulsion_ * std::pow(deficit, 2.0);
            }
            // Si te pegas mucho a la derecha, te empuja a la izquierda (+)
            if (!falta_der && dist_der < umbral_peligro_) {
                double deficit = (umbral_peligro_ - dist_der) / umbral_peligro_;
                angulo_giro += fuerza_repulsion_ * std::pow(deficit, 2.0);
            }
        }

        // 4. Límites de seguridad mecánicos
        if (angulo_giro > limite_direccion_) angulo_giro = limite_direccion_;
        if (angulo_giro < -limite_direccion_) angulo_giro = -limite_direccion_;

        // 5. Publicar a Gazebo
        geometry_msgs::msg::Twist cmd;
        cmd.linear.x = velocidad_base_;                
        cmd.angular.z = angulo_giro;       

        pub_cmd_vel_->publish(cmd);

        error_anterior_ = error_actual;
        tiempo_anterior_ = tiempo_actual;
    }
};

int main(int argc, char * argv[]) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<ControlNodeBasico>());
    rclcpp::shutdown();
    return 0;
}