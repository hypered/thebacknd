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

  base = import "${toString sources.nixpkgs}/nixos/lib/eval-config.nix" {
    modules = [
      "${toString sources.nixpkgs}/nixos/modules/virtualisation/digital-ocean-image.nix"
      ./machines/base/configuration.nix
    ];
  };

  qemu = import "${toString sources.nixpkgs}/nixos/lib/eval-config.nix" {
    modules = [
      "${toString sources.nixpkgs}/nixos/modules/virtualisation/qemu-vm.nix"
      ./machines/base/configuration.nix
      ./machines/base/no-gui.nix
    ];
  };

  example = import "${toString sources.nixpkgs}/nixos/lib/eval-config.nix" {
    modules = [
      "${toString sources.nixpkgs}/nixos/modules/virtualisation/digital-ocean-image.nix"
      ./machines/base/configuration.nix
      ./machines/example/hello.nix
    ];
  };

  nginx = import "${toString sources.nixpkgs}/nixos/lib/eval-config.nix" {
    modules = [
      "${toString sources.nixpkgs}/nixos/modules/virtualisation/digital-ocean-image.nix"
      ./machines/base/configuration.nix
      ./machines/nginx/nginx.nix
    ];
  };

in rec
  {
    # Build with nix-build -A <attr>
    toplevels.base = base.config.system.build.toplevel;
    toplevels.example = example.config.system.build.toplevel;
    toplevels.nginx = nginx.config.system.build.toplevel;
    image = base.config.system.build.digitalOceanImage;
    runvm = qemu.config.system.build.vm;
    binaries = naersk.buildPackage ./.;

    # A shell to try out our binaries
    # Run with nix-shell default.nix -A shell
    shell = pkgs.mkShell {
      buildInputs = [
        binaries
      ];
      shellHook = ''
        source <(thebacknd --generate bash run)
      '';
    };
  }
