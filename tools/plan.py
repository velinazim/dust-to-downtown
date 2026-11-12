"""Split an episode into render chunks.  python3 tools/plan.py <slug> [fps] [max_chunks]"""
import json, math, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
slug = sys.argv[1]
fps = int(sys.argv[2]) if len(sys.argv) > 2 else 30
maxc = int(sys.argv[3]) if len(sys.argv) > 3 else 20
c = json.load(open(os.path.join(ROOT, 'cities', slug, 'city.json')))
co = c.get('cold_open')   # cold open = extra seconds before the timeline
frames = int(round((sum(s['seconds'] for s in c['segments']) + (float(co.get('seconds', 7)) if co else 0.0)) * fps))
n = max(1, min(maxc, math.ceil(frames / 300)))
size = math.ceil(frames / n)
chunks = [{'start': i, 'end': min(frames, i + size)} for i in range(0, frames, size)]
print(json.dumps({'slug': slug, 'fps': fps, 'frames': frames, 'chunks': chunks}))
