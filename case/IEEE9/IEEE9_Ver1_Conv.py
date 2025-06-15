# This file contains the conversion commands of the PSSE Case. For more help, check examples about why and how to convert the components

psspy.fdns([1,0,1,1,1,0,99,0]) # apply fixed slope decoupled NR power flow calc.
psspy.cong(0) # Convert generators
psspy.conl(0,1,1,[0,0],[50.0,30.0,40.0,20.0]) # Convert load 1
psspy.conl(0,1,2,[0,0],[50.0,30.0,40.0,20.0]) # Convert load 2
psspy.conl(0,1,3,[0,0],[50.0,30.0,40.0,20.0]) # Convert load 3
# psspy.conl(0,1,3,[0,0],[50.0,30.0,40.0,20.0]) # Convert load 3
psspy.ordr(0)
psspy.fact()
psspy.tysl(0)
psspy.tysl(0)
