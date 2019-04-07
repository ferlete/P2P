# P2P FACOM

P2P Simulation

  - Client and Server TCP and UDP P2P networdk
  - Music share
  - Playback on download

# New Features!

  - UDP Server Suporte
  - TCP Server Suporte

### Installation

P2P requires [ffmpeg](https://ffmpeg.org/download.html) to run.

Install the dependencies and devDependencies and start the server.

```sh
$ apt-get install ffmpeg
$ cd P2P
$ git clone https://github.com/ferlete/P2P/P2P.git
```

### Run

For run TCP server
```sh
$ cd P2P 
$ python3 p2p-runner.py -t server -p 8000 --tcp 
```

For run UDP server
```sh
$ cd P2P 
$ python3 p2p-runner.py -t server -p 8000 --udp 
```

For run TCP Client
```sh
$ cd P2P 
$ python3 p2p-runner.py -t client -p 8000 
```