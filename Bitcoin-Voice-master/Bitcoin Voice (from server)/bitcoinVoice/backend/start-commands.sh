#./start-apiRouter.sh & # this starts in the root user crontab
cd /home/bitcoinvoice/projects/bitcoinVoice/backend/
./start-bitcoind.sh &

./start-getinfo.sh &

./start-scan.sh &
