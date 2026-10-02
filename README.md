# graze-prize-mcp 🐐

MCP server sharing a **masked** prize-list dataset with AI clients. Masked means: PAN last-4 only, no CVV, no full PAN — the bundled `data/sample.json` holds a single obviously-fake record.

## Quickstart

```bash
pip install -r requirements.txt
python mcp_server.py          # MCP over stdio
```

Point at your own **masked** export (never a file with full PANs/CVVs):

```bash
GRAZE_PRIZE_DATA=/path/to/masked.json python mcp_server.py
```

## Tools

| Tool | What it does |
| --- | --- |
| `prize_stats` | record count, distinct Rx count, top Rx |
| `search_records` | search by name, Rx, email, PAN last-4 |
| `get_record` | one masked record by 1-based id |
| `list_rx_values` | distinct Rx values |
| `prize://masked-schema` | field layout resource |

## Connect an AI client

Claude Desktop (`claude_desktop_config.json`) or any client with an `mcpServers` block:

```json
{ "mcpServers": { "graze-prize": {
  "command": "python",
  "args": ["/path/to/graze-prize-mcp/mcp_server.py"]
} } }
```

## Privacy

This repo ships **no real data** — only `data/sample.json` (one synthetic record: Testy McTestface). Real/full datasets are excluded via `.gitignore`.
