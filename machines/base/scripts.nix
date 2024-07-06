{ pkgs }:
let
current-system = pkgs.runCommandLocal "current-system" {
  script = ../../scripts/current-system.sh;
  nativeBuildInputs = [ pkgs.makeWrapper ];
} ''
  makeWrapper $script $out/bin/current-system \
    --prefix PATH : ${pkgs.lib.makeBinPath []}
'';

desired-system = pkgs.runCommandLocal "desired-system" {
  script = ../../scripts/desired-system.sh;
  nativeBuildInputs = [ pkgs.makeWrapper pkgs.curl system-input ];
} ''
  makeWrapper $script $out/bin/desired-system \
    --prefix PATH : ${pkgs.lib.makeBinPath []}
'';

destroy-system = pkgs.runCommandLocal "destroy-system" {
  script = ../../scripts/destroy-system.sh;
  nativeBuildInputs = [ pkgs.makeWrapper pkgs.curl pkgs.jq system-input ];
} ''
  makeWrapper $script $out/bin/destroy-system \
    --prefix PATH : ${pkgs.lib.makeBinPath []}
'';

update-system = pkgs.runCommandLocal "update-system" {
  script = ../../scripts/update-system.sh;
  nativeBuildInputs = [ pkgs.makeWrapper system-input ];
} ''
  install -m755 $script -D $out/bin/update-system
  patchShebangs $out/bin/update-system
  wrapProgram $out/bin/update-system \
    --prefix PATH : ${pkgs.lib.makeBinPath [ pkgs.curl pkgs.jq pkgs.nix system-input ]}
'';

system-input = pkgs.runCommandLocal "system-input" {
  script = ../../scripts/system-input.sh;
  nativeBuildInputs = [ pkgs.makeWrapper pkgs.curl pkgs.jq ];
} ''
  install -m755 $script -D $out/bin/system-input
  patchShebangs $out/bin/system-input
  wrapProgram $out/bin/system-input \
    --prefix PATH : ${pkgs.lib.makeBinPath [ pkgs.curl pkgs.jq ]}
'';

in
{
  inherit
    current-system
    desired-system
    destroy-system
    update-system
    system-input
    ;
}
