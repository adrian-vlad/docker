###Config
There is only one file that is used as input for the application and it's called `streaming.yml`. This a yaml file that has the following structure:
```
limit_disk_space: maximum amount of bytes that the recordings will occupy
camera:
  <name1>:
    src: "rtsp url to the live stream of the camera"
    rtsp_transport: "tcp" | "udp". Default: "udp". Some rtsp streams don't work on udp. Setting this option to "tcp" might help
  <name2>: ..
  <name3>: ..
  ..
```
###Run
```
docker run --init --rm -v <path_to_directory_containing_streaming.yml_file>:/opt/streaming -v <path_to_directory_that_will_store_the_recordings>:/opt/static/recordings --net my_net janus
```

###Endpoints
- `/live/<id>` - shows live view of the respective camera. `id` is an int that corresponds to the index of the respective camera in the `streaming.yml`'s camera array.
- `/static/history.html` - the page where past recordings can be viewed.


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
