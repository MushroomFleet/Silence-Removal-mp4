#!/usr/bin/env python3
"""
silence_removal.py - A tool to remove silent sections from videos.

This script detects silent sections in videos below a defined threshold (default 0.5 dB)
and removes segments that are longer than a defined length (default 0.5 seconds).
"""

import os
import json
import time
from datetime import datetime
from typing import List, Tuple
from moviepy.editor import VideoFileClip
from pydub import AudioSegment
from pydub.silence import detect_nonsilent

def load_config(config_path: str = "config.json") -> dict:
    """
    Load configuration from config.json file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Dictionary containing configuration values
    """
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Set default values if not present
        if 'silence_threshold' not in config:
            # Default is 0.5 dB as specified in requirements.
            # For pydub, silence is detected using negative values,
            # so we convert this to a suitable negative threshold.
            config['silence_threshold'] = -50  
        elif config['silence_threshold'] > 0:
            # If the threshold was specified as a positive value in the config,
            # convert it to a negative value suitable for pydub
            print(f"Converting positive silence threshold {config['silence_threshold']} dB to negative value for detection")
            config['silence_threshold'] = -abs(config['silence_threshold'] * 100)
            
        if 'min_silence_length' not in config:
            config['min_silence_length'] = 0.5  # seconds
        if 'output_path' not in config and 'input_path' in config:
            config['output_path'] = os.path.dirname(config['input_path'])
            
        return config
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found at {config_path}")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON format in configuration file at {config_path}")

def get_silent_segments(audio_file: str, silence_threshold: float, min_silence_length: float) -> List[Tuple[float, float]]:
    """
    Detect silent segments in the audio.
    
    Args:
        audio_file: Path to the audio file
        silence_threshold: Threshold in dB for silence detection (negative value)
        min_silence_length: Minimum length of silence to consider (in seconds)
        
    Returns:
        List of tuples containing (start_time, end_time) of silent segments
    """
    # Load audio
    audio = AudioSegment.from_file(audio_file)
    
    # Convert minimum silence length to milliseconds
    min_silence_ms = int(min_silence_length * 1000)
    
    # Detect non-silent parts
    non_silent_ranges_ms = detect_nonsilent(
        audio,
        min_silence_len=min_silence_ms,
        silence_thresh=silence_threshold
    )
    
    # Convert to seconds
    non_silent_ranges = [(start/1000, end/1000) for start, end in non_silent_ranges_ms]
    
    # Calculate silent segments as gaps between non-silent parts
    silent_segments = []
    
    # Add silence at the beginning if needed
    if non_silent_ranges and non_silent_ranges[0][0] > 0:
        silent_segments.append((0, non_silent_ranges[0][0]))
    
    # Add silence between non-silent parts
    for i in range(len(non_silent_ranges) - 1):
        silent_segments.append((non_silent_ranges[i][1], non_silent_ranges[i+1][0]))
    
    # Add silence at the end if needed
    audio_length_sec = len(audio) / 1000
    if non_silent_ranges and non_silent_ranges[-1][1] < audio_length_sec:
        silent_segments.append((non_silent_ranges[-1][1], audio_length_sec))
    
    # Filter out silent segments that are shorter than the minimum length
    silent_segments = [(start, end) for start, end in silent_segments 
                      if end - start >= min_silence_length]
    
    return silent_segments

def create_subclip(video, start_time, end_time):
    """
    Create a subclip from a video between start_time and end_time.
    
    Args:
        video: VideoFileClip object
        start_time: Start time in seconds
        end_time: End time in seconds
        
    Returns:
        A new VideoFileClip that is a subclip of the original
    """
    # Use the built-in subclip method now that we have the right moviepy version
    return video.subclip(start_time, end_time)

def remove_silence_from_video(video_path: str, silent_segments: List[Tuple[float, float]], output_path: str) -> None:
    """
    Remove silent segments from the video and save the result.
    
    Args:
        video_path: Path to the input video
        silent_segments: List of (start, end) tuples representing silent segments
        output_path: Path where to save the output video
    """
    # Load the video
    video = VideoFileClip(video_path)
    
    if not silent_segments:
        print("No silent segments to remove.")
        video.write_videofile(output_path, codec="libx264", audio_codec="aac")
        video.close()
        return
    
    # Create a list of segments to keep
    keep_segments = []
    
    # Add segment from start to first silence
    if silent_segments[0][0] > 0:
        keep_segments.append((0, silent_segments[0][0]))
    
    # Add segments between silences
    for i in range(len(silent_segments) - 1):
        keep_segments.append((silent_segments[i][1], silent_segments[i+1][0]))
    
    # Add segment from last silence to end
    if silent_segments[-1][1] < video.duration:
        keep_segments.append((silent_segments[-1][1], video.duration))
    
    # Extract clips to keep using the subclip function
    clips = [video.subclip(start, end) for start, end in keep_segments]
    
    if not clips:
        print("Warning: No segments to keep after removing silence.")
        video.close()
        return
    
    # Concatenate clips
    from moviepy.editor import concatenate_videoclips
    final_clip = concatenate_videoclips(clips)
    
    # Write the result to file
    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
    
    # Close the clips to release resources
    final_clip.close()
    for clip in clips:
        clip.close()
    video.close()

def process_long_video(video_path: str, silence_threshold: float, min_silence_length: float, output_path: str) -> None:
    """
    Process a long video by analyzing audio in chunks but processing video in one pass.
    
    Args:
        video_path: Path to the input video
        silence_threshold: Threshold in dB for silence detection (negative value)
        min_silence_length: Minimum length of silence to consider (in seconds)
        output_path: Path where to save the output video
    """
    # Get video information
    video = VideoFileClip(video_path)
    duration = video.duration
    video.close()
    
    # Process audio in chunks of 10 minutes (600 seconds)
    chunk_size = 600
    chunks = [(i, min(i + chunk_size, duration)) 
              for i in range(0, int(duration), chunk_size)]
    
    # Create temporary directory
    temp_dir = os.path.join(os.path.dirname(output_path), "temp_chunks")
    os.makedirs(temp_dir, exist_ok=True)
    
    all_silent_segments = []
    
    for i, (start, end) in enumerate(chunks):
        print(f"Processing audio chunk {i+1}/{len(chunks)}...")
        
        # Extract audio chunk directly
        temp_audio_path = os.path.join(temp_dir, f"audio_{i}.wav")
        
        # Use the subclip method directly
        video = VideoFileClip(video_path)
        video_chunk = video.subclip(start, end)
        video_chunk.audio.write_audiofile(temp_audio_path)
        video_chunk.close()
        video.close()
        
        # Detect silent segments
        silent_segments = get_silent_segments(temp_audio_path, silence_threshold, min_silence_length)
        
        # Adjust timings to account for chunk start time
        adjusted_segments = [(s + start, e + start) for s, e in silent_segments]
        all_silent_segments.extend(adjusted_segments)
        
        # Clean up temporary files
        os.remove(temp_audio_path)
    
    # Merge overlapping silent segments
    if all_silent_segments:
        all_silent_segments.sort()
        merged_segments = [all_silent_segments[0]]
        
        for segment in all_silent_segments[1:]:
            # If current segment overlaps with the last merged segment
            if segment[0] <= merged_segments[-1][1]:
                # Extend the last merged segment if needed
                merged_segments[-1] = (merged_segments[-1][0], max(merged_segments[-1][1], segment[1]))
            else:
                # Add the current segment as a new merged segment
                merged_segments.append(segment)
    else:
        merged_segments = []
    
    # Process the entire video with merged silent segments
    remove_silence_from_video(video_path, merged_segments, output_path)
    
    # Clean up temporary directory
    try:
        os.rmdir(temp_dir)
    except OSError:
        print(f"Warning: Could not remove temporary directory {temp_dir}")

def main():
    """Main function to coordinate the silence removal process."""
    print("Silence Removal Tool")
    print("-------------------")
    
    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return
    
    # Extract configuration values
    input_path = config.get('input_path')
    output_dir = config.get('output_path')
    silence_threshold = config.get('silence_threshold')
    min_silence_length = config.get('min_silence_length')
    
    if not input_path:
        print("Error: No input path specified in configuration.")
        return
    
    # Check if input file exists
    if not os.path.isfile(input_path):
        print(f"Error: Input file not found at {input_path}")
        return
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create output filename with timestamp
    filename = os.path.basename(input_path)
    name, ext = os.path.splitext(filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"{name}_{timestamp}{ext}"
    output_path = os.path.join(output_dir, output_filename)
    
    print(f"Processing video: {input_path}")
    print(f"Silence threshold: {silence_threshold} dB")
    print(f"Minimum silence length: {min_silence_length} seconds")
    print(f"Output will be saved to: {output_path}")
    
    # Process the video
    start_time = time.time()
    
    # Get video information to determine if it's a long video
    try:
        video = VideoFileClip(input_path)
        duration = video.duration
        video.close()
        
        print(f"Video duration: {duration:.2f} seconds")
        
        # If video is longer than 30 minutes, use the long video processing method
        if duration > 1800:
            print("Detected long video, using chunk-based processing...")
            process_long_video(input_path, silence_threshold, min_silence_length, output_path)
        else:
            # Extract audio to a temporary file
            print("Extracting audio...")
            temp_audio = "temp_audio.wav"
            video = VideoFileClip(input_path)
            video.audio.write_audiofile(temp_audio)
            video.close()
            
            # Detect silent segments
            print("Detecting silent segments...")
            silent_segments = get_silent_segments(temp_audio, silence_threshold, min_silence_length)
            
            print(f"Found {len(silent_segments)} silent segments to remove.")
            
            # Remove temporary audio file
            os.remove(temp_audio)
            
            # Process the video
            print("Processing video...")
            remove_silence_from_video(input_path, silent_segments, output_path)
        
        end_time = time.time()
        print(f"Processing completed in {end_time - start_time:.2f} seconds")
        print(f"Output saved to: {output_path}")
        
    except Exception as e:
        print(f"Error processing video: {e}")

if __name__ == "__main__":
    main()
