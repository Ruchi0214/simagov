import os
import json
from openai import OpenAI
from env import ReguLateRLEnv, ComplianceAction
# We are setting DEFAULT values so the script runs even if the environment is empty.
# Required environment variables
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
HF_TOKEN = os.getenv("HF_TOKEN", "")

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

def run_inference():
    env = ReguLateRLEnv()
    obs = env.reset(task_id="standard")
    
    print(f"[START] task_id=standard")
    
    total_reward = 0
    done = False
    step_count = 0
    
    while not done and step_count < 20:
        # Simple heuristic for the baseline: 70% investment, 30% compliance
        action = ComplianceAction(investment_level=0.7, compliance_spend=0.3)
        
        step_data = env.step(action)
        total_reward += step_data.reward
        
        # REQUIRED LOG FORMAT
        log_entry = {
            "step": step_count,
            "observation": step_data.observation.dict(),
            "reward": step_data.reward,
            "done": step_data.done
        }
        print(f"[STEP] {json.dumps(log_entry)}")
        
        done = step_data.done
        step_count += 1
    
    avg_score = total_reward / step_count
    print(f"[END] score={avg_score}")

if __name__ == "__main__":
    run_inference()