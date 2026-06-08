# agentic-agile — developer & release entrypoint.
# Run `make` (no target) for help.

SHELL        := bash
.DEFAULT_GOAL := help

PLUGIN       := agentic-agile
MARKET       := agentic-agile-marketplace
PLUGIN_DIR   := plugin
CTX          := plugin/tools/ctx-symbols
BIN_DIR      ?= $(HOME)/.local/bin
REPO         := $(CURDIR)
VERSION      := $(shell python3 -c "import json;print(json.load(open('plugin/.claude-plugin/plugin.json'))['version'])")
TAG          := v$(VERSION)

# Colors
C := \033[36m
B := \033[1m
R := \033[0m

.PHONY: help
help: ## Show this help
	@printf "$(B)agentic-agile$(R)  v$(VERSION)\n\n"
	@printf "Usage: make $(C)<target>$(R)\n\n"
	@grep -hE '^[a-zA-Z0-9_-]+:.*?## ' $(MAKEFILE_LIST) \
	  | sort | awk 'BEGIN{FS=":.*?## "}{printf "  $(C)%-16s$(R) %s\n",$$1,$$2}'

# ── Build / install ────────────────────────────────────────────────
.PHONY: build
build: ## Build ctx-symbols (release)
	cd $(CTX) && cargo build --release

.PHONY: install
install: ## Build + install ctx-symbols to BIN_DIR (and md-db guidance)
	./plugin/tools/install.sh "$(BIN_DIR)"

.PHONY: link
link: ## Register THIS repo as a local marketplace and install the plugin (dev)
	@command -v claude >/dev/null || { echo "claude CLI not found — install: curl -fsSL https://claude.ai/install.sh | bash -s stable"; exit 1; }
	claude plugin marketplace add "$(REPO)"
	claude plugin install "$(PLUGIN)@$(MARKET)"

.PHONY: unlink
unlink: ## Uninstall the plugin and remove the local marketplace
	-claude plugin uninstall "$(PLUGIN)@$(MARKET)"
	-claude plugin marketplace remove "$(MARKET)"

# ── Format / lint / test ───────────────────────────────────────────
.PHONY: fmt
fmt: ## Format ctx-symbols
	cd $(CTX) && cargo fmt

.PHONY: fmt-check
fmt-check: ## Check formatting (no writes)
	cd $(CTX) && cargo fmt --all -- --check

.PHONY: clippy
clippy: ## Clippy with warnings-as-errors
	cd $(CTX) && cargo clippy --all-targets -- -D warnings

.PHONY: shellcheck
shellcheck: ## Lint gate scripts (skipped with a warning if shellcheck is absent)
	@command -v shellcheck >/dev/null \
	  && shellcheck -S error -e SC1091 plugin/bin/_gatelib.sh plugin/bin/gate-* plugin/bin/log-execution \
	  || echo "WARN: shellcheck not installed; skipping (CI enforces it)"

.PHONY: json
json: ## Validate plugin.json + marketplace.json
	@python3 -c "import json;json.load(open('plugin/.claude-plugin/plugin.json'));json.load(open('.claude-plugin/marketplace.json'));print('JSON ok')"

.PHONY: lint
lint: clippy shellcheck json ## Run all linters

.PHONY: test
test: ## Run ctx-symbols tests
	cd $(CTX) && cargo test --all-targets

.PHONY: validate
validate: json ## claude plugin validate --strict
	@command -v claude >/dev/null || { echo "claude CLI not found — install: curl -fsSL https://claude.ai/install.sh | bash -s stable"; exit 1; }
	claude plugin validate ./plugin --strict

.PHONY: ci
ci: fmt-check lint test ## Run everything CI runs (except the live claude install)

# ── Release / publish ──────────────────────────────────────────────
.PHONY: version
version: ## Print the current version
	@echo "$(VERSION)"

.PHONY: version-check
version-check: ## Assert plugin.json, Cargo.toml, and CHANGELOG agree
	@python3 scripts/version-check.py

.PHONY: release
release: ci validate version-check ## Verify, then create annotated git tag vX.Y.Z
	@git rev-parse --git-dir >/dev/null 2>&1 || { echo "not a git repo — run: git init && git add -A && git commit -m init"; exit 1; }
	@test -z "$$(git status --porcelain)" || { echo "working tree dirty — commit first"; exit 1; }
	@git rev-parse "$(TAG)" >/dev/null 2>&1 && { echo "tag $(TAG) already exists"; exit 1; } || true
	git tag -a "$(TAG)" -m "agentic-agile $(TAG)"
	@echo "Tagged $(TAG). Run 'make publish' to push."

.PHONY: publish
publish: ## Push the current branch + tags to origin (run after `make release`)
	@git rev-parse --git-dir >/dev/null 2>&1 || { echo "not a git repo"; exit 1; }
	@git remote get-url origin >/dev/null 2>&1 || { echo "no 'origin' remote — git remote add origin <url>"; exit 1; }
	git push origin HEAD
	git push origin --tags
	@echo "Published. Users: /plugin marketplace add <repo-url> && /plugin install $(PLUGIN)@$(MARKET)"

# ── Hooks / housekeeping ───────────────────────────────────────────
.PHONY: hooks
hooks: ## Install the tracked git hooks (sets core.hooksPath)
	git config core.hooksPath .githooks
	chmod +x .githooks/* 2>/dev/null || true
	@echo "git hooks installed (.githooks): pre-commit, pre-push"

.PHONY: smoke
smoke: build ## Quick offline gate smoke test (structural gate on a tmp tree)
	@export PATH="$(BIN_DIR):$$PATH"; \
	  cp "$(CTX)/target/release/ctx-symbols" "$(BIN_DIR)/ctx-symbols" 2>/dev/null || true; \
	  T=$$(mktemp -d); printf 'pub fn a(){let x=1;}\npub fn caller(){a();}\n' > "$$T/a.rs"; \
	  REPO_DIR="$$T" CLAUDE_PLUGIN_ROOT="$(CURDIR)/plugin" plugin/bin/gate-structural-integrity; \
	  echo "structural gate exit=$$?"; rm -rf "$$T"

.PHONY: clean
clean: ## Remove build artifacts
	cd $(CTX) && cargo clean
