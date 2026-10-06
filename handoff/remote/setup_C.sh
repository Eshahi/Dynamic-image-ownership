set -e
cd /workspace; . venv/bin/activate; A=/workspace/assets/a6
echo "$(date -u +%H:%M:%S) repo"
rm -rf /workspace/m1b && git clone -q -b claude/m1b-package /root/m1b-package.bundle /workspace/m1b
cd /workspace/m1b
for t in parent rehearsal runtime; do tar -xf /root/$t.tar; done
cp -a "/workspace/m1b-data/W:/." "W:/"
mkdir -p "W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/assets"
ln -sfn "$A" "W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/assets/a6"
printf '/W:\n/C:\n' >> .git/info/exclude
git -c safe.directory='*' log --oneline -1
echo "dirty entries: $(git status --porcelain | wc -l)"
echo "$(date -u +%H:%M:%S) tests"
python -m unittest tests.test_m1b_coco512_worker 2>&1 | tail -3
echo SETUP_DONE
