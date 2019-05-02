# P2P FACOM

P2P Simulation

  - Client and Server UDP P2P network
  - Music share
  - Playback on download

# New Features!

  - UDP client / server
  - Search file on seeder
  - Seeder sends file using sequential method
  - Seeder sends file using sequential random method
  - Seeder sends file using sequential method semi-Random method
  - Leecher show statistics after download
  - Leecher Plot graphic after download
  - Leecher check for seeder alive
  - Parallel download suport
  
### Installation

P2P requires [ffmpeg](https://ffmpeg.org/download.html) to run.

Install the dependencies and devDependencies and start the server.

```sh
$ apt-get install ffmpeg
$ apt-get install python3-tk
$ apt-get install python3-pip
$ apt-get install python3-pyaudio 
$ pip3 install -r requirements.txt
$ git clone https://github.com/ferlete/P2P
```

### Usage
to see how to use
```sh
$ cd P2P 
$ python3 p2p-runner.py -h
```

### Server

For run UDP server with method sequential
```sh
$ cd P2P 
$ python3 p2p-runner.py -t server -i 127.0.0.1 -p 9000
```

For run UDP server with method random
```sh
$ cd P2P 
$ python3 p2p-runner.py -t server -i 127.0.0.1 -p 9000 -m random
```

For run UDP server with method semi-random
```sh
$ cd P2P 
$ python3 p2p-runner.py -t server -i 127.0.0.1 -p 9000 -m semi-random
```

### Client

For run UDP Client
```sh
$ cd P2P 
$ python3 p2p-runner.py -t client 
```

For run UDP Client with statistic
```sh
$ cd P2P 
$ python3 p2p-runner.py -t client --statistic
```

For run UDP Client with graphic statistic
```sh
$ cd P2P 
$ python3 p2p-runner.py -t client --graphic
```

For run UDP Client with parallel download
```sh
$ cd P2P 
$ python3 p2p-runner.py -t server -i 127.0.0.1 -p 9000 (run new windows)
$ python3 p2p-runner.py -t server -i 127.0.0.2 -p 9000 (run new windows)
$ python3 p2p-runner.py -t client --parallel
```