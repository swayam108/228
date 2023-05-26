import glob
import os
import sys
import time
import csv

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

actor_list = []
vehicle_control=[]


read_csv=open('manual_control_data.csv','r')
reader=csv.reader(read_csv)
next(reader)
for row in reader:
    vehicle_control.append(row)


try:
    client = carla.Client('127.0.0.1', 2000)
    client.set_timeout(2.0)
    world = client.get_world()
    get_blueprint_of_world = world.get_blueprint_library()
    car_model = get_blueprint_of_world.filter('crossbike')[0]
    spawn_point = world.get_map().get_spawn_points()[1]
    dropped_vehicle = world.spawn_actor(car_model, spawn_point)


    simulator_camera_location_rotation = carla.Transform(spawn_point.location, spawn_point.rotation)
    simulator_camera_location_rotation.location += spawn_point.get_forward_vector() * 30
    simulator_camera_location_rotation.rotation.yaw += 180
    simulator_camera_view = world.get_spectator()
    simulator_camera_view.set_transform(simulator_camera_location_rotation)
    dropped_vehicle.set_transform(spawn_point)
    actor_list.append(dropped_vehicle)

    def throttle_vehicle():
        for vehicle_control_data in vehicle_control:
            dropped_vehicle.apply_control(carla.vehicle_control(throttle=float(vehicle_control_data[2]),
                                                                brake=float(vehicle_control_data[0]),
                                                                steer=float(vehicle_control_data[3])))
            print(vehicle_control_data[2],vehicle_control_data[0],vehicle_control_data[3])
            time.sleep(15/1000)
    
    throttle_vehicle()

    time.sleep(1000)
finally:
    print('destroying actors')
    for actor in actor_list:
        actor.destroy()
    print('done.')