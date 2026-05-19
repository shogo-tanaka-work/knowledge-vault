# Vercel Docs URL Inventory

> 取得日：2026-05-08
> ソース：https://vercel.com/sitemap.xml （フラットなサイトマップで、サブ sitemap への分割は無し / 約 1,000+ URL を含む）
> 取得方法：WebFetch で sitemap.xml を 2 パスで抽出し、`/docs` ランディング（https://vercel.com/docs）でトップレベル構造を補完。
> robots.txt：ai-train=no / ai-input=yes / search=yes（教材化用途は出典明示で OK）
> 補足：v0 は独立サブドメイン（`https://v0.app/docs/...`）、AI Gateway は Vercel 配下の `/docs/ai-gateway/*` と独立 LP（`/ai-gateway`、`/ai-gateway/leaderboards`、`/ai-gateway/models`）を併用。Sandbox は `/docs/vercel-sandbox/*` と REST API ベータが存在。

---

## 00-index

| URL | ページタイトル | 想定章番号 |
|---|---|---|
| https://vercel.com/docs | Vercel Documentation（トップ） | 00 |
| https://vercel.com/docs/sitemap | Docs サイトマップ | 00 |
| https://vercel.com/kb | Vercel Knowledge Base | 00 |

## 10-overview-landscape

| URL | ページタイトル | 想定章番号 |
|---|---|---|
| https://vercel.com/ | Vercel トップ（The AI Cloud） | 10 |
| https://vercel.com/docs | Vercel Documentation 概要 | 10 |
| https://vercel.com/ai | AI Cloud（プロダクトページ） | 10 |
| https://vercel.com/docs/getting-started-with-vercel | Getting Started | 10 |
| https://vercel.com/docs/incremental-migration | Incremental Migration Guide | 10 |
| https://vercel.com/docs/production-checklist | Production Checklist | 10 |
| https://vercel.com/about | About Vercel | 10 |

## 20-frameworks-and-builds

| URL | ページタイトル | 想定章番号 |
|---|---|---|
| https://vercel.com/docs/frameworks | Frameworks 概要 | 20 |
| https://vercel.com/docs/frameworks/nextjs | Next.js on Vercel | 20 |
| https://vercel.com/docs/frameworks/more-frameworks | More Frameworks | 20 |
| https://vercel.com/docs/builds/build-features | Build Features | 20 |
| https://vercel.com/docs/builds/build-queues | Build Queues | 20 |
| https://vercel.com/docs/builds/configure-a-build | Configure a Build | 20 |
| https://vercel.com/docs/build-output-api | Build Output API | 20 |
| https://vercel.com/docs/git | Git Integration | 20 |
| https://vercel.com/docs/project-configuration | Project Configuration | 20 |
| https://vercel.com/docs/private-registry | Private Registry | 20 |
| https://vercel.com/academy/production-monorepos | Production Monorepos（Academy） | 20 |
| https://vercel.com/academy/production-monorepos/turborepo-basics | Turborepo Basics | 20 |
| https://vercel.com/academy/production-monorepos/remote-caching | Turborepo Remote Caching | 20 |
| https://vercel.com/changelog/import-turborepo-nx-and-rush-monorepos-with-zero-configuration | Monorepo zero-config import | 20, 50 |

## 21-functions-and-fluid-compute

| URL | ページタイトル | 想定章番号 |
|---|---|---|
| https://vercel.com/docs/functions | Vercel Functions | 21 |
| https://vercel.com/docs/functions/runtimes | Function Runtimes | 21 |
| https://vercel.com/docs/functions/usage-and-pricing | Functions: Active CPU / Provisioned Memory | 21 |
| https://vercel.com/docs/fluid-compute | Fluid Compute | 21 |
| https://vercel.com/changelog/vercel-functions-can-now-run-on-fluid-compute | Functions on Fluid Compute（リリース） | 21, 50 |
| https://vercel.com/changelog/higher-defaults-and-limits-for-vercel-functions-running-fluid-compute | Higher defaults/limits for Fluid Compute | 21, 50 |
| https://vercel.com/changelog/vercel-functions-now-have-faster-and-fewer-cold-starts | Cold start 改善 | 21, 50 |
| https://vercel.com/changelog/streaming-now-enabled-by-default-for-all-node-js-vercel-functions | Streaming default ON | 21, 50 |
| https://vercel.com/changelog/zero-config-fastapi-backends | FastAPI zero-config | 21, 50 |

## 22-routing-middleware-and-edge

| URL | ページタイトル | 想定章番号 |
|---|---|---|
| https://vercel.com/docs/routing-middleware | Routing Middleware | 22 |
| https://vercel.com/changelog/vercel-edge-middleware-is-now-generally-available | Edge Middleware GA | 22, 50 |
| https://vercel.com/changelog/vercel-edge-functions-are-now-in-public-beta | Edge Functions Public Beta | 22, 50 |
| https://vercel.com/changelog/improved-node-js-compatibility-for-edge-middleware-and-edge-functions | Edge: Node.js 互換 | 22, 50 |
| https://vercel.com/changelog/more-flexible-environment-variables-in-edge-functions-and-middleware | Edge: 環境変数 | 22, 50 |

## 23-isr-and-image-optimization

| URL | ページタイトル | 想定章番号 |
|---|---|---|
| https://vercel.com/docs/incremental-static-regeneration | ISR | 23 |
| https://vercel.com/docs/image-optimization | Image Optimization | 23 |
| https://vercel.com/docs/caching/cache-control-headers | Cache-Control Headers | 23 |
| https://vercel.com/docs/caching/cdn-cache | CDN Cache | 23 |
| https://vercel.com/changelog/introducing-the-runtime-cache-api | Runtime Cache API | 23, 50 |
| https://vercel.com/changelog/serve-personalized-content-faster-with-vary-support | Vary support | 23, 50 |
| https://vercel.com/changelog/request-collapsing-for-isr-cache-misses | Request collapsing for ISR | 23, 50 |
| https://vercel.com/changelog/stale-if-error-cache-control-header-is-now-supported | stale-if-error 対応 | 23, 50 |

## 24-deployments-and-environments

| URL | ページタイトル | 想定章番号 |
|---|---|---|
| https://vercel.com/docs/deployments/environments | Environments（Preview/Production/Custom） | 24 |
| https://vercel.com/docs/rolling-releases | Rolling Releases | 24 |
| https://vercel.com/docs/instant-rollback | Instant Rollback | 24 |
| https://vercel.com/docs/deployments/claim-deployments | Claim Deployments | 24, 43 |
| https://vercel.com/changelog/revert-and-pin-deployments-with-instant-rollback | Instant Rollback（発表） | 24, 50 |
| https://vercel.com/changelog/every-push-now-receives-a-unique-url | Every push → unique URL | 24, 50 |
| https://vercel.com/changelog/skew-protection-is-now-enabled-by-default-for-new-projects | Skew Protection default | 24, 50 |
| https://vercel.com/changelog/spend-management-now-pauses-production-deployments-by-default | Spend management default | 24, 50 |

## 25-domains-and-delivery-network

| URL | ページタイトル | 想定章番号 |
|---|---|---|
| https://vercel.com/docs/cdn | Vercel Delivery Network / CDN | 25 |
| https://vercel.com/docs/manage-cdn-usage | Manage CDN Usage | 25 |
| https://vercel.com/docs/domains | Domains（推定 canonical） | 25 |
| https://vercel.com/changelog/improved-cdn-performance | CDN performance 改善 | 25, 50 |
| https://vercel.com/changelog/https-dns-records-are-now-supported-in-vercel-dns | HTTPS DNS records 対応 | 25, 50 |
| https://vercel.com/changelog/bulk-redirects-are-now-generally-available | Bulk Redirects GA | 25, 50 |
| https://vercel.com/changelog/improved-domains-page | Improved Domains page | 25, 50 |

## 26-storage-and-marketplace

| URL | ページタイトル | 想定章番号 |
|---|---|---|
| https://vercel.com/docs/integrations | Vercel Marketplace / Integrations | 26 |
| https://vercel.com/docs/vercel-blob/using-blob-sdk | Vercel Blob SDK | 26 |
| https://vercel.com/kb/storage | KB: Storage | 26 |
| https://vercel.com/docs/integrations/create-integration/marketplace-api/reference/partner/delete-resource | Marketplace API: delete-resource | 26 |
| https://vercel.com/docs/integrations/create-integration/marketplace-api/reference/partner/delete-installation | Marketplace API: delete-installation | 26 |
| https://vercel.com/changelog/upstash-joins-the-vercel-marketplace | Upstash Marketplace | 26, 50 |
| https://vercel.com/changelog/convex-joins-the-vercel-marketplace | Convex Marketplace | 26, 50 |
| https://vercel.com/changelog/clerk-joins-the-vercel-marketplace | Clerk Marketplace | 26, 50 |
| https://vercel.com/changelog/groq-fal-and-deepinfra-join-the-vercel-marketplace | Groq/Fal/DeepInfra | 26, 50 |
| https://vercel.com/changelog/railway-integration-postgres-redis-mysql | Railway integration | 26, 50 |
| https://vercel.com/changelog/stripe-is-now-generally-available-on-the-marketplace-and-v0 | Stripe GA on Marketplace/v0 | 26, 50 |
| https://vercel.com/changelog/5tb-file-transfers-with-vercel-blob-multipart-uploads | Blob 5TB multipart | 26, 50 |
| https://vercel.com/changelog/view-upload-and-delete-blob-files-in-the-dashboard | Blob Dashboard UI | 26, 50 |
| https://vercel.com/changelog/protect-your-edge-config-with-a-json-schema | Edge Config JSON schema | 26, 50 |

## 27-observability-and-analytics

| URL | ページタイトル | 想定章番号 |
|---|---|---|
| https://vercel.com/docs/observability | Observability Suite | 27 |
| https://vercel.com/docs/analytics/quickstart | Web Analytics Quickstart | 27 |
| https://vercel.com/docs/analytics/redacting-sensitive-data | Analytics: Redacting Sensitive Data | 27 |
| https://vercel.com/docs/speed-insights | Speed Insights（推定 canonical） | 27 |
| https://vercel.com/docs/logs | Runtime Logs | 27 |
| https://vercel.com/docs/drains | Drains 概要 | 27 |
| https://vercel.com/docs/drains/using-drains | Using Drains | 27 |
| https://vercel.com/changelog/30-day-runtime-log-retention-now-available-in-observability-plus | 30-day log retention | 27, 50 |
| https://vercel.com/changelog/improved-metrics-search-in-observability-plus | Metrics search | 27, 50 |
| https://vercel.com/changelog/create-and-share-queries-with-notebooks-in-vercel-observability | Notebooks in Observability | 27, 50 |
| https://vercel.com/changelog/correlate-logs-and-traces-with-opentelemetry-in-vercel-log-drains | OpenTelemetry log drains | 27, 50 |
| https://vercel.com/changelog/html-element-attribution-in-speed-insights | Speed Insights: HTML attribution | 27, 50 |
| https://vercel.com/changelog/filter-by-custom-date-ranges-in-speed-insights | Speed Insights: 日付範囲 | 27, 50 |
| https://vercel.com/changelog/filter-by-custom-date-ranges-in-web-analytics | Web Analytics: 日付範囲 | 27, 50 |
| https://vercel.com/changelog/improved-data-collection-for-web-analytics-and-speed-insights-with-resilient | Resilient data collection | 27, 50 |

## 30-security-compliance

| URL | ページタイトル | 想定章番号 |
|---|---|---|
| https://vercel.com/docs/security | Security 概要（推定 canonical） | 30 |
| https://vercel.com/docs/compliance | Compliance（SOC2/ISO/HIPAA/GDPR、推定 canonical） | 30 |
| https://vercel.com/docs/conformance/rules/nextjs_missing_security_headers | Conformance: security headers | 30 |
| https://vercel.com/legal/dpa | Data Processing Addendum | 30 |
| https://vercel.com/changelog/hipaa-baas-are-now-available-to-pro-teams | HIPAA BAA Pro 解禁 | 30, 50 |
| https://vercel.com/changelog/openid-connect-federation-now-generally-available | OIDC Federation GA | 30, 33, 50 |

## 31-waf-and-firewall

| URL | ページタイトル | 想定章番号 |
|---|---|---|
| https://vercel.com/docs/vercel-firewall/vercel-waf | Vercel WAF | 31 |
| https://vercel.com/docs/vercel-firewall/firewall-concepts | Firewall Concepts | 31 |
| https://vercel.com/docs/vercel-firewall/firewall-api | Firewall API | 31 |
| https://vercel.com/changelog/rest-api-for-the-vercel-firewall | Firewall REST API | 31, 50 |
| https://vercel.com/changelog/create-custom-waf-rules-directly-from-the-vercel-firewall-tab | Custom WAF rules UI | 31, 50 |
| https://vercel.com/changelog/vercel-firewall-rule-builder-now-supports-or-for-rule-condition-groups | Firewall rule OR | 31, 50 |
| https://vercel.com/changelog/vercel-terraform-provider-now-supports-vercel-firewall | Terraform provider for Firewall | 31, 50 |
| https://vercel.com/changelog/improved-analytics-experience-now-available-on-the-vercel-firewall | Firewall analytics | 31, 50 |
| https://vercel.com/changelog/vercel-firewall-proactively-protects-against-vulnerability-with-middleware | Firewall proactive Middleware CVE | 31, 50 |
| https://vercel.com/changelog/vercel-firewall-protects-against-the-samlstorm-vulnerability | SAMLStorm protection | 31, 50 |
| https://vercel.com/changelog/restrict-access-with-ip-blocking-by-cidr-range | IP blocking by CIDR | 31, 50 |

## 32-bot-management-and-botid

| URL | ページタイトル | 想定章番号 |
|---|---|---|
| https://vercel.com/docs/bot-management | Bot Management | 32 |
| https://vercel.com/docs/bot-management#ai-bots-managed-ruleset | AI Bots Managed Ruleset | 32 |
| https://vercel.com/docs/botid | BotID | 32 |
| https://vercel.com/docs/botid/local-development-behavior | BotID: Local Dev Behavior | 32 |

## 33-deployment-protection-and-rbac

| URL | ページタイトル | 想定章番号 |
|---|---|---|
| https://vercel.com/docs/deployment-protection | Deployment Protection | 33 |
| https://vercel.com/docs/rbac | RBAC | 33 |
| https://vercel.com/docs/accounts | Accounts / Teams | 33 |
| https://vercel.com/changelog/protected-preview-deployments-available-on-all-plans | Protected Preview 全プラン | 33, 50 |
| https://vercel.com/changelog/access-groups-now-generally-available-on-enterprise-plans | Access Groups GA | 33, 50 |
| https://vercel.com/changelog/restrict-repository-deployments-to-specific-teams | Repo → Teams 制限 | 33, 50 |
| https://vercel.com/changelog/deployments-can-now-require-cryptographically-verified-commits | Verified commits 必須化 | 33, 50 |
| https://vercel.com/changelog/2fa-is-now-available | 2FA 提供開始 | 33, 50 |
| https://vercel.com/changelog/enhanced-security-with-new-api-scopes-for-integrations | API scopes for integrations | 33, 50 |

## 34-ddos-and-network

| URL | ページタイトル | 想定章番号 |
|---|---|---|
| https://vercel.com/docs/security/ddos-mitigation | Platform DDoS Mitigation | 34 |
| https://vercel.com/docs/vercel-firewall/ddos-mitigation | Firewall: DDoS Mitigation | 34 |
| https://vercel.com/changelog/vercel-firewall-now-stops-ddos-attacks-up-to-40x-faster | DDoS 40x faster | 34, 50 |
| https://vercel.com/changelog/strengthening-vercels-infrastructure-against-http-2-rapid-reset-attacks | HTTP/2 Rapid Reset 対策 | 34, 50 |
| https://vercel.com/changelog/improve-infrastructure-security-with-vercel-secure-compute | Vercel Secure Compute | 34, 50 |
| https://vercel.com/changelog/static-ips-are-now-available-for-more-secure-connectivity | Static IPs | 34, 50 |
| https://vercel.com/changelog/trusted-ips-is-now-generally-available-for-enterprise-customers | Trusted IPs GA | 34, 50 |
| https://vercel.com/changelog/deprecating-the-dhe-cipher-suite-for-tls-connections | DHE 廃止 | 34, 50 |

## 35-safe-zones-map

| URL | ページタイトル | 想定章番号 |
|---|---|---|
| https://vercel.com/docs/security | Security 概要（プラン別マトリクス参照用） | 35 |
| https://vercel.com/pricing | Pricing（プラン別機能比較） | 35 |
| https://vercel.com/docs/pricing/understanding-my-invoice | 請求の理解 | 35 |
| https://vercel.com/docs/production-checklist | Production Checklist（安全度評価の起点） | 35 |

## 40-v0-and-ai-sdk

| URL | ページタイトル | 想定章番号 |
|---|---|---|
| https://v0.app/docs/introduction | v0 Docs Introduction（独立サブドメイン） | 40 |
| https://vercel.com/docs/ai-sdk | AI SDK | 40 |
| https://vercel.com/academy/ai-sdk | Academy: AI SDK | 40 |
| https://vercel.com/academy/ai-sdk/basic-chatbot | Academy: Basic Chatbot | 40 |
| https://vercel.com/academy/ai-sdk/tool-use | Academy: Tool Use | 40 |
| https://vercel.com/academy/ai-sdk/structured-data-extraction | Academy: Structured Data Extraction | 40 |
| https://vercel.com/changelog/create-private-blob-stores-with-a-single-click-in-v0 | v0: Private Blob | 40, 50 |

## 41-ai-gateway

| URL | ページタイトル | 想定章番号 |
|---|---|---|
| https://vercel.com/ai-gateway | AI Gateway（プロダクト LP） | 41 |
| https://vercel.com/ai-gateway/leaderboards | AI Gateway Leaderboards | 41 |
| https://vercel.com/ai-gateway/models | AI Gateway Models | 41 |
| https://vercel.com/docs/ai-gateway | AI Gateway Docs | 41 |
| https://vercel.com/docs/ai-gateway/ecosystem | AI Gateway Ecosystem | 41 |
| https://vercel.com/docs/ai-gateway/ecosystem/framework-integrations | Framework Integrations | 41 |
| https://vercel.com/docs/ai-gateway/ecosystem/framework-integrations/pydantic-ai | Pydantic AI | 41 |
| https://vercel.com/docs/ai-gateway/ecosystem/app-attribution | App Attribution | 41 |
| https://vercel.com/docs/ai-gateway/ecosystem/stripe-billing | Stripe Billing | 41 |
| https://vercel.com/docs/ai-gateway/capabilities/zdr | ZDR | 41 |
| https://vercel.com/docs/ai-gateway/capabilities/image-generation/ai-sdk | Image Generation | 41 |
| https://vercel.com/docs/ai-gateway/chat-platforms | Chat Platforms | 41 |
| https://vercel.com/docs/ai-gateway/chat-platforms/open-webui | Open WebUI | 41 |
| https://vercel.com/docs/ai-gateway/chat-platforms/librechat | LibreChat | 41 |
| https://vercel.com/docs/ai-gateway/models-and-providers/model-variants | Model Variants | 41 |
| https://vercel.com/changelog/ai-gateway-is-now-in-beta | AI Gateway Beta | 41, 50 |
| https://vercel.com/changelog/ai-gateway-is-now-generally-available | AI Gateway GA | 41, 50 |
| https://vercel.com/changelog/openai-compatible-api-endpoints-now-supported-in-ai-gateway | OpenAI 互換 API | 41, 50 |
| https://vercel.com/changelog/access-perplexity-web-search-on-vercel-ai-gateway-with-any-model | Perplexity web search | 41, 50 |
| https://vercel.com/changelog/claude-sonnet-4-now-supports-1m-token-context-in-vercel-ai-gateway | Claude Sonnet 4 1M context | 41, 50 |
| https://vercel.com/changelog/claude-sonnet-4-6-is-live-on-ai-gateway | Claude Sonnet 4.6 | 41, 50 |
| https://vercel.com/changelog/gemini-3-pro-now-available-in-vercel-ai-gateway | Gemini 3 Pro | 41, 50 |
| https://vercel.com/changelog/gemini-3-1-pro-is-live-on-ai-gateway | Gemini 3.1 Pro | 41, 50 |
| https://vercel.com/changelog/gemini-3-flash-is-now-available-on-the-vercel-ai-gateway | Gemini 3 Flash | 41, 50 |
| https://vercel.com/changelog/gemini-3-1-flash-lite-is-now-on-ai-gateway | Gemini 3.1 Flash-Lite | 41, 50 |
| https://vercel.com/changelog/grok-4-20-on-ai-gateway | Grok 4.20 | 41, 50 |
| https://vercel.com/changelog/grok-imagine-video-on-ai-gateway | Grok Imagine Video | 41, 50 |
| https://vercel.com/changelog/glm-5-is-live-on-ai-gateway | GLM-5 | 41, 50 |
| https://vercel.com/changelog/glm-5v-turbo-on-ai-gateway | GLM-5V Turbo | 41, 50 |
| https://vercel.com/changelog/recraft-image-models-now-on-ai-gateway | Recraft image models | 41, 50 |
| https://vercel.com/changelog/openai-gpt-oss-safeguard-20b-now-available-in-vercel-ai-gateway | GPT-OSS Safeguard 20B | 41, 50 |
| https://vercel.com/changelog/moonshot-ais-kimi-k2-0905-model-is-now-supported-in-vercel-ai-gateway | Kimi K2 | 41, 50 |
| https://vercel.com/changelog/image-only-models-available-in-vercel-ai-gateway | Image-only models | 41, 50 |

## 42-mcp-and-sandbox

| URL | ページタイトル | 想定章番号 |
|---|---|---|
| https://vercel.com/docs/mcp | MCP Servers | 42 |
| https://vercel.com/docs/vercel-sandbox | Vercel Sandbox | 42 |
| https://vercel.com/docs/vercel-sandbox/sdk-reference | Sandbox SDK Reference | 42 |
| https://vercel.com/docs/rest-api/sandboxes-v2-beta/list-sandboxes | Sandbox API: list | 42 |
| https://vercel.com/docs/rest-api/sandboxes-v2-beta/get-a-command | Sandbox API: get command | 42 |
| https://vercel.com/docs/rest-api/sandboxes-v2-beta/list-commands | Sandbox API: list commands | 42 |
| https://vercel.com/docs/rest-api/sandboxes-v2-beta/kill-a-command | Sandbox API: kill command | 42 |
| https://vercel.com/docs/rest-api/sdk/sandboxes/list-snapshots | Sandbox SDK: list snapshots | 42 |
| https://vercel.com/changelog/vercel-sandboxes-ga | Sandbox GA | 42, 50 |
| https://vercel.com/changelog/vercel-sandbox-persistent-sandboxes-beta | Persistent Sandboxes Beta | 42, 50 |
| https://vercel.com/changelog/vercel-sandbox-snapshots-now-allow-custom-retention-periods | Snapshot retention | 42, 50 |
| https://vercel.com/changelog/vercel-sandboxes-now-allow-unique-customizable-names | Sandbox names | 42, 50 |
| https://vercel.com/changelog/sandbox-now-supports-sudo-and-installing-rpm-packages | Sandbox sudo/rpm | 42, 50 |
| https://vercel.com/changelog/devin-raycast-windsurf-and-goose-now-supported-on-vercel-mcp | MCP: Devin/Raycast/Windsurf/Goose | 42, 50 |
| https://vercel.com/changelog/build-mcp-server-with-nuxt | MCP server with Nuxt | 42, 50 |
| https://vercel.com/changelog/402-mcp-enables-x402-payments-in-mcp | x402 MCP payments | 42, 50 |
| https://vercel.com/kb/guide/how-to-build-an-mcp-server-with-nuxt | KB: Build MCP server with Nuxt | 42 |

## 43-ai-agents-and-claim-deployments

| URL | ページタイトル | 想定章番号 |
|---|---|---|
| https://vercel.com/agent | Agent（プロダクト LP） | 43 |
| https://vercel.com/docs/agent-resources | Agent Resources | 43 |
| https://vercel.com/docs/deployments/claim-deployments | Claim Deployments | 43 |
| https://vercel.com/kb/guide/how-to-build-ai-agents-with-vercel-and-the-ai-sdk | KB: Build AI agents | 43 |
| https://vercel.com/changelog/copy-visual-context-to-agents | Copy visual context to agents | 43, 50 |
| https://vercel.com/changelog/copy-to-prompt-instructions-now-available-for-flags | Copy-to-prompt for Flags | 43, 50 |
| https://vercel.com/changelog/vercel-flags-are-now-optimized-for-agents | Flags for agents | 43, 50 |
| https://vercel.com/academy/filesystem-agents | Academy: Filesystem Agents | 43 |
| https://vercel.com/academy/slack-agents/ai-tools-and-functions | Academy: Slack Agents | 43 |
| https://vercel.com/academy/agent-friendly-apis | Academy: Agent-friendly APIs | 43 |

## 50-changelog-digest

| URL | ページタイトル | 想定章番号 |
|---|---|---|
| https://vercel.com/changelog | Changelog 一覧（インデックス） | 50 |
| https://vercel.com/changelog/vercel-queues-now-in-public-beta | Vercel Queues Public Beta | 50 |
| https://vercel.com/changelog/vercel-flags-ga | Flags GA | 50 |
| https://vercel.com/changelog/vercel-flags-is-now-in-public-beta | Flags Public Beta | 50 |
| https://vercel.com/changelog/streamdown-v2 | Streamdown v2 | 50 |
| https://vercel.com/changelog/next-forge-6 | Next Forge 6 | 50 |
| https://vercel.com/changelog/next-js-14 | Next.js 14 | 50 |
| https://vercel.com/changelog/next-js-ai-chatbot-2-0 | Next.js AI Chatbot 2.0 | 50 |
| https://vercel.com/changelog/45-percent-faster-build-initialization | Build init 45% faster | 50 |
| https://vercel.com/changelog/turbo-build-machines | Turbo build machines | 50 |
| https://vercel.com/changelog/improved-build-compute-performance-for-enterprise-customers | Build compute Enterprise | 50 |
| https://vercel.com/changelog/access-billing-usage-cost-data-api | Billing/usage API | 50 |
| https://vercel.com/changelog/improved-hard-caps-for-spend-management | Spend management hard caps | 50 |
| https://vercel.com/changelog/cve-2026-23869 | CVE-2026-23869 | 50 |
| https://vercel.com/changelog/cve-2025-55173 | CVE-2025-55173 | 50 |
| https://vercel.com/changelog/cve-2025-55182 | CVE-2025-55182 | 50 |
| https://vercel.com/changelog/cve-2025-52662-xss-on-nuxt-devtools | CVE-2025-52662 | 50 |
| https://vercel.com/changelog/summaries-of-cve-2025-59471-and-cve-2025-59472 | CVE-2025-59471 / 59472 | 50 |

## 51-ship-week-and-roadmap

| URL | ページタイトル | 想定章番号 |
|---|---|---|
| https://vercel.com/shipped | Shipped（Ship イベント） | 51 |
| https://vercel.com/ai-accelerator | AI Accelerator | 51 |
| https://vercel.com/changelog/improved-infrastructure-pricing-is-now-active-for-new-customers | Infrastructure pricing 改善 | 51 |

## 60-cli-and-rest-api-index

| URL | ページタイトル | 想定章番号 |
|---|---|---|
| https://vercel.com/docs/cli | Vercel CLI（推定 canonical） | 60 |
| https://vercel.com/docs/cli/contract | CLI Contract | 60 |
| https://vercel.com/docs/rest-api | REST API（推定 canonical） | 60 |
| https://vercel.com/docs/rest-api/errors | REST API Errors | 60 |
| https://vercel.com/docs/rest-api/sdk/connect/create-a-secure-compute-network | REST API: Secure Compute | 60 |
| https://vercel.com/docs/rest-api/sdk/integrations/retrieve-an-integration-configuration | REST API: Integrations | 60 |
| https://vercel.com/docs/rest-api/sdk/logs/get-logs-for-a-deployment | REST API: Logs | 60 |
| https://vercel.com/docs/rest-api/drains/retrieve-a-list-of-all-drains | REST API: Drains | 60 |
| https://vercel.com/docs/build-output-api | Build Output API | 60 |
| https://vercel.com/changelog/activity-log-now-available-in-vercel-cli | Activity log in CLI | 60, 50 |
| https://vercel.com/changelog/improved-cli-experience-when-linking-and-creating-environment-variables | CLI env vars UX | 60, 50 |

## 90-product-hints

| URL | ページタイトル | 想定章番号 |
|---|---|---|
| https://vercel.com/pricing | Pricing | 90 |
| https://vercel.com/docs/pricing/understanding-my-invoice | Understanding my Invoice | 90 |
| https://vercel.com/docs/pricing/regional-pricing/iad1 | Regional Pricing: iad1（代表例） | 90 |
| https://vercel.com/docs/queues/pricing | Queues Pricing | 90 |
| https://vercel.com/customers/datocms-builds-60-faster-with-a-streamlined-workflow | 顧客事例: DatoCMS | 90 |
| https://vercel.com/customers/super-serves-thousands-of-domains-on-one-project-with-next-js-and-vercel | 顧客事例: Super | 90 |

## 99-sources

| URL | ページタイトル | 想定章番号 |
|---|---|---|
| https://vercel.com/sitemap.xml | Vercel sitemap.xml | 99 |
| https://vercel.com/docs | Vercel Documentation トップ | 99 |
| https://vercel.com/docs/sitemap | Docs サイトマップ | 99 |
| https://vercel.com/changelog | Changelog 一覧 | 99 |
| https://vercel.com/kb | Knowledge Base | 99 |
| https://vercel.com/legal/dpa | DPA | 99 |
| https://v0.app/docs/introduction | v0 Docs（独立サブドメイン） | 99 |

---

## 除外候補（スコープ外）

| URL | 理由 |
|---|---|
| https://vercel.com/careers/* （全件） | 採用情報（教材スコープ外） |
| https://vercel.com/geist/badge | デザインシステム Geist のコンポーネントカタログ（教材外） |
| https://vercel.com/geist/menu | 同上 |
| https://vercel.com/contact/sales/nextjs | 営業問い合わせ |
| https://vercel.com/blog/* | ブログ記事（changelog 章でカバー、必要に応じ個別取得） |
| https://vercel.com/changelog/april-2022-papercuts | 2 年以上前の papercuts（鮮度不足） |
| https://vercel.com/changelog/september-2022-papercuts | 同上 |
| https://vercel.com/changelog/january-2023 | 月次まとめ（個別 changelog でカバー済） |
| https://vercel.com/changelog/march-2023 | 同上 |
| https://vercel.com/changelog/node-js-14-lts-is-now-available | 旧 Node.js LTS（既に非推奨） |
| https://vercel.com/changelog/node-js-16-lts-is-now-available | 同上 |
| https://vercel.com/changelog/node-js-16-deprecation | 同上（履歴のみ） |
| https://vercel.com/changelog/node-js-18-is-being-deprecated | 旧 Node.js（履歴のみ、必要なら 24 章に補足） |
| https://vercel.com/docs/pricing/regional-pricing/{fra1,gru1,kix1,hkg1,lhr1,pdx1,sfo1,sin1,syd1,yul1,hnd1,icn1} | リージョン別価格詳細（代表として iad1 のみ採用） |
| https://vercel.com/docs/errors/* | 個別エラーページ（参照リファレンスとして必要時に直接参照） |
| https://vercel.com/docs/conformance/rules/nextjs_missing_react_strict_mode | Conformance ルール詳細（30 章で代表のみ採用） |
| https://vercel.com/academy/* （上記で採用済以外） | Academy 詳細レッスン（必要時に個別追加） |

---

## サマリ

- 採用 URL（22 章合計）：合計 **約 195 件**
- 除外候補：合計 **約 30 件**（カテゴリ単位で集約しているため実 URL 数はさらに多い）
- 特筆事項：
  - **v0 は独立サブドメイン**（`v0.app/docs/...`）で運用されており、Vercel ドメイン配下には存在しない。
  - **AI Gateway** は `/docs/ai-gateway/*`（仕様）と `/ai-gateway`、`/ai-gateway/leaderboards`、`/ai-gateway/models`（プロダクト LP）が併存し、教材化時は両方リンクが必要。
  - **Vercel Sandbox** は `/docs/vercel-sandbox/*`（SDK リファレンス）と `/docs/rest-api/sandboxes-v2-beta/*`（REST API ベータ）の二系統あり、42 章では両方を採用。
  - **Changelog** は単独ページ単位の URL が膨大（500+）あるため、章 50 では「重要マイルストーン」と「直近 12〜18 ヶ月」の代表 URL に絞った。月次まとめ（`/changelog/{month}-{year}`）と古い Node.js LTS リリースは除外候補へ。
  - 一部 canonical URL（`/docs/security`、`/docs/compliance`、`/docs/domains`、`/docs/cli`、`/docs/rest-api`、`/docs/speed-insights`）は sitemap WebFetch のサンプリング上限により直接ヒットしなかったため、`/docs` ランディングのナビ構造から推定して採用した（教材編集時に存在確認＆リダイレクト追跡が必要）。
