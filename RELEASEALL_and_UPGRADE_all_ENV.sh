pip_upgrade_cmd="pip install -U coaiapy coaiapy-mcp"

./release-all.sh && \
	conda activate src && \
	$pip_upgrade_cmd && \
	conda activate jgtsd && \
	$pip_upgrade_cmd

