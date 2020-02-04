EUROBENCH Benchmark Software
=================================================

Benchmark core, benchmark scripts and graphical interface for the MADROB and BEAST benchmarks.

## Installation

Install the ROS package as usual:
```
cd catkin_workspace/src
git clone https://github.com/madrob-beast/eurobench_benchmarking_software.git
pip install -r eurobench_benchmarking_software/requirements.txt
cd ../
catkin_make
```

Note: The default output directory is `~/eurobench_output`, and can be configured in `config/general.yaml`.

## Running benchmarks

Start the benchmark core in either MADROB or BEAST mode:
```
roslaunch eurobench_benchmark_core madrob_all.launch 
OR
roslaunch eurobench_benchmark_core beast_all.launch
```

Use the GUI to select the current robot, the benchmark to run, and specific settings for either the MADROB or BEAST environment.
Benchmarks can be started, stopped prematurely, and the results can be viewed on the right.

When a benchmark finishes, its results are written to the output directory.

Two example benchmark scripts (with ID `TEST_BENCHMARK_MADROB` and `TEST_BENCHMARK_BEAST`) are included. They listen to a simple On/Off sensor to determine if a robot passed through it. A rosbag with mock sensor readings is played in a loop by the launch file.
