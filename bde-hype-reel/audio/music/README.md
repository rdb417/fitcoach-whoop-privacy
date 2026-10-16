Drop the licensed track here as `track.wav` (or .flac/.mp3/.m4a) and re-render.
It replaces the synthesised music bus; SFX, ducking and the silence beat stay.
Set the in-point per cut in `reel/audio.py` (`MUSIC_OFFSET`). If its tempo
differs from 96 BPM, retime shots 4 to 10 in `reel/edl.py` to its beat grid.
