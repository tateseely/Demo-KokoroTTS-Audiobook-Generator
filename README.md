# Demo-KokoroTTS-Audiobook-Generator
This is a demo to see how well various hardware could run the Kokoro TTS model. The python scripts were initially generated using ChatGPT, but I modified the code for the Kokoro 82M model found at https://huggingface.co/hexgrad/Kokoro-82M.
There are 2 python scripts; one that extracts the text from a pdf file, the other converting one or more text files into wav audio files. The first script is "pdf-to-chapter-txt.py". If the pdf has an outline, it will divide the extracted text according to the outline. The text files will be saved in a directory with the same filename as the pdf in the same directory as the pdf. To use this script, use the python command followed by the path for the script and then the path for the pdf. To make things easy, I prefer to put the script in the same directory as the pdf and run the script in a terminal like so:

    python pdf-to-chapter-txt.py 'My Book.pdf'

The second python script is "txt-to-wav.py". This script will generate wav files for one or more text files. The arguments are optional. Huggingface has more information about voice options: [VOICES.md · hexgrad/Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md)
Here is how I use it to process one text file:

    python txt-to-wav.py path/to/file.txt --voice af_nova --lang a --speed 1.0

It can also process all of the text files in the directory it is run in:

    python txt-to-wav.py --voice bm_george --lang b --speed 1.0
