{ pkgs, ... }:
let
current-system = pkgs.runCommandLocal "current-system" {
  script = ../scripts/current-system.sh;
  nativeBuildInputs = [ pkgs.makeWrapper ];
} ''
  makeWrapper $script $out/bin/current-system \
    --prefix PATH : ${pkgs.lib.makeBinPath []}
'';

desired-system = pkgs.runCommandLocal "desired-system" {
  script = ../scripts/desired-system.sh;
  nativeBuildInputs = [ pkgs.makeWrapper pkgs.curl ];
} ''
  makeWrapper $script $out/bin/desired-system \
    --prefix PATH : ${pkgs.lib.makeBinPath []}
'';

destroy-system = pkgs.runCommandLocal "destroy-system" {
  script = ../scripts/destroy-system.sh;
  nativeBuildInputs = [ pkgs.makeWrapper pkgs.curl pkgs.jq ];
} ''
  makeWrapper $script $out/bin/destroy-system \
    --prefix PATH : ${pkgs.lib.makeBinPath []}
'';

update-system = pkgs.runCommandLocal "update-system" {
  script = ../scripts/update-system.sh;
  nativeBuildInputs = [ pkgs.makeWrapper pkgs.curl ];
} ''
  makeWrapper $script $out/bin/update-system \
    --prefix PATH : ${pkgs.lib.makeBinPath []}
'';

in
{
  environment.systemPackages = [
    current-system
    desired-system
    destroy-system
    update-system
    pkgs.jq
  ];
}
