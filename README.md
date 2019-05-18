# P2P FACOM

Uma simples implementação para emular um sistema P2P para transmissão de dados multimídia, usando o protocolo UDP para estabelecer comunicação de um processo a outro. 
O sistema possui dois tipos de peers: emissor(seeder) e receptor(leecher) 

  - Rede P2P de Leecher e Seeder
  - Compartilhamento de música MP3
  - Player de áudio

## Características

  - Seeder e Leecher suportam UDP
  - Pesquisa de arquivos de áudio
  - Seeder envia arquivos utilizando métodos sequencial, aleatório e semi-aleatório
  - Seeder suporte envio parcial de arquivo
  - Seeder suporta envio resposta PING/PONG
  - Leecher possui solicitação de retransmissão de pacotes faltantes
  - Leecher mostra estatisticas após download
  - Leecher mostra gráfico de pacotes enviados, recebidos e tocados
  - Leecher reproduz áudio após completar download
  - Leecher pré-visualiza áudio enquanto faz download
  - Leecher verifica seeder ativos ao iniciar
  
  
### Instalação

P2P Facom requer [ffmpeg](https://ffmpeg.org/download.html) para reproduzir áudio.

Instale as dependências para utilizar o software.

```sh
$ sudo apt-get install ffmpeg
$ sudo apt-get install python3-pip
$ sudo apt-get install python3-pyaudio
$ sudo apt-get install python3-pyqt5 
$ sudo apt-get install python3-tk
$ sudo apt-get install git
$ mkdir P2P
$ cd P2P
$ sudo git clone https://github.com/ferlete/P2P.git
$ sudo pip3 install -r requeriments.txt

```

### Modo de uso
para verificar modo de uso
```sh
$ cd P2P 
$ python3 p2p-runner.py -h
```

### Seeder

Para executar o Seeder com método sequencial
```sh
$ python3 p2p-runner.py -t seeder -i 127.0.0.1 -p 9000 -m sequential
```

Para executar o Seeder com método aleatório
```sh
$ python3 p2p-runner.py -t seeder -i 127.0.0.2 -p 9000 -m random
```

Para executar o Seeder com método semi-aleatório
```sh
$ python3 p2p-runner.py -t seeder -i 127.0.0.3 -p 9000 -m semi-random
```

### Leecher

Para executar a interface gráfica do Leecher
```sh
$ python3 p2p-runner.py -t leecher 
```

### Problemas conhecidos
Erro: Qt: Session management error: Could not open network socket

Solução: $ unset SESSION_MANAGER