# must be run from backend
echo "start-scan.sh : Starting blockchain scanner..."
cd /home/bitcoinvoice/projects/bitcoinVoice/backend
python3 blockchainScanner.py $1 >> /home/bitcoinvoice/projects/bitcoinVoice/backend/start-scan.log
