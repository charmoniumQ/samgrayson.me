https://github.com/charmoniumQ/scope_timer
cons of gprof:
	- measures everything, could have overhead
	- no information on dynamic arguments
	- captures caller of thread-launch
caveats:
	- no recursion
	- **not for optimization**; for component comparison in a system
		- Not answering "how to make faster system with same components at a low-level?"; answering "which components take the most CPU time?"; answering "what's the end-to-end latency in my system?"
Improvements:
	- Switchboard communicates its serial number
	- Also have integer-comments
	- Bloat-free (standardized?) binary file format
Compare overhead per funccall
perf, poormansprofiler, operf, gprof
http://poormansprofiler.org/
https://stackoverflow.com/questions/1777556/alternatives-to-gprof/1779343#1779343
https://oprofile.sourceforge.io/examples/
https://stackoverflow.com/questions/375913/how-can-i-profile-c-code-running-on-linux/378024#378024
