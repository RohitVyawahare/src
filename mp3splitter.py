# Download ffmpeg and compile
# install pydub - pip install pydub (https://github.com/jiaaro/pydub)
# run python mp3splitter.py

from pydub import AudioSegment
from pydub.silence import split_on_silence

sound = AudioSegment.from_mp3("latest.mp3") # mp3 file path


chunks = split_on_silence(sound, 
    # must be silent for 3 secs
    min_silence_len=3000,

    # consider it silent if quieter than 25 dBFS
    silence_thresh=-25
)

for i, chunk in enumerate(chunks):
    chunk.export("chunk{0}.mp3".format(i), format="mp3")

# EOF