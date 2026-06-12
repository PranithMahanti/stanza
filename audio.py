import os
import sys
import threading
import sounddevice as sd
import soundfile as sf

class NativeAudioPlayer:
    def __init__(self, file_path: str):
        self.file_path = os.path.expanduser(file_path)
        self.data = None
        self.fs = None
        self.stream = None
        
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
            return False

    def _callback(self, outdata, frames, time, status):
        """Internal audio buffer feeding callback."""
        if status:
            print(status, file=sys.stderr)
        
        # Calculate how many frames are left to play
        chunksize = min(len(self.data) - self.current_frame, frames)
        
        if chunksize > 0:
            # Feed the next chunk of audio data to the output hardware
            outdata[:chunksize] = self.data[self.current_frame:self.current_frame + chunksize]
            outdata[chunksize:] = 0
            self.current_frame += chunksize
        else:
            # Track is finished
            outdata[:] = 0
            raise sd.CallbackStop

    def play(self):
        if not self.is_playing:
            self.is_playing = True
            # Create an output stream using our tracking callback function
            self.stream = sd.OutputStream(
                samplerate=self.fs, 
                channels=self.data.shape[1],
                callback=self._callback, 
                finished_callback=self.event.set
            )
            self.stream.start()
            print("Playback Started.")

    def pause(self):
        if self.is_playing and self.stream:
            self.stream.stop()
            self.is_playing = False
            print("Playback Paused.")

    def resume(self):
        if not self.is_playing and self.data is not None:
            self.play()

    def stop(self):
        if self.stream:
            self.stream.close()
        self.is_playing = False
        self.current_frame = 0
        print("Playback Stopped.")

    def is_active(self) -> bool:
        # Returns True if the track isn't finished yet
        return self.current_frame < len(self.data)

def main():
    TRACK_PATH = "/home/promethei/Music/Milk & Kisses/01 - Violaine.mp3"
    
    player = NativeAudioPlayer(TRACK_PATH)
    if not player.load_file():
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
