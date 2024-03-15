# Copyright 2022 INRAE, French National Research Institute for Agriculture, Food and Environment
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from launch import LaunchDescription

from launch.actions import (
    IncludeLaunchDescription,
    DeclareLaunchArgument,
    OpaqueFunction,
    GroupAction,
    SetEnvironmentVariable,
)

from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

from tirrex_demo import (
    get_log_directory,
    get_debug_directory,
    get_demo_timestamp,
    save_replay_configuration,
)


def get_mode(context):
    return LaunchConfiguration("mode").perform(context)


def get_robot(context):
    return LaunchConfiguration("robot").perform(context)


def get_launch_robot(context):
    return LaunchConfiguration("launch_robot").perform(context)


def get_path(context):
    return LaunchConfiguration("path").perform(context)


def get_record(context):
    return LaunchConfiguration("record").perform(context)


def get_demo_config_directory(context):
    return LaunchConfiguration("demo_config_directory").perform(context)


def get_robot_config_directory(context):
    # demo_config_directory = get_demo_config_directory(context)
    # robot_config_directory = demo_config_directory + "/robots/" + get_robot(context)
    # if os.path.exists(robot_config_directory):
    #     return robot_config_directory
    # else:
    return get_package_share_directory("tirrex_" + get_robot(context)) + "/config"


def launch_setup(context, *args, **kwargs):

    robot_namespace = get_robot(context)

    demo = "tirrex_path_following"
    demo_timestamp = get_demo_timestamp()

    mode = get_mode(context)
    record = get_record(context)
    demo_config_directory = get_demo_config_directory(context)
    robot_config_directory = get_robot_config_directory(context)
    print("demo_config_directory", demo_config_directory)
    print("robot_config_directory", robot_config_directory)
    path = get_path(context)

    debug_directory = get_debug_directory(demo, demo_timestamp, record)
    log_directory = get_log_directory(demo, demo_timestamp, record)

    print(" demo_config_directory ", demo_config_directory)
    print(" debug_directory ", debug_directory)
    print(" log_directory ", log_directory)

    actions = []

    # in rolling : use launch_ros/launch_ros/actions/set_ros_log_dir.py instead
    actions.append(SetEnvironmentVariable("ROS_LOG_DIR", log_directory))

    if get_launch_robot(context) == "true":
        actions.append(
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    get_package_share_directory("tirrex_demo") + "/launch/core.launch.py"
                ),
                launch_arguments={
                    "mode": mode,
                    "demo_config_directory": demo_config_directory,
                    "robot_config_directory": robot_config_directory,
                    "robot_namespace": robot_namespace,
                }.items(),
            )
        )

    actions.append(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                get_package_share_directory("tirrex_demo")
                + "/launch/robot/robot_localisation.launch.py"
            ),
            launch_arguments={
                "mode": mode,
                "robot_namespace": robot_namespace,
                "demo_config_directory": demo_config_directory,
                "robot_config_directory": robot_config_directory,
            }.items(),
        )
    )

    actions.append(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                get_package_share_directory("tirrex_demo")
                + "/launch/robot/robot_path_following.launch.py"
            ),
            launch_arguments={
                "mode": mode,
                "robot_namespace": robot_namespace,
                "demo_config_directory": demo_config_directory,
                "robot_config_directory": robot_config_directory,
                "trajectory_filename": path,
            }.items(),
        )
    )

    # if record == "true":

    #     actions.append(
    #         IncludeLaunchDescription(
    #             PythonLaunchDescriptionSource(
    #                 get_package_share_directory("tirrex_demo") + "/launch/record.launch.py"
    #             ),
    #             launch_arguments={
    #                 "demo": demo,
    #                 "demo_timestamp": demo_timestamp,
    #                 "demo_config_directory": demo_config_directory,
    #                 "mode": mode,
    #                 "robot_namespace": robot_namespace,
    #             }.items(),
    #         )
    #     )

    #     save_replay_configuration(
    #         demo,
    #         demo_timestamp,
    #         "tirrex_path_following.launch.py",
    #         {
    #             "mode": "replay_" + mode,
    #             "robot": robot_namespace,
    #             "launch_robot": "true",
    #             "path": path,
    #         },
    #     )

    return [GroupAction(actions)]


def generate_launch_description():

    declared_arguments = []

    declared_arguments.append(DeclareLaunchArgument("mode", default_value="simulation"))

    declared_arguments.append(DeclareLaunchArgument("robot"))

    declared_arguments.append(DeclareLaunchArgument("launch_robot", default_value="true"))

    declared_arguments.append(DeclareLaunchArgument("path"))

    declared_arguments.append(DeclareLaunchArgument("record", default_value="false"))

    declared_arguments.append(
        DeclareLaunchArgument(
            "demo_config_directory",
            default_value=get_package_share_directory("tirrex_path_following") + "/config",
        )
    )

    return LaunchDescription(declared_arguments + [OpaqueFunction(function=launch_setup)])
