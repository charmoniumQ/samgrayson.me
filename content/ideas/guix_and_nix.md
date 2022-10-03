Functional Package Management
	Hardware-level virtualization
		Xen, KVM, Qemu
		Paravirtualization involves modifying the guest a little.
	OS-level virtualization
		That has too much overhead; build in isolation techniques into the OS
		Docker, but also FreeBSD jail
		https://leftasexercise.com/2018/04/12/docker-internals-process-isolation-with-namespaces-and-cgroups/
	Maybe that's still too much? Docker images are fat, take forever to build, and aren't actually deterministic.
	Environment-level virtualization
		Same FS, but PATH and LD_LIBRARY_PATH are automatically set by $PACKAGE_MANAGER for different uses.
		Multiple profiles, different versions of the software coexist, but still reuse where possible
		Deterministic (name has hash of inputs)
		Cache builds
		Distribute software systems https://www.mpscholten.de/docker/2016/01/27/you-are-most-likely-misusing-docker.html
		Declarative
		Roll-back
		Cons:
			Learning curve
			Disk and CPU utilization
			https://hands-on.cloud/why-you-should-never-ever-use-nixos/
Guix vs Nix?
	https://news.ycombinator.com/item?id=16490027
	Scheme > Nix lang
	Nix has more pkgs
	Static types
	Parameterized packages
	Both have fantastic communities
	Guix can import Nix packages, but not the other way around. I think this is due to Guix's lazy-evaluation.
	More tools (`guix lint` checks for CVEs, `guix graph` shows you a graph of packages)
	More complete documentation (no Nix pills)
	Guix has no devops (although it's coming https://guix.gnu.org/blog/2019/towards-guix-for-devops/)
Guix problems
	Packages not already existing
	Even if already exist, may need to write a new one for configuration
	Not too bad; Writing recipes is easy, isn't it?
Guile problems
	Lisp makes it easy to hack the language. The macro system permits one to manipulate the AST. Cite BeautifulRacket. That is simultaneously its power and its downfall. Everyone and their mother has a syntax manipulation macro.
		Interpreting syntax has dynamic-scope vs local-scope. I couldn't find a way to pass a variable defined in enclosing scope to a package.
	Imports bind names into the global namespace (from blah import *). Binding to a namespace is possible, but not the default. When I want to see how some symbol works, and I can't statically locate its definition.
