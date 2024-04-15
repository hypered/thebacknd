{ config, lib, pkgs,
  ... }:
{
  services.sshd.enable = true;

  users.users.root = {
    password = "nixos";
  };

  services.openssh.settings.PermitRootLogin = lib.mkDefault "yes";
  services.getty.autologinUser = lib.mkDefault "root";

  imports = [
    ./scripts.nix
  ];
}
