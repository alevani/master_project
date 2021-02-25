# Ant-Inspired Task Allocation Implementation.
Ant-Inspired Task Allocation Model Within a Swarm of Homogeneous Simulated Robotic-Agents

## What can be observed
The robot are dispatch from a starting point in an Arena. Their task is selected following the Task allocation model proposed in this paper: https://ssr.seas.harvard.edu/files/ssr/files/disc14-cornejo.pdf.
Throughout the simulation, Forager will collect resource from the outside world and gather them in the home area (blue). Then, nest maintenance will process the resource and move it to the brood-caring area (pink) for it to e picked up and move to the waiste area (orange).

### Communication
The knowledge about a task or a need are not shared within the robot anymore. Instead, the nest serves as an information center where ant report their current task and ask for
a new assignment under specific conditions. This is to ensure the simulation lays in the decentralized / distributed swarm robot paradigm.

## How to: Line command
```
> python simulation.py -r <nb_robot> -p <np_point> -s <is_simulation_visible> -b <do_robot_lose_battery> -t <do_record_trail> -a <avoidance_activation>
> python simulation.py -r 50 -p 1000 -s True -b False -t False -a True

-r = Number of simulated robot
-p = Number of randomly generated resource
-s = Show visualisation
-b = Active battery effects
-t = Record robot's path
-a = specifies if the robot should avoid one another
```

## In-pygame command shorcut
```
q -> Quit the simulation
y -> Shows sensors and collision box
r -> Increments resrouce's needs by a random number
x -> if -t = True, show where each robot have been during the simulation
p -> Pause the simulation
right-click -> add a robot to the simulation (NOT SUPPORTED ATM)
left-click -> spread a random number of point in a 100x100 area around the position of the click
```

Current status: [Video link](https://www.youtube.com/watch?v=HpS3zuJ1a9I)
[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/HpS3zuJ1a9I/0.jpg)](https://www.youtube.com/watch?v=HpS3zuJ1a9I)


Below, some results of the current task allocation system. There's 50 robot running, no battery loss, -10 food every 500 simulation step.
![IMAGE ALT TEXT HERE](https://github.com/alevani/master_project/blob/main/assets/stress-test-result.png)