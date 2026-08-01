# hermes-ollama-cloud

Ollama Cloud web search and fetch plugin for [Hermes Agent](https://github.com/NousResearch/hermes-agent).

Uses Ollama Cloud's built-in [web search and fetch API](https://docs.ollama.com/capabilities/web-search) as a `web_search` / `web_extract` backend. If you already have an Ollama Cloud subscription (e.g. for inference), web search is included at no extra cost — no Tavily, Exa, or Firecrawl key needed.

## Install

### Option A — pip (recommended)

```bash
pip install hermes-ollama-cloud
```

The package registers itself via the `hermes_agent.plugins` entry point. Hermes discovers it automatically on next startup.

### Option B — manual drop-in

```bash
git clone https://github.com/jcmcneal/hermes-ollama-cloud.git ~/.hermes/plugins/web/ollama
```

Then enable it:

```bash
hermes plugins enable web-ollama
```

## Configure

Set your Ollama API key:

```bash
# ~/.hermes/.env
OLLAMA_API_KEY=your-api-key-here
```

Get your key at [ollama.com](https://ollama.com/settings/keys) (sign in → create API key).

Select Ollama as your web backend:

```yaml
# ~/.hermes/config.yaml
web:
  backend: ollama
```

Or per-capability:

```yaml
web:
  search_backend: ollama
  extract_backend: ollama
```

You can also select it interactively via `hermes tools`.

## API endpoints

| Capability | Endpoint |
|------------|----------|
| Search | `POST https://ollama.com/api/web_search` |
| Fetch | `POST https://ollama.com/api/web_fetch` |

Auth: Bearer token via `OLLAMA_API_KEY`.

## Compatibility

- Hermes Agent v0.13+ (requires the `WebSearchProvider` plugin registry)
- Python 3.10+

## License

MIT
