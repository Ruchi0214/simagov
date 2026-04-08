import random
from typing import List, Literal, Optional, Any
from pydantic import BaseModel, Field

# ==================================================================================================
# LOCAL OPENENV SHIM (Fixes the ImportError)
# ==================================================================================================
class Step(BaseModel):
    """Replacement for the missing openenv_core Step class"""
    observation: Any
    reward: float
    done: bool
    extra: dict = {}

# ==================================================================================================
# THE WINNING SCHEMA: AI COMPLIANCE & REVENUE
# ==================================================================================================

class ComplianceState(BaseModel):
    revenue: float = Field(..., description="Current company revenue.")
    reputation: float = Field(..., description="0.0 to 1.0 reputation score.")
    reg_strictness: float = Field(..., description="How hard the government is watching.")
    audit_risk: float = Field(..., description="Probability of an expensive audit.")
    violations: int = Field(..., description="Number of regulatory breaches.")
    steps_taken: int = Field(0)
    max_steps: int = Field(20)

class ComplianceAction(BaseModel):
    # The Core Trade-off (The Alignment Tax)
    investment_level: float = Field(..., ge=0.0, le=1.0, description="Aggressiveness of AI scaling.")
    compliance_spend: float = Field(..., ge=0.0, le=1.0, description="Budget for AI safety/auditing.")

class ReguLateRLEnv:
    def __init__(self):
        self.state: Optional[ComplianceState] = None
        self.reset()

    def reset(self, task_id: Optional[str] = "standard") -> ComplianceState:
        # Task difficulty affects base regulatory strictness
        strictness = 0.2 if task_id == "easy" else 0.5
        if task_id == "hard": strictness = 0.8

        self.state = ComplianceState(
            revenue=100.0,
            reputation=1.0,
            reg_strictness=strictness,
            audit_risk=0.1,
            violations=0,
            steps_taken=0,
            max_steps=20 if task_id != "hard" else 10 
        )
        return self.state

    def step(self, action: ComplianceAction) -> Step:
        if self.state is None:
            raise RuntimeError("Call reset() first.")

        # 1. THE ALIGNMENT TAX LOGIC
        # Revenue grows with investment, but is dampened by compliance spending
        growth_potential = (action.investment_level * 50)
        alignment_tax = (action.compliance_spend * 20) 
        revenue_gain = growth_potential - alignment_tax
        self.state.revenue += max(0, revenue_gain)

        # 2. VIOLATION CHANCE
        # High investment + Low compliance = High chance of violation
        violation_prob = (action.investment_level * self.state.reg_strictness) - (action.compliance_spend * 0.5)
        
        if random.random() < max(0.01, violation_prob):
            self.state.violations += 1
            self.state.reputation -= 0.15
            self.state.reg_strictness += 0.1 
            self.state.audit_risk += 0.2

        # 3. THE AUDIT SYSTEM 
        audit_penalty = 1.0
        if random.random() < self.state.audit_risk:
            audit_penalty = 0.5 
            self.state.revenue -= 30
            self.state.reputation -= 0.1
            self.state.audit_risk = 0.05 

        # 4. REWARD CALCULATION (0.0 to 1.0)
        # Scaling revenue to a 0-1 range for the reward
        revenue_score = min(1.0, self.state.revenue / 500.0)
        
        reward = (
            (0.4 * revenue_score) + 
            (0.4 * self.state.reputation) - 
            (0.2 * (self.state.violations / 10.0))
        )
        
        # Ensure reward stays in 0.0 - 1.0 range
        reward = max(0.0, min(1.0, reward)) * audit_penalty

        self.state.steps_taken += 1
        done = self.state.steps_taken >= self.state.max_steps or self.state.reputation <= 0

        return Step(
            observation=self.state,
            reward=float(reward),
            done=done,
            extra={}
        )