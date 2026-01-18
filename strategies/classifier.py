"""
Regime Classifier
=================
Classify market into regimes based on metrics.
"""

from strategies.metrics import IncrementalMetrics


class RegimeClassifier:
    """
    Classifies market regime based on observable signals.
    """
    
    # Regime constants
    CALIBRATING = "CALIBRATING"
    NORMAL = "NORMAL"
    STRESSED = "STRESSED"
    CRASH = "CRASH"
    HFT = "HFT"
    RECOVERY = "RECOVERY"
    
    def __init__(self):
        self.current_regime = self.CALIBRATING
        self.previous_regime = self.CALIBRATING
        self.regime_duration = 0
        self.crash_cooldown = 0  # Steps since last crash
    
    def classify(self, metrics: IncrementalMetrics) -> str:
        """
        Determine current market regime based on metrics.
        
        Args:
            metrics: IncrementalMetrics instance with current market state
            
        Returns:
            Regime string (CALIBRATING, NORMAL, STRESSED, CRASH, HFT, RECOVERY)
        """
        self.previous_regime = self.current_regime
        
        # Still calibrating
        if not metrics.calibrated:
            self.current_regime = self.CALIBRATING
            return self.current_regime
        
        # Extract signals
        spread_ratio = metrics.spread_ratio
        depth_ratio = metrics.depth_ratio
        abs_velocity = abs(metrics.price_velocity)
        abs_imbalance = abs(metrics.imbalance)
        churn = metrics.churn_rate
        
        # --- CRASH detection (highest priority) ---
        # Lowered thresholds to catch mini flash crashes
        # Also added compound condition: multiple elevated signals = crash
        is_crash = (
            spread_ratio > 2.0 or           # Lowered from 2.5
            abs_velocity > 0.10 or          # Lowered from 0.15
            abs_imbalance > 0.5 or          # Lowered from 0.6
            # Compound: multiple stressed signals together indicate crash
            (spread_ratio > 1.8 and abs_velocity > 0.06) or
            (spread_ratio > 1.8 and abs_imbalance > 0.4) or
            (abs_velocity > 0.08 and abs_imbalance > 0.45)
        )
        
        if is_crash:
            self.current_regime = self.CRASH
            self.crash_cooldown = 0
        
        # --- RECOVERY detection (recently exited crash) ---
        elif self.previous_regime == self.CRASH and spread_ratio < 1.8:
            self.current_regime = self.RECOVERY
            self.crash_cooldown = 100  # Stay cautious for 100 steps
        
        elif self.current_regime == self.RECOVERY:
            self.crash_cooldown -= 1
            if self.crash_cooldown <= 0 and spread_ratio < 1.5:
                # Transition out of recovery
                self.current_regime = self.NORMAL
        
        # --- STRESSED detection (with hysteresis) ---
        # BUG FIX: Changed from 'if' to 'elif' to properly chain with CRASH detection
        elif self.previous_regime == self.STRESSED:
            STRESSED_EXIT = 1.2
            # Already in STRESSED: exit only if conditions improve significantly
            if spread_ratio > STRESSED_EXIT or abs_imbalance > 0.3 or depth_ratio < 0.6:
                self.current_regime = self.STRESSED
            else:
                self.current_regime = self.NORMAL
        
        elif spread_ratio > 1.5 or abs_imbalance > 0.4 or depth_ratio < 0.5:
            # Enter STRESSED from NORMAL
            self.current_regime = self.STRESSED
        
        # --- HFT detection (high churn but not crashing) ---
        else:
            HFT_ENTER = 0.20
            HFT_EXIT = 0.12
            stable_enough = spread_ratio < 1.6 and depth_ratio > 0.4 and abs_velocity < 0.08
            
            if self.previous_regime == self.HFT:
                if stable_enough and churn >= HFT_EXIT:
                    self.current_regime = self.HFT
                else:
                    self.current_regime = self.NORMAL
            else:
                if stable_enough and churn >= HFT_ENTER:
                    self.current_regime = self.HFT
                else:
                    self.current_regime = self.NORMAL
        
        # Track duration
        if self.current_regime == self.previous_regime:
            self.regime_duration += 1
        else:
            self.regime_duration = 0
        
        return self.current_regime
