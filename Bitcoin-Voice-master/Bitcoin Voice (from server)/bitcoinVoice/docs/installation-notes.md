# Bitcoin Voice

# code dependencies to be installed 
sudo pip3 install psycopg2
sudo pip3 install python-bitcoinrpc

# postgres setup
sudo apt install postgres-9.4 pgadmin3

# python3

# Download and sync the blockchain nodes you want to scan for public labels
https://www.bitcoinunlimited.info/download

## CONFIGURATION OF bitcoin.conf files required 
##
## bitcoin.conf configuration file. Lines beginning with # are comments.
##

# BITCOIN VOICE OPTIONS - BITCOIN CASH
# multiple clients running need a different port for each number
port=8338 
# include all transactions in the rpc database needs -reindex
txindex=1
# Listen for RPC connections on this TCP port:
rpcport=8331
# You can use Bitcoin or bitcoind to send commands to Bitcoin/bitcoind
# running on another host using this option:
#rpcconnect=127.0.0.1
server=1
rpcauth=bitcoinvoice:46e4a4517db427c09cc6e720733a6e20$aa515cd7759d0599ac1bac2edb86cabfacd5d9401796435bf81c2aad72420ff1

# Server auto startup 
# need sleep 60 to give some time for postgres server to start
# sudo crontab -e 
@reboot sleep 60 && <installpath>/bitcoinVoice/backend/start-apiRouter.sh

# crontab -e
@reboot  sleep 60 && <installpath>/bitcoinVoice/backend/startAll.sh > <installpath>/bitcoinVoice/backend/startAll.log

# Monitor system status
cd backup
./start-getinfo.sh

# section 1 is the blockchain nodes status info
# section 2 is the process ID and recent log of the web server python3 apiRouter.py
# section 3 is the process ID and recent log of the public label scanner process python3 blockchainScanner.py
# for example
Connecting to Bitcoin testnet ...
{
  "version": 1000300,
  "protocolversion": 80002,
  "walletversion": 60000,
  "balance": 0.00000000,
  "blocks": 1291392,
  "timeoffset": 0,
  "connections": 12,
  "proxy": "",
  "difficulty": 1,
  "testnet": true,
  "keypoololdest": 1513632602,
  "keypoolsize": 101,
  "paytxfee": 0.00000000,
  "relayfee": 0.00000000,
  "errors": "Warning: unknown new rules activated (versionbit 28)"
}

Getting process for web server apiRouter.py ...
1909 python3 -u ./apiRouter.py /home/bitcoinvoice/projects/bitcoinVoice

Recent output of apiRouter.py log ...
Connected to bitcoinVoice DB...

Getting process for blockchainScanner.py ...
1915 python3 -u blockchainScanner.py

Recent output of blockchainScanner.py log ...

### Adding unspent public labels ...
Verifying range from block 516669 to 516679
Deleting data processed after block height 516669
Scanning from block 516669 to 516679
Scanning block data for public label outputs...

### Updating spent public labels ...
Completed scan of blockchain bitcoin on port 8330

