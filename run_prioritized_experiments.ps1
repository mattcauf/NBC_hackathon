# Prioritized Experiment Runner - Cross-Scenario Data Collection
# Runs critical experiments across all scenarios for strategy development

param(
    [string]$Name = "Three-Bayesians",
    [string]$Password = "Limit_Up_Limit_D0wn!",
    [string]$ServerHost = "3.98.52.120:8433",
    [switch]$Secure
)

$ErrorActionPreference = "Continue"

Write-Host "========================================"
Write-Host "Prioritized Cross-Scenario Experiment Runner"
Write-Host "========================================"
Write-Host "Team: $Name"
Write-Host "Host: $ServerHost"
Write-Host "Secure: $Secure"
Write-Host "========================================"
Write-Host ""
Write-Host "This will run critical experiments across all scenarios:"
Write-Host "  Phase 1: Crash understanding (flash_crash, mini_flash_crash)"
Write-Host "  Phase 2: Market regime understanding (stressed_market, hft_dominated)"
Write-Host ""
Write-Host "Starting in 3 seconds..."
Start-Sleep -Seconds 3
Write-Host ""

# Define experiments as: scenario,experiment,description
$experiments = @(
    @("flash_crash", "passive", "Baseline crash dynamics"),
    @("mini_flash_crash", "passive", "Baseline mini crash dynamics"),
    @("flash_crash", "qty_300", "Test winning strategy in flash crash"),
    @("mini_flash_crash", "qty_300", "Test winning strategy in mini crash"),
    @("stressed_market", "passive", "Baseline stressed market dynamics"),
    @("hft_dominated", "passive", "Baseline HFT-dominated market dynamics"),
    @("stressed_market", "qty_300", "Test winning strategy in stressed market"),
    @("hft_dominated", "qty_300", "Test winning strategy in HFT-dominated market")
)

$total = $experiments.Count
$current = 0
$successful = 0
$failed = 0
$failedExperiments = @()

foreach ($exp in $experiments) {
    $scenario = $exp[0]
    $experiment = $exp[1]
    $description = $exp[2]
    $current++
    
    if ($current -le 4) {
        $phase = "1"
    } else {
        $phase = "2"
    }
    
    Write-Host ""
    Write-Host "========================================"
    Write-Host "[$current/$total] Phase $phase"
    Write-Host "========================================"
    Write-Host "Scenario: $scenario"
    Write-Host "Experiment: $experiment"
    Write-Host "Description: $description"
    Write-Host "----------------------------------------"
    
    # Build command
    $cmd = "python -m collectors.runner --scenario $scenario --experiment $experiment --name `"$Name`" --password `"$Password`" --host $ServerHost"
    
    if ($Secure) {
        $cmd = $cmd + " --secure"
    }
    
    # Run experiment
    $startTime = Get-Date
    try {
        Invoke-Expression $cmd
        $exitCode = $LASTEXITCODE
        $endTime = Get-Date
        $duration = [math]::Round(($endTime - $startTime).TotalSeconds)
        
        if ($exitCode -eq 0) {
            $successful++
            Write-Host ""
            Write-Host "[OK] Success: $scenario : $experiment (took $duration s)"
        } else {
            $failed++
            $failedExperiments += "$scenario : $experiment"
            Write-Host ""
            Write-Host "[FAIL] Failed: $scenario : $experiment (took $duration s)"
        }
    }
    catch {
        $endTime = Get-Date
        $duration = [math]::Round(($endTime - $startTime).TotalSeconds)
        $failed++
        $failedExperiments += "$scenario : $experiment"
        Write-Host ""
        Write-Host "[FAIL] Failed: $scenario : $experiment (took $duration s)"
        Write-Host "Error: $_"
    }
    
    # Delay between runs (except for last one)
    if ($current -lt $total) {
        Write-Host ""
        Write-Host "Waiting 5 seconds before next experiment..."
        Start-Sleep -Seconds 5
    }
}

Write-Host ""
Write-Host "========================================"
Write-Host "Batch Run Complete"
Write-Host "========================================"
Write-Host "Successful: $successful / $total"
Write-Host "Failed: $failed / $total"
Write-Host "========================================"

if ($failedExperiments.Count -gt 0) {
    Write-Host ""
    Write-Host "Failed experiments:"
    foreach ($failedExp in $failedExperiments) {
        Write-Host "  - $failedExp"
    }
}

Write-Host ""
Write-Host "Generating summary report..."
python -m analysis.summary --summary

Write-Host ""
Write-Host "Generating synthesis report..."
python -m analysis.synthesize

Write-Host ""
Write-Host "========================================"
Write-Host "Analysis Complete"
Write-Host "========================================"
Write-Host "Check the following files:"
Write-Host "  - data/processed/summary_report.csv"
Write-Host "  - data/processed/synthesis_report.md"
Write-Host "========================================"
