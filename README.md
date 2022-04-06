# Process-tracker
Simple program that iterates over the currently running processes every 5 minutes, currently it checks for 'firefox.exe' but that can be easily changed by swapping the variable 'process'.

If the program was found in the active processes then it marks the time when it was first seen. Once the program is no longer in the active processes (ie program was closed) then it takes the current time minus the start time to get the total time the process was online. Then it uploads that data to a graph on pixela's website. 
