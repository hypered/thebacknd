{ config, lib, pkgs, ... }:
{
  networking.firewall.allowedTCPPorts = [ 80 ];

  services.nginx = {
    enable = true;
    recommendedGzipSettings = true;
    virtualHosts."example.com" = {
      locations = {
        "/" = {
          extraConfig = "return 200 \"Thebacknd Nginx example.\";";
        };
      };
    };
  };
}
