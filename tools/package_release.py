"""Create self-contained press kit and deployable static website ZIP files."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
ROOT=Path(__file__).resolve().parents[1]
with ZipFile(ROOT/'downloads/TodoApp-press-kit.zip','w',ZIP_DEFLATED) as z:
    for p in sorted((ROOT/'press').glob('*.png')):
        z.write(p,'TodoApp-press-kit/'+p.name)
    z.write(ROOT/'press/短视频分镜与配文.md','TodoApp-press-kit/短视频分镜与配文.md')
    z.write(ROOT/'assets/share-cover.jpg','TodoApp-press-kit/share-cover.jpg')
with ZipFile(ROOT/'downloads/TodoApp-website.zip','w',ZIP_DEFLATED) as z:
    for filename in ['index.html','styles.css']:
        z.write(ROOT/filename,filename)
    for folder in ['assets','press']:
        for p in sorted((ROOT/folder).rglob('*')):
            if p.is_file() and p.name not in ['.DS_Store','TodoApp-website.zip']:
                z.write(p,p.relative_to(ROOT))
    # Only publish release files; users may extract ZIPs inside downloads locally.
    for name in ['Shijian_0.1.0_x64.dmg', 'TodoApp_0.1.0_x64.dmg', 'SHA256SUMS.txt', 'release.json', 'TodoApp-press-kit.zip']:
        p = ROOT / 'downloads' / name
        z.write(p, p.relative_to(ROOT))
print('Created TodoApp-press-kit.zip and TodoApp-website.zip')
