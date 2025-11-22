# Demo videos
Generating by using SSR to record output from the debug script

Concert the mkv files with this command
```
ffmpeg -i clock.mkv -vf "fps=15,scale=640:-1:flags=lanczos" -loop 0 clock.gif
```
