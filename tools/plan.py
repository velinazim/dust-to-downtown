"""Split an episode into render chunks.  python3 tools/plan.py <slug> [fps] [max_chunks]"""
import json, math, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
slug = sys.argv[1]
fps = int(sys.argv[2]) if len(sys.argv) > 2 else 30
maxc = int(sys.argv[3]) if len(sys.argv) > 3 else 20
c = json.load(open(os.path.join(ROOT, 'cities', slug, 'city.json')))
frames = int(round(sum(s['seconds'] for s in c['segments']) * fps))
n = max(1, min(maxc, math.ceil(frames / 300)))
size = math.ceil(frames / n)
chunks = [{'start': i, 'end': min(frames, i + size)} for i in range(0, frames, size)]
print(json.dumps({'slug': slug, 'fps': fps, 'frames': frames, 'chunks': chunks}))
