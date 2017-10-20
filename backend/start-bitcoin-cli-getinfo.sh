echo "Bitcoin Cash mainnet"
$HOME/bitcoinCashUnlimited/bin/bitcoin-cli -datadir=$HOME/.bitcoinCash getinfo

echo "Bitcoin mainnet"
bitcoin-cli -datadir=$HOME/.bitcoin getinfo

echo "Bitcoin testnet"
bitcoin-cli -datadir=$HOME/.bitcoinTestnet getinfo



