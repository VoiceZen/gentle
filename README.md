# Gentle
**Robust yet lenient forced-aligner built on Kaldi. A tool for aligning speech with text.**

## Getting Started

There are three ways to install Gentle.

1. Download the [pre-built Mac application](https://github.com/lowerquality/gentle/releases/latest). This package includes a GUI that will start the server and a browser. It only works on Mac OS.

2. Use the [Docker](https://www.docker.com/) image. Just run ```docker run -P lowerquality/gentle```. This works on all platforms supported by Docker.

3. Download the source code and run ```./install.sh```. Then run ```python3 serve.py``` to start the server. This works on Mac and Linux.

## Using Gentle

By default, the aligner listens at http://localhost:8765. That page has a graphical interface for transcribing audio, viewing results, and downloading data.

There is also a REST API so you can use Gentle in your programs. Here's an example of how to use the API with CURL:

```bash
curl -F "audio=@audio.mp3" -F "transcript=@words.txt" "http://localhost:8765/transcriptions?async=false"
```

If you've downloaded the source code you can also run the aligner as a command line program:

```bash
git clone https://github.com/lowerquality/gentle.git
cd gentle
./install.sh
python3 align.py audio.mp3 words.txt
```

The default behaviour outputs the JSON to stdout.  See `python3 align.py --help` for options.

## Using Gentle for a batch of audios and save the output

Gentle could also be run for a batch of audios and the output would be saved as .json file.

The sound file and transcript files are saved in separate folders. (e.g. sound files are at `datasetA/wavs` and transcripts are at `datasetA/txt`)

The name of text files should be aligned with the wavs; meaning the text file corresponding to a wav file should have the same name. The notebook named [make_data_for_webalign.ipynb](make_data_for_webalign.ipynb) can be referred for this.

Example:
```bash
python align_batch.py --wav_pattern="datasetA/wavs/*.wav" --txt_pattern="datasetA/txt/*.txt" --output_dir temp/
```
Here, we have given the wave and text file patterns. The output directory which saves the json output is also provided.
See `python3 align_batch.py --help` for options.
