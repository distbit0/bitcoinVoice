# Bitcoin Voice

# code dependencies to be intalled 
sudo pip3 install psycopg2
sudo pip3 install python-bitcoinrpc


# postgres setup
sudo apt install postgres-9.4 pgadmin3


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



