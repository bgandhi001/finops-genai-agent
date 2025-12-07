import json
import random
from datetime import datetime

# ==============================================================================
# PROTOTYPE: FinOps GenAI Agent (CUR-Only Mode)
# 
# This script demonstrates how the "Agent" connects the SQL results (from Athena)
# to the LLM to generate insights.
# ==============================================================================

def mock_run_athena_query(query_name):
    """
    Simulates executing the SQL queries we wrote against Athena.
    Returns mocked list of dictionaries (rows).
    """
    print(f"[*] Running Athena Query: {query_name}...")
    
    # Scenario 1: Architecture Inference (Result of Query #1 from athena_architecture_inference.sql)
    if query_name == "cross_az_traffic":
        return [
            {
                "line_item_product_code": "AmazonEC2",
                "line_item_usage_type": "USE2-DataTransfer-Regional-Bytes",
                "line_item_availability_zone": "us-east-2a",
                "total_gb": 50000, 
                "total_cost": 450.00
            },
            {
                "line_item_product_code": "AmazonEC2",
                "line_item_usage_type": "USE2-DataTransfer-Regional-Bytes",
                "line_item_availability_zone": "us-east-2b",
                "total_gb": 48000, 
                "total_cost": 432.00
            }
        ]

    # Scenario 2: Tagging Correlation (Result of Query #1 from athena_tagging_correlation.sql)
    elif query_name == "tagging_correlation":
        return [
            {
                "untagged_resource": "vol-0abcdef1234567890",
                "first_seen_time": "2023-11-15T14:00:00Z",
                "untagged_spend": 45.00,
                "tagged_neighbor": "i-0123456789abcdef0",
                "neighbor_project": "PaymentsAPI",
                "neighbor_cost_center": "CC-998"
            },
            {
                "untagged_resource": "vol-0abcdef1234567890", # Same resource matches another neighbor
                "first_seen_time": "2023-11-15T14:00:00Z",
                "untagged_spend": 45.00,
                "tagged_neighbor": "lb-app-prod-v2",
                "neighbor_project": "PaymentsAPI", # Consistent project
                "neighbor_cost_center": "CC-998"
            }
        ]
    return []

def mock_llm_call(prompt):
    """
    Simulates sending the prompt to a model like GPT-4 or Claude 3.
    """
    print(f"\n[>] Sending Prompt to LLM:\n{'-'*40}\n{prompt}\n{'-'*40}\n")
    
    # In a real app, this would be: response = bedrock_client.invoke_model(...)
    
    # Heuristic response generation based on prompt content
    if "Cross-AZ" in prompt:
        return (
            "**Insight:** I detected high Cross-AZ data transfer ($882/mo) between "
            "us-east-2a and us-east-2b.\n"
            "**Inference:** This suggests a 'chatty' microservice architecture where "
            "services in Zone A are heavily querying Zone B.\n"
            "**Recommendation:** \n"
            "1. Identify the specific services (likely EC2 or RDS) involved.\n"
            "2. If possible, configure clients to prefer 'local' endpoints to avoid the hop.\n"
            "3. **Estimated Savings:** ~$882/month."
        )
    elif "untagged resource" in prompt.lower():
        return (
            "**Analysis:** I found untagged volume `vol-0abcdef...` ($45/mo).\n"
            "**Evidence:** It was created at `2023-11-15 14:00:00`, the exact same hour as "
            "instance `i-01234...` and load balancer `lb-app-prod-v2`.\n"
            "**Conclusion:** Both 'neighbors' are tagged `Project: PaymentsAPI`.\n"
            "**Confidence:** HIGH (95%).\n"
            "**Action:** I recommend applying tag `Project: PaymentsAPI` to `vol-0abcdef...`."
        )
    return "No insight generated."

# ==============================================================================
# AGENT LOGIC: ARCHITECTURE INFERENCER
# ==============================================================================
def run_architecture_agent():
    print("\n=== RUNNING AGENT: ARCHITECTURE INFERENCER ===")
    
    # 1. Get Data
    data = mock_run_athena_query("cross_az_traffic")
    
    # 2. Build Prompt
    # We serialize the data to JSON to let the LLM analyze it structurally
    context_data = json.dumps(data, indent=2)
    
    prompt = f"""
    You are a FinOps Architect Assistant. 
    Analyze the following AWS Cost & Usage Report (CUR) data snippet regarding Data Transfer.
    
    Data:
    {context_data}
    
    Task:
    1. Identify the cost driver.
    2. Infer the likely architecture causing this (e.g., Cross-AZ chatter, Public Internet via NAT).
    3. Suggest a remediation.
    """
    
    # 3. Get Insight
    insight = mock_llm_call(prompt)
    print(f"[<] Agent Response:\n{insight}")

# ==============================================================================
# AGENT LOGIC: TAGGING SHERLOCK HOLMES
# ==============================================================================
def run_tagging_agent():
    print("\n=== RUNNING AGENT: TAGGING SHERLOCK HOLMES ===")
    
    # 1. Get Data
    data = mock_run_athena_query("tagging_correlation")
    
    # 2. Build Prompt
    context_data = json.dumps(data, indent=2)
    
    prompt = f"""
    You are a Forensic FinOps Agent.
    I have an untagged resource. I looked for other resources that started billing 
    at the exact same timestamp (neighbors).
    
    Data:
    {context_data}
    
    Task:
    1. Look for consistency in the tags of the 'neighbors'.
    2. Determine the probability that the untagged resource belongs to the same project.
    3. Recommend a tag if confidence is high.
    """
    
    # 3. Get Insight
    insight = mock_llm_call(prompt)
    print(f"[<] Agent Response:\n{insight}")

if __name__ == "__main__":
    run_architecture_agent()
    run_tagging_agent()
