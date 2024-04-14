let
  sources = import ./nix/sources.nix;
  nixpkgs = import sources.nixpkgs {};

  qemu = import "${toString sources.nixpkgs}/nixos/lib/eval-config.nix" {
    modules = [
      "${toString sources.nixpkgs}/nixos/modules/virtualisation/qemu-vm.nix"
      ./machine/configuration.nix
      ./machine/no-gui.nix
    ];
  };

in rec
  {
    # Build with nix-build -A <attr>
    runvm = qemu.config.system.build.vm;
  }
