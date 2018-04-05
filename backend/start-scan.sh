# must be run from backend
echo "start-scan.sh : Starting blockchain scanner..."
cd /home/bitcoinvoice/projects/bitcoinVoice/backend
python3 -u blockchainScanner.py $1 > start-scan.log
