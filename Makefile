.EXPORT_ALL_VARIABLES:
.PHONY: MAKECMDGOALS

# Self-documenting Makefile
# https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
help:  ## Print this help
	@grep -E '^[a-zA-Z][^:]*:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

requirements:  ## Install requirements
	poetry install

update:  ## Update requirements
	poetry update

test: requirements  ## Run unittests
	poetry run pytest

run:  ## Run script
	poetry run lxc-provision
