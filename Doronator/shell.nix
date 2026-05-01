{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    # Python 3.14 with tkinter
    (python314.withPackages (ps: with ps; [
      tkinter
      jedi-language-server
      pyqt6
      # Add other python packages here
    ]))

    # Language Servers for Helix
    ruff
    # pkgs."jedi-language-server"
    python314Packages.python-lsp-server
    stdenv.cc.cc.lib
    portaudio
    qt6.qtwayland
    zlib
  ];

  LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath (with pkgs; [
    stdenv.cc.cc.lib
    portaudio
    zlib
  ]);
  
  shellHook = ''
    source .venv/bin/activate
    export PATH="$PATH"
    
    echo "🐍 Python 3.14 development shell active"
    echo "Helix LSPs available: ruff, jedi, pylsp"
    
    # Ensure tkinter can find its libraries
    export TK_LIBRARY="${pkgs.tk}/lib/${pkgs.tk.libPrefix}"
    export TCL_LIBRARY="${pkgs.tcl}/lib/${pkgs.tcl.libPrefix}"
  '';
}
