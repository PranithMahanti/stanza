import audio
import database

import os
from pathlib import Path
import tinytag

def getAllMusicFiles(mainPath):
    items = [{"dir": dirpath, "name":f} for dirpath, dirnames, filenames in os.walk(os.path.expanduser(mainPath)) 
            for f in filenames]   
    return items

def getMetadata(mainPath):
    tag = tinytag.TinyTag.get(mainPath)
    data = {
        "title": tag.title,
        "artist": tag.artist,
        "album": tag.album, 
        "genre": tag.genre,
        "year": tag.year,
        "composer": tag.composer,
        "duration": tag.duration,
        "bitrate": tag.bitrate
    }
    return data

if __name__ == "__main__":
    music = getAllMusicFiles("~/Music/")
    #for i in music:
    #    print(getMetadata(os.path.join(i['dir'], i['name'])))
    
    print(f"{music[0]['dir']}{music[0]['name']}")
    player = audio.NativeAudioPlayer(os.path.join(music[0]['dir'], music[0]['name']))
    
    if player.load_file():  
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

