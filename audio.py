import os
import sys
import threading
import sounddevice as sd
import soundfile as sf
import numpy as np
from typing import Optional

class NativeAudioPlayer:
    def __init__(self, file_path: str):
        self.file_path = os.path.expanduser(file_path)
        
        self.data: Optional[np.ndarray] = None
        self.fs: Optional[int] = None
        self.stream: Optional[sd.OutputStream] = None
        
        # Playback control states
        self.current_frame = 0
        self.is_playing = False
        self.event = threading.Event()

    def load_file(self) -> bool:
        if not os.path.exists(self.file_path):
            print(f"Error: File not found at '{self.file_path}'")
            return False
        try:
            # Read the audio file into a NumPy array
            self.data, self.fs = sf.read(self.file_path, always_2d=True)
            return True
        except Exception as e:
            print(f"Error loading audio file: {e}")
            self.data = None
            self.fs = None
            return False

    def _callback(self, outdata: np.ndarray, frames: int, time: list, status: sd.CallbackFlags) -> None:
        """Internal audio buffer feeding callback."""
        if status:
            print(status, file=sys.stderr)
        
        if self.data is None:
            outdata[:] = 0
            raise sd.CallbackStop
        
        chunksize = min(len(self.data) - self.current_frame, frames)
        
        if chunksize > 0:
            outdata[:chunksize] = self.data[self.current_frame:self.current_frame + chunksize]
            outdata[chunksize:] = 0
            self.current_frame += chunksize
        else:
            outdata[:] = 0
            raise sd.CallbackStop

    def play(self) -> None:
        if self.data is None or self.fs is None:
            print("Error: Cannot play. No audio data loaded.")
            return

        if not self.is_playing:
            if self.stream is not None:
                self.stream.close()

            self.is_playing = True
            
            self.stream = sd.OutputStream(
                samplerate=self.fs, 
                channels=self.data.shape[1],
                callback=self._callback, 
                finished_callback=self.event.set
            )
            self.stream.start()
            print("Playback Started.")

    def pause(self) -> None:
        if self.is_playing and self.stream is not None:
            self.stream.stop()
            self.is_playing = False
            print("Playback Paused.")

    def resume(self) -> None:
        if not self.is_playing and self.data is not None:
            if self.stream is not None:
                self.stream.start()
                self.is_playing = True
                print("Playback Resumed.")
            else:
                self.play()

    def stop(self) -> None:
        if self.stream is not None:
            self.stream.close()
            self.stream = None # Completely dump the stream object reference
        self.is_playing = False
        self.current_frame = 0
        print("Playback Stopped.")

    def is_active(self) -> bool:
        if self.data is None:
            return False
        return self.current_frame < len(self.data)

def main():
    TRACK_PATH = "~/Music/Milk & Kisses/01 - Violaine.mp3"
    
    player = NativeAudioPlayer(TRACK_PATH)
    
    if not player.load_file():
        print("Initialization failed. Exiting.")
        return

    player.play()

    print("\n=======================================")
    print("  Controls: [p] Pause  [r] Resume  [s] Stop")
    print("=======================================")

    while player.is_active():
        try:
            command = input("\nEnter control command: ").strip().lower()
            if command == 'p':
                player.pause()
            elif command == 'r':
                player.resume()
            elif command == 's':
                player.stop()
                break
        except (KeyboardInterrupt, SystemExit):
            break

    player.stop()
    print("Goodbye!")

if __name__ == "__main__":
    main()
