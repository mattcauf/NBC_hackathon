#!/bin/bash
# Prioritized Experiment Runner - Cross-Scenario Data Collection
# Runs critical experiments across all scenarios for strategy development

NAME="${1:-Three-Bayesians}"
PASSWORD="${2:-Limit_Up_Limit_D0wn!}"
HOST="${3:-3.98.52.120:8433}"
SECURE="${4:-secure}"

echo "========================================"
echo "Prioritized Cross-Scenario Experiment Runner"
echo "========================================"
echo "Team: $NAME"
echo "Host: $HOST"
echo "Secure: $SECURE"
echo "========================================"
echo ""
echo "This will run critical experiments across all scenarios:"
echo "  Phase 1: Crash understanding (flash_crash, mini_flash_crash)"
echo "  Phase 2: Market regime understanding (stressed_market, hft_dominated)"
echo ""
echo "Starting in 3 seconds..."
sleep 3
echo ""

# Define experiments as: scenario:experiment:description
experiments=(
    # Phase 1: Critical Crash Understanding
    "flash_crash:passive:Baseline crash dynamics"
    "mini_flash_crash:passive:Baseline mini crash dynamics"
    "flash_crash:qty_300:Test winning strategy in flash crash"
    "mini_flash_crash:qty_300:Test winning strategy in mini crash"
    
    # Phase 2: Market Regime Understanding
    "stressed_market:passive:Baseline stressed market dynamics"
    "hft_dominated:passive:Baseline HFT-dominated market dynamics"
    "stressed_market:qty_300:Test winning strategy in stressed market"
    "hft_dominated:qty_300:Test winning strategy in HFT-dominated market"
)

total=${#experiments[@]}
current=0
successful=0
failed=0
failed_experiments=()

for exp_config in "${experiments[@]}"; do
    IFS=':' read -r scenario experiment description <<< "$exp_config"
    current=$((current + 1))
    
    echo ""
    echo "========================================"
    echo "[$current/$total] Phase $([ $current -le 4 ] && echo '1' || echo '2')"
    echo "========================================"
    echo "Scenario: $scenario"
    echo "Experiment: $experiment"
    echo "Description: $description"
    echo "----------------------------------------"
    
    # Build command
    cmd="python -m collectors.runner --scenario $scenario --experiment $experiment --name \"$NAME\" --password \"$PASSWORD\" --host $HOST"
    
    if [ -n "$SECURE" ]; then
        cmd="$cmd --secure"
    fi
    
    # Run experiment
    start_time=$(date +%s)
    if eval $cmd; then
        end_time=$(date +%s)
        duration=$((end_time - start_time))
        successful=$((successful + 1))
        echo ""
        echo "✓ Success: $scenario:$experiment (took ${duration}s)"
    else
        end_time=$(date +%s)
        duration=$((end_time - start_time))
        failed=$((failed + 1))
        failed_experiments+=("$scenario:$experiment")
        echo ""
        echo "✗ Failed: $scenario:$experiment (took ${duration}s)"
    fi
    
    # Delay between runs (except for last one)
    if [ $current -lt $total ]; then
        echo ""
        echo "Waiting 5 seconds before next experiment..."
        sleep 5
    fi
done

echo ""
echo "========================================"
echo "Batch Run Complete"
echo "========================================"
echo "Successful: $successful/$total"
echo "Failed: $failed/$total"
echo "========================================"

if [ ${#failed_experiments[@]} -gt 0 ]; then
    echo ""
    echo "Failed experiments:"
    for failed_exp in "${failed_experiments[@]}"; do
        echo "  - $failed_exp"
    done
fi

echo ""
echo "Generating summary report..."
python -m analysis.summary --summary

echo ""
echo "Generating synthesis report..."
python -m analysis.synthesize

echo ""
echo "========================================"
echo "Analysis Complete"
echo "========================================"
echo "Check the following files:"
echo "  - data/processed/summary_report.csv"
echo "  - data/processed/synthesis_report.md"
echo "========================================"

