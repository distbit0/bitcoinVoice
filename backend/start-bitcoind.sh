# the ~ must be replaced with the complete path to the blockchain folders
echo "start-bitcoind.sh : Starting blockchain nodes..."
$HOME/bitcoinCashUnlimited/bin/bitcoind -datadir=$HOME/.bitcoinCash &
$HOME/bitcoinUnlimited/bin/bitcoind -datadir=$HOME/.bitcoinTestnet &
$HOME/bitcoinUnlimited/bin/bitcoind -datadir=$HOME/.bitcoin &
