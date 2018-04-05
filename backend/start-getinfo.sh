echo "Connecting to Bitcoin Cash mainnet ..."
$HOME/bitcoinCashUnlimited/bin/bitcoin-cli -datadir=$HOME/.bitcoinCash getinfo
echo ""

echo "Connecting to Bitcoin mainnet ..."
$HOME/bitcoinUnlimited/bin/bitcoin-cli -datadir=$HOME/.bitcoin getinfo
echo ""

echo "Connecting to Bitcoin testnet ..."
$HOME/bitcoinUnlimited/bin/bitcoin-cli -datadir=$HOME/.bitcoinTestnet getinfo
echo ""

echo "Getting process for web server apiRouter.py ..."
pgrep -af apiRouter.py
echo ""

echo "Recent output of apiRouter.py log ..."
tail start-apiRouter.log -n10
echo ""

echo "Getting process for blockchainScanner.py ..."
pgrep -af blockchainScanner.py
echo ""

echo "Recent output of blockchainScanner.py log ..."
tail start-scan.log -n10
echo ""
