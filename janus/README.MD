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
