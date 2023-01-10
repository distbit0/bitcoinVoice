BITCOINVOICE="/home/bitcoinvoice/projects/bitcoinVoice"
export BITCOINVOICE
cd $BITCOINVOICE/backend

#./start-apiRouter.sh & # this starts in the root user crontab

./start-bitcoind.sh &

./start-getinfo.sh &

./start-scan.sh &
