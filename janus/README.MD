### Config
There is only one file that is used as input for the application and it's called `streaming.yml`. This a yaml file that has the following structure:
```
limit_disk_space: maximum amount of bytes that the recordings will occupy
camera:
  <name1>:
    src: "rtsp url to the live stream of the camera"
    rtsp_transport: "tcp" | "udp". Default: "udp". Some rtsp streams don't work on udp. Setting this option to "tcp" might help
    hik:  (Only for hikvision cameras) configuration to connect to the hikvision camera to fetch events and display them in the history page
      url: "http url to the hikvision camera"
      user: "username to login to the camera"
      pass: "password for the username"
  <name2>: ..
  <name3>: ..
  ..
```
Example config:
```
limit_disk_space: 50000000000
camera:
  camera-1:
    src: "rtsp://admin:admin@ipcamera-1:554/Streaming/channels/101"
    rtsp_transport: "udp"
    hik:
      url: "http://ipcamera-1"
      user: "admin"
      pass: "admin"
  camera-2:
    src: "rtsp://admin:admin@ipcamera-1:554/Streaming/channels/102"
    rtsp_transport: "udp"
    hik:
      url: "http://ipcamera-1"
      user: "admin"
      pass: "admin"
  camera-3:
    src: "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov"
    rtsp_transport: "udp"
```
### Run
```
docker run --init --rm -v <path_to_directory_containing_streaming.yml_file>:/opt/streaming -v <path_to_directory_that_will_store_the_recordings>:/opt/static/recordings --net my_net janus
```

### Endpoints
- `/live/<id>` - shows live view of the respective camera. `id` is an int that corresponds to the index of the respective camera in the `streaming.yml`'s camera array (first camera has id 1, second camera id 2 and so on).
- `/static/history.html` - the page where past recordings can be viewed. This page has a few nice features:
  - all cameras play at the same time and keep their time synchronized
  - play speed can be increased or decreased
  - video files can be saved on the device
  - can scroll the time using the timeline panel or the time bar of each video element
  - can disable one or more cameras by clicking on their name in the timeline; also enable them back by pressin `show all`
  - displays events for hikvision cameras only
  - the video elements automatically resize and rearrange to occupy as much of the page as possible
  - can collapse the timeline element to have more space for displaying the recordings

## TODO
- vazut cum detectam ca ffmpeg nu mai inregistreaza sau s-a blocat
- un stream mai mic separat pentru live
- history.html:312 Uncaught DOMException: Failed to set the 'playbackRate' property on 'HTMLMediaElement': The provided playback rate (26.889) is not in the supported playback range.
    at HTMLVideoElement.UserInputVideo.video.doUpdate (http://192.168.111.12/static/history.html:312:31)
    at updateAll (http://192.168.111.12/static/history.html:833:41)
    at Timer.updateSecond [as oncomplete] (http://192.168.111.12/static/history.html:668:5)
    at Timer.step (http://192.168.111.12/static/history.html:473:22)
- schimbat culoarea la iteme in ceva mai contrastant (poate rosu)
- filtrare dupa anumite eventuri
- culori :
    - video #85d8a6
    - event #195f2f cu scris alb
    - folosit className pentru schimbat stilul si culorile
- in major label sa puna si urmatoarele doua unituri
- adaugat moment.js si vis.js in static si vazut bundle-ul cu ele doua
- in video-ul de la shinobi a lui spaceinvader unul din mount-uri e rw-slave
- configul trebuie montat RO

- cand porneste face sync disk->db
- in rulare foloseste doar db ca sa ia decizii
- poate baza de date pusa separat
- folosit timezone; data de la numele fisierului e in utc, dar in pagina se arata in Bucharest/EastEurope
- vazut ca video-urile sunt continue perfect (merge-uit doua video-uri cu bunny)
- folosit logging
- in recorder prins erorile de pe stderr si pasate in logger
- favicon la history.html
- numele de camere nu tre sa inceapa cu _
- pus udp si 900 in default.py
- remove old events
- remove empty directories
- default -> constants
- verificat ca e timp destul pentru ca recorderul sa se opreasca
- elementele stackabile cu un buton de enable/disable
- add example streaming.yml file
- make live video resize with the page
- vis.js performance
- de vazut ffpmeg multithreading daca poate sa accelereze crearea de segmente ca sa nu mai ramana spatiul de aproape o secunda intre segmente
- se poate muta axa in partea de sus si la fel si itemele: orientation: 'top'
- should record fragmented mp4 to avoid file corruption if the recording machine is suddenly powered off:
    - movflags=frag_keyframe+default_base_moof+empty_moov+separate_moof
    - fragmented mp4 video file in "video" tag is slow to start in Chrome. Firefox works better. Probably because Chome wants to read all the moof atoms before starting playing.
    Link to test: https://happy-testing.s3-eu-west-1.amazonaws.com/stack-overflow/help.mp4
    - for the above reason, we should try to make this project work in Firefox
    - https://stackoverflow.com/questions/61803136/ffmpeg-fragmented-mp4-takes-long-time-to-start-playing-on-chrome
    - http://atomicparsley.sourceforge.net/
    - https://trac.ffmpeg.org/ticket/5702
    - qtfaststart -l <video_file>
- https://github.com/aiortc/aiortc/pull/434
