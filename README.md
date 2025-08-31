## video-trimmer

A simple CLI to trim videos with ffmpeg.

### Install and run from anywhere (Linux)

- pipx (recommended)
```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx install .
# New shell may be required to pick up PATH changes
video-trimmer --help
```

- pip user install
```bash
python3 -m pip install --user .
# Ensure ~/.local/bin is on your PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
video-trimmer --help
```

- Run as a module (without installing)
```bash
python3 -m video_trimmer --help
```

- Optional: single-file binary via PyInstaller
```bash
python3 -m pip install pyinstaller
pyinstaller --onefile -n video-trimmer src/video_trimmer/__main__.py
# Move ./dist/video-trimmer to a directory on your PATH, e.g. ~/.local/bin
mv dist/video-trimmer ~/.local/bin/
```

### Usage
```bash
video-trimmer -i input.mp4 -s 10 -e 25
# or interactively (choose file via fuzzy finder)
video-trimmer -s 00:00:10 -e 00:00:25
```

If you omit `-o/--output`, the output name defaults to `name_trim_{start}-{end}{ext}`.

### License

GNU GPL-3.0-or-later. See `LICENSE`.


