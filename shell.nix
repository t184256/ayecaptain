{ pkgs ? import <nixpkgs> { } }:
with pkgs;
mkShell {
  buildInputs = [
    (python3.withPackages (ps: with ps; [
      numpy
      scipy
      cairo
      pygobject3
    ]))
    gnome3.gtk
    gobjectIntrospection
  ];
}
