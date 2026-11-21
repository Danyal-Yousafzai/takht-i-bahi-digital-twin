"""
generate_audio.py — pre-render hotspot narration for the Takht-i-Bahi Digital Twin.

Most phones and Windows PCs have no Urdu or Pashto text-to-speech voice, so the
browser's Web Speech API stays silent for UR / PS.  This script renders every
hotspot card (title + body, exactly as shown in the app) to MP3 with Microsoft's
neural voices via edge-tts, falling back to gTTS if edge-tts is unavailable.

The text is read straight from the HOTSPOTS object in app.js (via Node.js), so
the audio always matches what is on screen.

    pip install edge-tts gTTS
    python generate_audio.py              # male narrators (default)
    python generate_audio.py --female     # female narrators
    python generate_audio.py --force      # re-render existing files

Output: assets/audio/{stupa,relic,niche}_{en,ur,ps}.mp3 + narration.json
"""

import argparse
import asyncio
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
APP_JS = os.path.join(HERE, "app.js")
OUT = os.path.join(HERE, "assets", "audio")

VOICES = {
    "male":   {"en": "en-GB-RyanNeural",  "ur": "ur-PK-AsadNeural", "ps": "ps-AF-GulNawazNeural"},
    "female": {"en": "en-GB-SoniaNeural", "ur": "ur-PK-UzmaNeural", "ps": "ps-AF-LatifaNeural"},
}
RATE = {"en": "-4%", "ur": "-8%", "ps": "-8%"}     # a calm guide's pace
GTTS_LANG = {"en": "en", "ur": "ur", "ps": "ur"}   # gTTS has no Pashto: Urdu reads the script


def load_hotspots():
    """Extract the HOTSPOTS object literal from app.js and evaluate it with Node."""
    src = open(APP_JS, encoding="utf-8").read()
    m = re.search(r"const HOTSPOTS = (\{.*?\n\});", src, re.S)
    if not m:
        sys.exit("Could not find `const HOTSPOTS = {...};` in app.js")
    js = f"const H = {m.group(1)}; process.stdout.write(JSON.stringify(H));"
    try:
        res = subprocess.run(["node", "-e", js], capture_output=True, check=True)
    except FileNotFoundError:
        sys.exit("Node.js is needed to read HOTSPOTS from app.js (https://nodejs.org)")
    except subprocess.CalledProcessError as e:
        sys.exit(e.stderr.decode("utf-8", "replace"))
    return json.loads(res.stdout.decode("utf-8"))


async def render_edge(text, voice, rate, path, attempts=4):
    """The edge-tts service sometimes returns no audio when called rapidly: retry with back-off."""
    import edge_tts
    for i in range(attempts):
        try:
            await edge_tts.Communicate(text, voice, rate=rate).save(path)
            if os.path.getsize(path) > 1024:
                return
        except Exception:
            if i == attempts - 1:
                raise
        await asyncio.sleep(2.0 * (i + 1))
    raise RuntimeError("no audio received")


def render_gtts(text, lang, path):
    from gtts import gTTS
    gTTS(text=text, lang=lang, slow=False).save(path)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--female", action="store_true", help="use female narrators")
    ap.add_argument("--force", action="store_true", help="overwrite existing MP3s")
    ap.add_argument("--engine", choices=["edge", "gtts"], default="edge")
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)

    hotspots = load_hotspots()
    voices = VOICES["female" if args.female else "male"]
    manifest = {}
    for key, spot in hotspots.items():
        for lang in ("en", "ur", "ps"):
            d = spot[lang]
            text = f"{d['title']}. {d['body']}"          # same string the app speaks
            name = f"{key}_{lang}.mp3"
            path = os.path.join(OUT, name)
            engine = args.engine
            if args.force or not os.path.exists(path):
                try:
                    if engine == "edge":
                        asyncio.run(render_edge(text, voices[lang], RATE[lang], path))
                    else:
                        render_gtts(text, GTTS_LANG[lang], path)
                except Exception as e:                    # network hiccup / missing package
                    print(f"  edge-tts failed for {name} ({e}); trying gTTS")
                    engine = "gtts"
                    render_gtts(text, GTTS_LANG[lang], path)
                print(f"  wrote {name:16s} {os.path.getsize(path) / 1024:6.0f} KB  "
                      f"[{voices[lang] if engine == 'edge' else 'gTTS ' + GTTS_LANG[lang]}]")
            else:
                print(f"  kept  {name}")
            manifest[f"{key}_{lang}"] = {"file": name, "voice": voices[lang] if engine == "edge" else "gTTS",
                                         "text": text}
    with open(os.path.join(OUT, "narration.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)
    print(f"Done: {len(manifest)} narrations in {OUT}")


if __name__ == "__main__":
    main()
