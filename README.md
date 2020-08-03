# Depot Optimization
The goal of this project was to determine the best routes and times to send airplanes to the depot, given we know their general maintenance schedule. The Air Force bases need to have a specific number of airplanes at their base at a given time, so they were spending a lot of money unnecessarily by flying plane 1 from base A to base B for a few weeks, and then flying that plane back to base A for a few weeks, then to depot, etc.

We broke it down into minimizing the amount of unnecessary flights taken by minimizing the amount of plane swaps, and the amount of slack planes being used.

Below I tried to show some examples of the data
## Data

52 planes, 4 bases, 445 months

### Data Example
```
Tail Number	Owning Base	  Model	Scheduled Start Date	Depot Length (d)	Actual Start	Forecasted Finish
1	            D	           C-X	      9/8/1998	            295	          7/7/1998	        1/1/2000
2	            W	           C-X	      11/7/1998	            295	          10/27/1998	      2/1/2000
3	            W	           C-X	      1/6/1999	            295	          12/27/1998	      3/2/2000
4	            T	           C-X	      3/7/1999	            295	          8/30/1998	        1/1/2000
5	            T	           C-X	      5/6/1999	            295	          3/6/1999	        4/2/2000
6	            D	           C-X	      7/5/1999	            295	          8/16/1999	        6/6/2000
7	            T	           C-X	      9/3/1999	            295	          6/12/1999	        5/3/2000
8	            D	           C-X	      11/2/1999	            295	          10/26/1999	      8/16/2000
```

#### Minimum Required at each base for each month
```
Base	Min Req
1	      6
2	      15
3	      6
4	      16
```

#### Minimum Owned for each base (includes depot data)
```
Base	Min Owned
1	      6
2	      14
3	      6
4	      15
```

## Optimization
Minimize the plane swaps and the use of slack planes
### Constraints
1.	Assign each tail to one base movement path every time period
2.	The sum of tails and slack tails not in depot from each base must be at least as large as the minimum possession parameter for every time period.
3.	The number of tails owned by a base must exactly equal the owned parameter for each time period
4.	Planes in depot when needed
5.	Tails must enter their initial possessing base on time period 0.
6.	The ending base of the current time period’s base movement path turned on for tail n must equal the starting base of the next time period’s base movement path turned on for tail n. This ties together base possessions over time. This constraint holds for all time periods before the final time period.
7.	This ties time periods together like constraint 6. But for the final time period.
8.	y is binary. Either the base movement path is assigned for tail n in time period t or it is not.
9.	s is binary. Either the base movement path is assigned for slack tail m in time period t or it is not.




## Goal
The goal of this optimization is to meet the minimum required at each base for every month (445) taking into account the planes that are
scheduled to be at base, shown in the Data Example above. If a plane from Base D goes to depot, a base with an excess of planes (more
planes than required) will send a plane to that base. We are taking that into account, and minimizing the amount of planes that move
from one base to another; minimize the unnecessary amount of flights per month

## Output
The output is when planes move from one base to another, including the depot. This optimization was taken to a C5 conference and saved $1.9B in maintenance realignment over 30 years, and $366M in flight hours for the C5. 
