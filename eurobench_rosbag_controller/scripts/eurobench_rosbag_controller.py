#!/usr/bin/env python

import rospy
import rosnode
from std_srvs.srv import Trigger, TriggerResponse, Empty, EmptyResponse
from eurobench_bms_msgs_and_srvs.srv import StartRecording, StartRecordingResponse, PlayRosbag, PlayRosbagResponse, StopBenchmark

import os
import subprocess


class RosbagController():
    def __init__(self):
        self.start_recording_service = rospy.Service('/eurobench_rosbag_controller/start_recording', StartRecording, self.start_recording)
        self.stop_recording_service = rospy.Service('/eurobench_rosbag_controller/stop_recording', Trigger, self.stop_recording)
        self.recording_process = None
        self.recording = False

        self.play_rosbag_service = rospy.Service('/eurobench_rosbag_controller/play_rosbag', PlayRosbag, self.play_rosbag)
        self.stop_rosbag_service = rospy.Service('/eurobench_rosbag_controller/stop_rosbag', Trigger, self.stop_rosbag)
        self.playing_process = None
        self.playing = False

        self.shutdown_service = rospy.Service('/eurobench_rosbag_controller/shutdown', Empty, self.shutdown_callback)

        try:
            rospy.wait_for_service('bmcore/stop_benchmark', timeout=5.0)
        except rospy.ROSException:
            rospy.logfatal('bmcore: stop_benchmark service unavailable.')
            rospy.signal_shutdown('Benchmark core unavailable')

        self.stop_benchmark = rospy.ServiceProxy('bmcore/stop_benchmark', StopBenchmark)

        rospy.loginfo('Rosbag Controller Started')

    def start_recording(self, req):
        if self.recording:
            rospy.logerr('Already Recording')
            return StartRecordingResponse(False)

        command = ['rosrun', 'rosbag', 'record', '-a', '-x'] + ['|'.join(req.excluded_topics)] + ['-O'] + [req.rosbag_filepath] + ['__name:=eurobench_rosbag_recorder_node']

        self.recording_process = subprocess.Popen(command)
        self.recording = True
        rospy.loginfo('Started recorder, PID %s' % self.recording_process.pid)
        return StartRecordingResponse(True)

    def stop_recording(self, req):
        if not self.recording:
            rospy.logerr('Not Recording')
            return TriggerResponse(False, 'Not Recording')

        rosnode.kill_nodes(['/eurobench_rosbag_recorder_node'])

        self.recording_process = None
        self.recording = False

        rospy.loginfo('Stopped Recording')
        return TriggerResponse(True, 'Stopped Recording')

    def play_rosbag(self, req):
        if self.playing:
            rospy.logerr('Already Playing')
            return PlayRosbagResponse(False)

        command = ['rosrun', 'rosbag', 'play'] + [req.rosbag_filepath] + ['__name:=eurobench_rosbag_player_node']

        self.playing_process = subprocess.Popen(command, stdout=subprocess.PIPE)
        self.playing = True
        rospy.loginfo('Started player, PID %s' % self.playing_process.pid)
        return PlayRosbagResponse(True)

    def stop_rosbag(self, req):
        if not self.playing:
            rospy.logerr('Not Playing')
            return TriggerResponse(False, 'Not Playing')

        rosnode.kill_nodes(['/eurobench_rosbag_player_node'])

        self.playing_process = None
        self.playing = False

        rospy.loginfo('Stopped Playing')
        return TriggerResponse(True, 'Stopped Playing')

    def run(self):
        rospy.init_node('eurobench_rosbag_controller')
        rate = rospy.Rate(10)  # 10Hz

        while not rospy.is_shutdown():
            # If rosbag is playing and has finished: terminate benchmark.
            if self.playing:
                for line in self.playing_process.stdout:
                    if 'Done.' in line:
                        self.stop_benchmark()

            rate.sleep()

    def shutdown_callback(self, _):
        self.stop_recording(None)
        self.stop_rosbag(None)

        # Shutdown in one second
        rospy.Timer(rospy.Duration(1), self.shutdown, oneshot=True)        

        response = EmptyResponse()
        return response

    def shutdown(self, _):
        rospy.signal_shutdown('Shutting down')


if __name__ == "__main__":
    controller = RosbagController()
    controller.run()
