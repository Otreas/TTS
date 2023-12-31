"# TTS" 

webui tested with python 3.10.6 

How to use:
 - install necessary python modules via command:
            pip install -r requirements.txt
 - run start.bat
 - If it is the first time running the program, it will download AI models for openai-whisper and coqui-ai


 Disclaimer:
 - The model I used for speech recognition is openai's large whisper model. If you value your computer's memory, i suggest you to switch it to base
    How do you do it?
        Open app.py in a text editor.
        change line 20 from this:
            whispermodel = whisper.load_model("large")
        to this:
            whispermodel = whisper.load_model("base")
    It will save around 2.5GB of memory.

    These models are multilingual, if you wish to have the speech recognition only in english, you can change it to "base.en", or any other model listed available on : https://github.com/openai/whisper

    I did not write any code for AI models or speech recognition, I just compiled them into a /kind of/ user friendly experience.