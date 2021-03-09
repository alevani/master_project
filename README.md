# Ant-Inspired Task Allocation Implementation.
Ant-Inspired Task Allocation Model Within a Swarm of Homogeneous Simulated Robotic-Agents

## What can be observed
The robot are dispatch from a starting point in an Arena. Their task is selected following the Task allocation model proposed in this paper: https://ssr.seas.harvard.edu/files/ssr/files/disc14-cornejo.pdf.
Throughout the simulation, Forager will collect resource from the outside world and gather them in the home area (blue). Then, nest processors will process the resource and move it to the cleaning area (pink) for it to e picked up and move to the waste area (orange).

### Communication
The knowledge about a task or a need are not shared within the robot anymore. Instead, the nest serves as an information center where ant report their current task and ask for
a new assignment under specific conditions. This is to ensure the simulation lays in the decentralized / distributed swarm robot paradigm.

Conditions for ant task report:
- The ant is currently not carrying a resource (clear sign of an ant currently active in its assigned task)
- AND the ant is on the area `TYPE_HOME`
- The ant has not report its task since `600` simulation timestep

## How to: Line command
```
> python simulation.py -r <nb_robot> -p <np_point> -s <is_simulation_visible> -b <do_robot_lose_battery> -t <do_record_trail> -a <avoidance_activation> -f <stats_file_name.csv> -e <exp_number (1 or 2)>
> python simulation.py -r 50 -p 1000 -s True -b False -t False -a True -f stats.csv -e 1

-r = Number of simulated robot
-p = Number of randomly generated resource
-s = Show visualisation
-b = Active battery effects
-t = Record robot's path
-a = specifies if the robot should avoid one another
-f = specify the name the output stats file should have
-e = speciy which of the two experiments the program will be running
```

## In-pygame command shorcut
```
q -> Quit the simulation
y -> Shows sensors and collision box
r -> Increments resrouce's needs by a random number
x -> if -t = True, show where each robot have been during the simulation
p -> Pause the simulation
right-click or click 7 -> add a robot to the simulation
left-click -> spread a random number of point in a 100x100 area around the position of the click
click 6 -> Remove a robot from the simulation
v -> Delete 1/3 of the robots (random)
b -> Delete 1/3 of the robots performing foraging
n -> Delete 1/3 of the robots performing nest processing
m -> Delete 1/3 of the robots performing cleaning
```

Current status: [Video link](https://www.youtube.com/watch?v=uGT88xa4q-w)
[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/uGT88xa4q-w/0.jpg)](https://www.youtube.com/watch?v=uGT88xa4q-w)


Below, some results of the current task allocation system. There's 50 robot running, no battery loss, -5 food every 500 simulation step.
![IMAGE ALT TEXT HERE](https://github.com/alevani/master_project/blob/main/assets/test50.png)