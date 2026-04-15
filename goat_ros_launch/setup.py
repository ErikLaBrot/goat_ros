"""Install the goat_ros_launch package."""

import glob
import os

from setuptools import find_packages, setup

package_name = 'goat_ros_launch'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml', 'README.md']),
        (os.path.join('share', package_name, 'launch'),
            glob.glob(os.path.join('launch', '*.launch.py'))),
        (os.path.join('share', package_name, 'config', 'rosbag', 'profiles'),
            glob.glob(os.path.join('config', 'rosbag', 'profiles', '*.txt'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='GOAT Maintainers',
    maintainer_email='goat@example.com',
    description='High-level launch and rosbag profiles for GOAT bringup.',
    license='TODO',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
        ],
    },
)
