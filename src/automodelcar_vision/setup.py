import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'automodelcar_vision'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # AÑADE ESTA LÍNEA PARA LOS ARCHIVOS LAUNCH:
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='tu_nombre',
    maintainer_email='tu_correo@email.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'camara_node = automodelcar_vision.camara_node:main',
            'ipm_node = automodelcar_vision.ipm_node:main',
            'carril_node = automodelcar_vision.carril_node:main',
            'yolo_node = automodelcar_vision.yolo_node:main',
        ],
    },
)