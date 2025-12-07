-- ====================================================================================
-- PROJECT IDEA 4: ARCHITECTURE INFERENCE AGENT (CUR VERSION)
-- Purpose: Extract usage patterns that imply specific architectural inefficiencies.
-- The GenAI Agent uses these results to "reconstruct" the architecture and suggest fixes.
-- ====================================================================================

-- ------------------------------------------------------------------------------------
-- 1. THE "CHATTY MICROSERVICE" DETECTOR (Cross-AZ Data Transfer)
-- Context: High regional data transfer often implies services in different AZs 
-- communicating heavily without using local routing.
-- GenAI Prompt: "Analyze the top pairs of AZs exchanging data. Suggest simple 
-- architectural changes like 'Keep traffic local' or 'Use Local Zones'."
-- ------------------------------------------------------------------------------------
SELECT 
    line_item_product_code,
    line_item_usage_type,
    resource_tags_user_name, -- Assuming you have a Name tag, adjust if needed
    line_item_availability_zone,
    SUM(line_item_usage_amount) AS total_gb,
    SUM(line_item_unblended_cost) AS total_cost
FROM 
    "cost_and_usage_report" -- REPLACE with your actual table name
WHERE 
    line_item_usage_type LIKE '%Regional-Bytes%'
    AND line_item_usage_start_date >= DATE_ADD('day', -30, CURRENT_DATE)
GROUP BY 
    line_item_product_code,
    line_item_usage_type,
    resource_tags_user_name,
    line_item_availability_zone
ORDER BY 
    total_cost DESC
LIMIT 20;

-- ------------------------------------------------------------------------------------
-- 2. THE "MISSING VPC ENDPOINT" DETECTOR (NAT Gateway Traffic Analysis)
-- Context: High NAT Gateway processing cost often comes from accessing AWS services 
-- (S3, DynamoDB) via the public internet instead of internal Gateway Endpoints.
-- GenAI Prompt: "Look at the volume of NAT Gateway traffic. If high, check if S3/DynamoDB
-- usage is also high in the same region. Suggest implementing VPC Endpoints."
-- ------------------------------------------------------------------------------------
WITH NatTraffic AS (
    SELECT 
        line_item_usage_account_id,
        line_item_availability_zone,
        SUM(line_item_usage_amount) AS nat_gb_processed,
        SUM(line_item_unblended_cost) AS nat_cost
    FROM "cost_and_usage_report"
    WHERE line_item_usage_type LIKE '%NatGateway-Bytes%'
    AND line_item_usage_start_date >= DATE_ADD('day', -30, CURRENT_DATE)
    GROUP BY line_item_usage_account_id, line_item_availability_zone
),
S3Traffic AS (
    SELECT 
        line_item_usage_account_id,
        line_item_availability_zone,
        SUM(line_item_usage_amount) AS s3_requests_or_bytes, -- Simplified metric
        SUM(line_item_unblended_cost) AS s3_cost
    FROM "cost_and_usage_report"
    WHERE line_item_product_code = 'AmazonS3'
    AND line_item_usage_start_date >= DATE_ADD('day', -30, CURRENT_DATE)
    GROUP BY line_item_usage_account_id, line_item_availability_zone
)
SELECT 
    n.line_item_usage_account_id,
    n.line_item_availability_zone,
    n.nat_gb_processed,
    n.nat_cost,
    s.s3_cost
FROM NatTraffic n
JOIN S3Traffic s ON n.line_item_usage_account_id = s.line_item_usage_account_id
-- Note: AZ join might be fuzzy if S3 usage isn't always AZ-specific in CUR, 
-- but account-level correlation is usually enough for the Agent to make a hypothesis.
ORDER BY n.nat_cost DESC;

-- ------------------------------------------------------------------------------------
-- 3. THE "LEGACY TECH" FINDER (GP2 vs GP3 Volume Usage)
-- Context: gp3 is cheaper and faster than gp2. Finding gp2 usage is an easy win.
-- GenAI Prompt: "Calculate potential savings by moving all these gp2 volumes to gp3.
-- Draft a Jira ticket description for the engineering team."
-- ------------------------------------------------------------------------------------
SELECT 
    line_item_resource_id,
    resource_tags_user_name,
    pricing_unit,
    SUM(line_item_usage_amount) AS total_storage_gb_months,
    SUM(line_item_unblended_cost) AS total_cost
FROM 
    "cost_and_usage_report"
WHERE 
    line_item_product_code = 'AmazonEC2'
    AND line_item_usage_type LIKE '%EBS:VolumeUsage.gp2%'
    AND line_item_usage_start_date >= DATE_ADD('day', -30, CURRENT_DATE)
GROUP BY 
    line_item_resource_id,
    resource_tags_user_name,
    pricing_unit
ORDER BY 
    total_cost DESC;
