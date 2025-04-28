from kokoro import KPipeline
from IPython.display import display, Audio
import soundfile as sf
import argparse
import os
import numpy as np
import torch
import glob 

# Example use in terminal: 
# Single file: python txt-to-wav.py path/to/file.txt --voice af_nova --lang a --speed 1.0
# All .txt files: python txt-to-wav.py --voice af_nova --lang a --speed 1.0

def narrate_text_file(file_path, voice='af_bella', lang_code='a', speed=1, use_cuda=True):
    # (Existing function body remains unchanged)
    device = torch.device("cuda" if torch.cuda.is_available() and use_cuda else "cpu")
    print(f"Using device: {device}")
    
    if device.type == 'cuda':
        cuda_version = torch.version.cuda
        print(f"CUDA version: {cuda_version}")
        if cuda_version != '12.6':
            print(f"Warning: Current CUDA version is {cuda_version}, not 12.6")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_file = f"{base_name}.wav"
    
    pipeline = KPipeline(lang_code=lang_code, device=device)
    
    generator = pipeline(
        text, voice=voice,
        speed=speed, split_pattern=r'\n+'
    )
    
    all_audio = []
    for i, (gs, ps, audio) in enumerate(generator):
        print(f"Processing chunk {i}:")
        print(f"Text: {gs}")
        all_audio.append(audio)
    
    combined_audio = np.concatenate(all_audio)
    
    sf.write(output_file, combined_audio, 24000)
    print(f"Narration saved to {output_file}")
    
    return Audio(data=combined_audio, rate=24000)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Narrate text files and save as a WAV.')
    parser.add_argument('file_path', nargs='?', default=None, 
                       help='Path to a specific text file. If omitted, processes all .txt files in the directory.')
    parser.add_argument('--voice', default='af_bella', help='Voice to use for narration')
    parser.add_argument('--lang', default='a', choices=['a', 'b'], 
                        help='Language code: "a" for American English, "b" for British English')
    parser.add_argument('--speed', type=float, default=1.0, help='Speech speed')
    
    args = parser.parse_args()
    
    # Find txt files to process
    if args.file_path:
        files_to_process = [args.file_path]
    else:
        files_to_process = glob.glob("*.txt")
        if not files_to_process:
            print("No txt files found in the current directory.")
            exit()
    
    # Process each txt file
    for file_path in files_to_process:
        print(f"\nProcessing file: {file_path}")
        narrate_text_file(file_path, args.voice, args.lang, args.speed, not args.no_cuda)