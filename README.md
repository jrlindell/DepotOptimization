# DepotOptimization

## Data

52 planes, 4 bases, 445 months

### Data Example
Tail Number	Owning Base	  Model	Scheduled Start Date	Depot Length (d)	Actual Start	Forecasted Finish
1	            D	           C-X	      9/8/1998	            295	          7/7/1998	      1/1/2000
2	            W	           C-X	      11/7/1998	            295	          10/27/1998	    2/1/2000
3	            W	           C-X	      1/6/1999	            295	          12/27/1998	    3/2/2000
4	            T	           C-X	      3/7/1999	            295	          8/30/1998	      1/1/2000
5	            T	           C-X	      5/6/1999	            295	          3/6/1999	      4/2/2000
6	            D	           C-X	      7/5/1999	            295	          8/16/1999	      6/6/2000
7	            T	           C-X	      9/3/1999	            295	          6/12/1999	      5/3/2000
8	            D	           C-X	      11/2/1999	            295	          10/26/1999	    8/16/2000

#### Minimum Required at each base for each month
Base	Min Req
1	      6
2	      15
3	      6
4	      16

#### Minimum Owned for each base (includes depot data)
Base	Min Owned
1	      6
2	      14
3	      6
4	      15

## Goal
The goal of this optimization is to meet the minimum required at each base for every month (445) taking into account the planes that are
scheduled to be at base, shown in the Data Example above. If a plane from Base D goes to depot, a base with an excess of planes (more
planes than required) will send a plane to that base. We are taking that into account, and minimizing the amount of planes that move
from one base to another; minimize the unnecessary amount of flights per month

## Output
