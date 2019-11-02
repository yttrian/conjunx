# conjunx
An automated TTS tool for tagged source videos

Made during the 24 hour [UB Hacking](https://www.ubhacking.com/) 2019 Hackathon

## How it works

1. A .cjxa file is created using a conjunx compatible editor
 - These files are compressed archives containing both source video files and transcripts
2. A request is made to the render server with the .cjx and a desired dictation to be created
3. The render server sends back the processed video file

## .cjxc caption file description

The first line of a caption file is the name of the video it refers to. 
All the following lines are a word/phrase, a starting timestamp, and an ending timestamp (in second + milliseconds)

For example:
```
Jeff Kaplan Responds to IGNs Overwatch Comments.mp4
so,4.833,5.051
a lot of,5.051,5.264
people,5.264,5.547
think,5.547,5.896
nobody,5.913,6.310
ever,6.332,6.611
reads,6.606,6.972
these,6.981,7.395
```