{ config, lib, pkgs,
  ... }:
let
  scripts = import ./scripts.nix { inherit pkgs; };
in
{
  services.sshd.enable = true;

  users.users.root = {
    password = "nixos";
  };

  services.openssh.settings.PermitRootLogin = lib.mkDefault "yes";
  services.getty.autologinUser = lib.mkDefault "root";

  systemd.services.update-system = {
    after = [ "network-online.target" ];
    requires = [ "network-online.target" ];
    wantedBy = [ "multi-user.target" ];
    restartIfChanged = false;
    serviceConfig = {
      Type = "oneshot";
      ExecStart = "${scripts.update-system}/bin/update-system";
    };
  };

  environment.systemPackages = [
    scripts.current-system
    scripts.desired-system
    scripts.destroy-system
    scripts.update-system
    pkgs.jq
  ];
}
