import pathlib, re, json, sys
sys.stdout.reconfigure(encoding="utf-8")
cache=pathlib.Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T3b")
for name in sys.argv[1:]:
    path=cache/name
    html=path.read_text(encoding="utf-8")
    found=re.search(r'"rawLines":(\[.*?\]),"stylingDirectives"',html)
    if found:
        text="\n".join(json.loads(found[1]))
        dest=path.with_suffix(".source.txt")
        dest.write_text(text,encoding="utf-8")
        print(dest)
    else:
        print("No rawLines:",name)
