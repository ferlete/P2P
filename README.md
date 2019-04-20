# P2P FACOM

P2P Simulation

  - Client and Server UDP P2P network
  - Music share
  - Playback on download

# New Features!

  - UDP server suport
  - Sequential method
  - Random method
  - Show statistics
  - Plot graphic
  
### Installation

P2P requires [ffmpeg](https://ffmpeg.org/download.html) to run.

Install the dependencies and devDependencies and start the server.

```sh
$ apt-get install ffmpeg
$ pip3 install pydub
$ mkdir P2P
$ cd P2P
$ git clone https://github.com/ferlete/P2P/P2P.git
```

### Run

For run UDP server method sequential
```sh
$ cd P2P 
$ python3 p2p-runner.py -t server -p 8000
```

For run UDP server method random
```sh
$ cd P2P 
$ python3 p2p-runner.py -t server -p 8000 -m random
```

For run UDP Client
```sh
$ cd P2P 
$ python3 p2p-runner.py -t client 
```