# Data Collection Module

Systematic experimentation framework for understanding market mechanics.

## Quick Start

```bash
# Run single experiment
python -m collectors.runner --scenario normal_market --experiment passive --name team --password pwd --host ip:port --secure

# List available experiments
python -m collectors.runner --list-experiments

# Run all experiments for one scenario
python -m collectors.runner --scenario flash_crash --all-experiments --name team --password pwd --host ip:port --secure
```

## Components

- **logger.py** - Structured JSONL logging
- **strategies.py** - Pluggable experiment strategies
- **bot.py** - Extended TradingBot with logging
- **runner.py** - Experiment orchestration CLI

## Usage

See `DATA_COLLECTION_README.md` in the root directory for full documentation.

