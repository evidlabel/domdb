# Self-documenting Makefile for domdb. Run `make` or `make help`.
.DEFAULT_GOAL := help

DOMDB   ?= uv run domdb
CASES   ?= ~/domdatabasen/cases
BIB_OUT ?= resources/cases.bib
HAY_OUT ?= resources/cases.yml
MD_OUT  ?= resources/cases.md
N       ?=

ifneq ($(strip $(N)),)
N_FLAG := -n $(N)
else
N_FLAG :=
endif

.PHONY: help sync run download docs readme bib hay md test

help: ## Show this help (default)
	@echo ""
	@echo "  domdb — Danish judicial verdicts → BibTeX / Hayagriva / Markdown / EVID"
	@echo ""
	@grep -hE '^[a-zA-Z0-9_-]+:.*?## ' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "  Variables (override on the command line):"
	@printf "    \033[36m%-12s\033[0m %s\n" "CASES"   "$(CASES)"
	@printf "    \033[36m%-12s\033[0m %s\n" "BIB_OUT" "$(BIB_OUT)"
	@printf "    \033[36m%-12s\033[0m %s\n" "HAY_OUT" "$(HAY_OUT)"
	@printf "    \033[36m%-12s\033[0m %s\n" "MD_OUT"  "$(MD_OUT)"
	@printf "    \033[36m%-12s\033[0m %s\n" "N"       "$(if $(N),$(N),-1 (all))"
	@echo ""
	@echo "  Examples:"
	@echo "    make run"
	@echo "    make docs"
	@echo "    make bib"
	@echo "    make hay"
	@echo "    make bib N=100 BIB_OUT=cases.bib"
	@echo "    make hay N=100 HAY_OUT=cases.yml"
	@echo "    make bib CASES=./cases"
	@echo ""

sync: ## Install/update the project venv (uv sync)
	uv sync

run: download ## Download latest verdicts into the local case cache

download: ## Download latest verdicts into the local case cache
	$(DOMDB) -d $(CASES) download

docs: ## Show CLI help tree (domdb -h)
	$(DOMDB) -h

readme: ## Print the project README
	@cat README.md

bib: ## Compile cached JSON verdicts into BibTeX
	@mkdir -p $(dir $(BIB_OUT))
	$(DOMDB) -d $(CASES) output bib -o $(BIB_OUT) $(N_FLAG)
	@echo "Wrote $(BIB_OUT)"

hay: ## Compile cached JSON verdicts into Hayagriva YAML (Typst)
	@mkdir -p $(dir $(HAY_OUT))
	$(DOMDB) -d $(CASES) output hay -o $(HAY_OUT) $(N_FLAG)
	@echo "Wrote $(HAY_OUT)"

md: ## Compile cached JSON verdicts into Markdown
	@mkdir -p $(dir $(MD_OUT))
	$(DOMDB) -d $(CASES) output md -o $(MD_OUT) $(N_FLAG)
	@echo "Wrote $(MD_OUT)"

test: ## Run the test suite
	uv run pytest -v
