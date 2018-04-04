echo "Connecting to Bitcoin Cash mainnet ..."
$HOME/bitcoinCashUnlimited/bin/bitcoin-cli -datadir=$HOME/.bitcoinCash getinfo
echo ""

echo "Connecting to Bitcoin mainnet ..."
$HOME/bitcoinUnlimited/bin/bitcoin-cli -datadir=$HOME/.bitcoin getinfo
echo ""

echo "Connecting to Bitcoin testnet ..."
$HOME/bitcoinUnlimited/bin/bitcoin-cli -datadir=$HOME/.bitcoinTestnet getinfo
echo ""

echo "Getting process for blockchainScanner.py ..."
ps -ef | grep blockchainScanner.py
echo ""

echo "Getting process for web server apiRouter.py ..."
ps -ef | grep apiRouter.py


