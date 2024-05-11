let
  sources = import ./nix/sources.nix;
  nixpkgs-mozilla = import sources.nixpkgs-mozilla;
  pkgs = import sources.nixpkgs {
    overlays = [
      nixpkgs-mozilla
    ];
  };

  toolchain = pkgs.latest.rustChannels.nightly.rust;

  naersk = pkgs.callPackage sources.naersk {
    cargo = toolchain;
    rustc = toolchain;
  };

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
    binaries = naersk.buildPackage ./.;

    # A shell to try out our binaries
    # Run with nix-shell default.nix -A shell
    shell = pkgs.mkShell {
      buildInputs = [
        binaries
      ];
    };
  }
