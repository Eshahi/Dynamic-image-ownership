set -u
R=/workspace/m1b-data; mkdir -p "$R"; cd "$R"
echo "$(date -u +%H:%M:%S) coco annotations"
curl -sSL --retry 3 -o ann.zip http://images.cocodataset.org/annotations/annotations_trainval2017.zip && unzip -q -o ann.zip annotations/instances_val2017.json && echo "ann ok"
bad=0; n=0
while read -r sha path; do
  rel="${path#W:/}"; dest="$R/W:/$rel"; mkdir -p "$(dirname "$dest")"
  case "$path" in
    *instances_val2017.json) cp annotations/instances_val2017.json "$dest";;
    *.jpg) curl -sSL --retry 3 -o "$dest" "http://images.cocodataset.org/val2017/$(basename "$path")";;
  esac
  if [ "$(sha256sum "$dest" | cut -d' ' -f1)" = "$sha" ]; then n=$((n+1)); else echo "MISMATCH $path"; bad=$((bad+1)); fi
done < /root/heldout-expected.txt
echo "verified $n, mismatched $bad"
echo SETUP_B_DONE
