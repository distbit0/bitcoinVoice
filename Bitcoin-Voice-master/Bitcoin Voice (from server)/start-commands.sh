#./start-apiRouter.sh & # this starts in the root user crontab

./start-bitcoind.sh &

./start-getinfo.sh &

./start-scan.sh &
