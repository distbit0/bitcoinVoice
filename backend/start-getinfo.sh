echo "Bitcoin Cash mainnet ####"
$HOME/bitcoinCashUnlimited/bin/bitcoin-cli -datadir=$HOME/.bitcoinCash getinfo

echo ""
echo "Bitcoin mainnet #########"
$HOME/bitcoinUnlimited/bin/bitcoin-cli -datadir=$HOME/.bitcoin getinfo

echo ""
echo "Bitcoin testnet #########"
$HOME/bitcoinUnlimited/bin/bitcoin-cli -datadir=$HOME/.bitcoinTestnet getinfo

echo ""

