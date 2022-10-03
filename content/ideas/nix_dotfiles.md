- https://news.ycombinator.com/item?id=21054462
Imperative vs declarative configuration

**Benefits:**
  - Parameterized (esp. multi-platform)
  - Config includes packages (always user-local)
  - Includes services
  - Type-safety (minimal)

**Downsides:**
  - Home manager doesn't support your config file?
  - Home manager doesn't support that option
  - 2-step reload

https://ghedam.at/24353/tutorial-getting-started-with-home-manager-for-nix
  Intro
  Up/downsides
https://hugoreeves.com/posts/2019/nix-home/
  Multi-machine, multi-user, multi-platform config
https://www.malloc47.com/migrating-to-nixos/
  Intro to NixOS

(as a user other than root with sudo permission) 
curl -L https://nixos.org/nix/install | sh

Supported things:
- SSH config
- Emacs
- User-level systemd units
- Put stuff on the $PATH
- Install package
