import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'automodelcar_design'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Rutas agregadas para tus carpetas
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*')),
        (os.path.join('share', package_name, 'meshes'), glob('meshes/*')),
        (os.path.join('share', package_name, 'launch'), glob('launch/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='jesus',
    maintainer_email='jesusflores.tech@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [

            #Nodos a ejecutar
            'camara_node = automodelcar_vision.camara_node:main',
            'ipm_node = automodelcar_vision.ipm_node:main',
            'carril_node = automodelcar_vision.carril_node:main',
            'yolo_node = automodelcar_vision.yolo_node:main',
        ],
    },
)