# 🔇 Video Silence Removal Tool 🎬

A Python-based tool that automatically detects and removes silent sections from videos!

## 🌟 What is this?

This is a specialized video editing tool that analyzes audio in video files to automatically identify and cut out silent sections. Perfect for cleaning up recordings, removing dead air from presentations, or tightening up video content! ✨

## 🎯 What does it do?

- 🔍 Detects silent segments in videos based on a configurable audio threshold
- ✂️ Automatically cuts out silent sections that exceed a minimum duration
- 🧩 Seamlessly joins the remaining sections into a clean, silence-free video
- ⏱️ Saves time by eliminating the need for manual editing
- 📊 Works efficiently even with longer videos through chunk-based processing
- 🔄 Preserves video quality while reducing file size

## 🛠️ How to Install

### Prerequisites

- 🐍 Python 3.6 or higher
- 🎥 FFmpeg (will be installed via the dependencies)

### Windows Installation (Super Easy! 🚀)

1. Clone or download this repository to your local machine
2. Run `install.bat` by double-clicking on it
3. Wait for the magic to happen ✨
4. The script will automatically install all required dependencies

### Manual Installation (For the Tech-Savvy 🤓)

1. Clone or download this repository
2. Open a terminal/command prompt in the repository directory
3. Run: `pip install -r requirements.txt`

## 📝 How to Use

1. **Configure the tool** 🔧
   - Open `config.json` in any text editor
   - Set the `input_path` to the path of your video file
   - Set the `output_path` to your desired output directory
   - Optionally adjust the `silence_threshold` (default: 0.5 dB) and `min_silence_length` (default: 0.5 seconds)

2. **Run the tool** 🏃‍♂️
   - Double-click on `silence_removal.py` or
   - Run from command line: `python silence_removal.py`

3. **Enjoy your edited video!** 🎉
   - The output file will be saved with the original filename plus a timestamp
   - No more awkward silences! 🙌

## ⚙️ Configuration Options

```json
{
  "input_path": "/path/to/your/video.mp4",
  "output_path": "/path/to/output/directory",
  "silence_threshold": 0.5,
  "min_silence_length": 0.5
}
```

- `input_path`: 📁 Path to your input video file
- `output_path`: 📂 Directory where processed videos will be saved
- `silence_threshold`: 🔈 Audio level (in dB) below which sound is considered silence
- `min_silence_length`: ⏱️ Minimum duration (in seconds) of silence needed to trigger removal

## 🌈 Tips & Tricks

- 🔊 For videos with background noise, try increasing the `silence_threshold` value
- ⏳ For removing only longer pauses, increase the `min_silence_length` value
- 🎵 This tool preserves audio quality in the non-silent sections
- 🚀 Processing time depends on video length and complexity
- 📱 Works great for creating social media clips from longer content!
- 🎙️ Perfect for cleaning up podcast recordings!

## 👨‍💻 Technical Details

The silence removal process works in these steps:
1. 📂 Load video file from the path specified in config.json
2. 🔊 Extract audio and analyze it to detect silent segments
3. ✂️ Create clips from the non-silent parts of the video
4. 🔄 Concatenate these clips together
5. 💾 Save the final video with a timestamp appended to the filename

For longer videos, the tool uses a chunk-based approach to efficiently process the audio without excessive memory usage! 🧠

## 🐞 Troubleshooting

- 🤔 Having issues? Make sure you have the correct paths in config.json
- 😱 Error with audio processing? Ensure you have FFMPEG installed on your system
- 📈 Out of memory? Try processing shorter videos or adjusting your chunk size
- 🤓 Need more help? Check the error messages for clues!

## 📄 License

This project is free to use! Share it with your friends! 🎁

## 🙏 Acknowledgements

- Built with ❤️ using [MoviePy](https://zulko.github.io/moviepy/) and [PyDub](https://github.com/jiaaro/pydub)
- Special thanks to 🧙‍♂️ Python for making this possible!

Enjoy your clean, silence-free videos! 🎥✨