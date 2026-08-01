# hermes-ollama-cloud

Ollama Cloud web search and fetch plugin for [Hermes Agent](https://github.com/NousResearch/hermes-agent).

Uses [Ollama Cloud](https://ollama.com)'s built-in [web search and fetch API](https://docs.ollama.com/capabilities/web-search) as a `web_search` / `web_extract` backend. If you already have an Ollama Cloud subscription (e.g. for inference), web search is included at no extra cost — no Tavily, Exa, or Firecrawl key needed.

> **Ollama vs. Ollama Cloud** — This plugin uses **Ollama Cloud**, Ollama's hosted API service at `ollama.com`. It is separate from local Ollama (the `ollama serve` daemon running on your machine). You need an Ollama Cloud account and API key even if you already run local Ollama for inference.
>
> In Hermes, the inference provider is called `ollama-cloud` and this plugin registers a web backend with the same name. Both use the same `OLLAMA_API_KEY`, but they are configured independently — one for chat completions, one for web search/extract.

## Install

### Option A — pip (recommended)

```bash
pip install hermes-ollama-cloud
```

The package registers itself via the `hermes_agent.plugins` entry point. Hermes discovers it automatically on next startup — no manual enable step needed.

### Option B — manual drop-in

```bash
git clone https://github.com/jcmcneal/hermes-ollama-cloud.git ~/.hermes/plugins/ollama-cloud
```

Then enable it:

```bash
hermes plugins enable ollama-cloud
```

> The plugin directory name must be `ollama-cloud` (flat, matching the plugin name in `plugin.yaml`). Hermes does not support nested subdirectories like `~/.hermes/plugins/web/ollama`.

## Configure

### 1. Set your Ollama Cloud API key

```bash
# ~/.hermes/.env
OLLAMA_API_KEY=your-api-key-here
```

Get your key at [ollama.com](https://ollama.com/settings/keys) (sign in → create API key).

You can also set it interactively:

```bash
hermes tools
```

Select **Ollama Cloud** as your web search and/or web extract provider, and Hermes will prompt for the key.

### 2. Select `ollama-cloud` as your web backend

```yaml
# ~/.hermes/config.yaml
web:
  backend: ollama-cloud
```

Or per-capability:

```yaml
web:
  search_backend: ollama-cloud
  extract_backend: ollama-cloud
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