# dreamapp
Jungian dream interpretation: extract symbols, retrieve corpus, synthesize, write to `wiki/dreams/`.

## Install

```
pip install -e dream-app
bash bin/setup-retrieve.sh                 # once, from vault root
cp dream-app/.env.example dream-app/.env   # fill in ANTHROPIC_API_KEY
```

## Usage

```
dreamapp interpret path/to/dream.txt
dreamapp interpret - < dream.txt           # stdin
dreamapp interpret wiki/dreams/....md --force
```

Flags: `--dry`, `--show-sources`, `--force`, `--title`, `--date YYYY-MM-DD`.
