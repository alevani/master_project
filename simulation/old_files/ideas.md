#! It does not seem impossible to have a record button that would save the point. This record button would record idk like
#! 5000 begin and from there on, giving the user a chance to record something he just missed, also without to have to watch
#! it from the begining again



#! It is likely that adding pheromones at every step is wrong. like ant will activate their pheromones only under specific circumstances
#! Do ants have a specific go home or go to food pheromone? if so I can easily add this behaviour by adding a pheromone type in the pheromone object and filtering when matching

# TODO Right now it's funny that I can right and left click but
# TODO ultimately one will have to decide wheter POIs should all be in the same list or
# TODO if they should be in dedicated list (home_pois, task_pois, and so on)
# TODO IF in separated lists, then I can have multiple function for sensing (bottom)
# TODO as if, if robot sense a resource, then he shift to an other sensing function
# TODO that handles to only sense a "home" pois type (maybe there's going to be one home but anyway)
# TODO 'cause if so, then he would avoid resources on its way which is nice I imagine (even though technically new resources shouldn't pop in the middle of a path sinc the path already has been covered by the ant...)
# TODO because it's cheaper to have two list than one list and O(n + 1) each iteration
# TODO like .. if it searches for home no need to check in the resource list :)

#! one need to fix: the way robot behave on pheromone, they should be able to take 90 degree angle
#! and also CIRCLE OF DEATH