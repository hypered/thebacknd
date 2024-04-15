let
  sources = import ./nix/sources.nix;
  nixpkgs = import sources.nixpkgs {};

  os = import "${toString sources.nixpkgs}/nixos/lib/eval-config.nix" {
    modules = [
      "${toString sources.nixpkgs}/nixos/modules/virtualisation/digital-ocean-image.nix"
      ./machine/configuration.nix
    ];
  };

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
    toplevel = os.config.system.build.toplevel;
    image = os.config.system.build.digitalOceanImage;
    runvm = qemu.config.system.build.vm;
  }
