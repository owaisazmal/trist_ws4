This package includes urdf of the robot and, SLAM and navigation.

### Note ###

# Used packages
- robot_localization
- ira_laser_tools
- pointcloud_to_laserscan
- gmapping
- move_base
- amcl
- teb-local-planner
- global-planner
- costmap-2d
- map-server

# Gazebo models and worlds
- Add all the models in igv/models folder into /usr/share/gazebo-{your gazebo version}/models folder.
- If you want more worlds, check https://github.com/mlherd/Dataset-of-Gazebo-Worlds-Models-and-Maps. Add the models of selected world into /usr/share/gazebo-{your gazebo version}/models folder and .world file into igv/worlds folder.
- Change the world name in the igv_robot.launch file.
sudo cp -r ~/2024igv_ws/src/igv/models/* /usr/share/gazebo-11/models/


# Sensor fusions
- converted camera pointcloud into a laserscan
- fused the above camera scan data with lidar scan data (using ira_laser_tools pkg)
- fused odometry with IMU (using robot_localization pkg)

# SLAM
- used Gmapping SLAM
- launching command: roslaunch igv igv_slam.launch
- After mapping, run command: rosrun map_server map_saver -f map name
- Run the above command in terminal in maps folder location. Otherwise manually add the saved .pgm and .yaml file into igv/maps folder.

# navigation
- implemented both AMCL and GPS localizations
- In GPS localization, odometry, IMU and GPS data have been fused using robot_localization pkg
- There are two seperate launch files for AMCL and GPS localizations. Use one of them at a time. Select the file in the igv_navigation.launch file (uncomment the wanted one and comment the remaining file)
- launching command: roslaunch igv igv_navigation.launch
- give a goal from 2D goal in RViz
