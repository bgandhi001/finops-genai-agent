-- ====================================================================================
-- PROJECT IDEA 5: TAGGING "SHERLOCK HOLMES" (CUR VERSION)
-- Purpose: Find correlations between untagged resources and tagged resources/events.
-- The GenAI Agent uses these time-series correlations to "guess" ownership.
-- ====================================================================================

-- ------------------------------------------------------------------------------------
-- 1. THE "TIME TRAVEL" CORRELATION
-- Context: Resources created (or starting usage) at the EXACT same hour often belong 
-- to the same deployment (Terraform apply, CloudFormation stack).
-- GenAI Prompt: "I have found Untagged Resource X. It started billing at 2023-10-27 10:00.
-- At that same hour, Resources Y and Z (tagged 'Project:Alpha') also started. 
-- Probability check: Does X belong to Project:Alpha?"
-- ------------------------------------------------------------------------------------

WITH ResourceStartTimes AS (
    SELECT 
        line_item_resource_id,
        MIN(line_item_usage_start_date) as first_seen_time,
        MAX(resource_tags_user_project) as project_tag, -- Adjust 'project' to your key
        MAX(resource_tags_user_cost_center) as cost_center_tag,
        SUM(line_item_unblended_cost) as total_spend
    FROM 
        "cost_and_usage_report"
    WHERE 
        line_item_usage_start_date >= DATE_ADD('day', -90, CURRENT_DATE)
    GROUP BY 
        line_item_resource_id
),
TaggedResources AS (
    SELECT * FROM ResourceStartTimes 
    WHERE project_tag IS NOT NULL AND project_tag != ''
),
UntaggedResources AS (
    SELECT * FROM ResourceStartTimes 
    WHERE (project_tag IS NULL OR project_tag = '')
    AND total_spend > 10.0 -- Filter noise, focus on things that matter
)
SELECT 
    u.line_item_resource_id AS untagged_resource,
    u.first_seen_time,
    u.total_spend AS untagged_spend,
    t.line_item_resource_id AS tagged_neighbor,
    t.project_tag AS neighbor_project,
    t.cost_center_tag AS neighbor_cost_center
FROM 
    UntaggedResources u
JOIN 
    TaggedResources t
ON 
    u.first_seen_time = t.first_seen_time
-- Optional: Tighten by account or region to reduce false positives
-- AND u.line_item_usage_account_id = t.line_item_usage_account_id 
ORDER BY 
    u.total_spend DESC, 
    u.first_seen_time;

-- ------------------------------------------------------------------------------------
-- 2. THE "SERVICE CLUSTER" INFERENCE
-- Context: If an account uses ONLY "Team Data Science" tags for SageMaker, and we find 
-- an untagged SageMaker instance, it's highly probable it belongs to them.
-- GenAI Prompt: "Analyze the tag distribution for this Service (e.g. SageMaker) in this Account.
-- If 90% of tagged resources belong to Team A, assign that probability to the untagged one."
-- ------------------------------------------------------------------------------------

SELECT 
    line_item_usage_account_id,
    line_item_product_code,
    resource_tags_user_project, -- The tag we are trying to predict
    COUNT(DISTINCT line_item_resource_id) as resource_count,
    SUM(line_item_unblended_cost) as total_cost
FROM 
    "cost_and_usage_report"
WHERE 
    line_item_usage_start_date >= DATE_ADD('day', -30, CURRENT_DATE)
GROUP BY 
    line_item_usage_account_id,
    line_item_product_code,
    resource_tags_user_project
ORDER BY 
    line_item_product_code, 
    resource_count DESC;

-- ------------------------------------------------------------------------------------
-- 3. THE "ORPHAN" DETECTOR
-- Context: Resources that exist but have 0 network traffic or low CPU (if metrics available)
-- or are unattached (EBS). CUR has specific usage types for 'Unused'.
-- GenAI Prompt: "These resources are untagged AND look unused. Prioritize investigating these."
-- ------------------------------------------------------------------------------------

SELECT 
    line_item_resource_id,
    line_item_usage_type,
    SUM(line_item_unblended_cost) as wasted_cost
FROM 
    "cost_and_usage_report"
WHERE 
    -- Common patterns for unattached volumes often show up as pure storage cost 
    -- without IOPS usage (depending on volume type), or explicit "Unused" line items 
    -- in some enterprise CUR configurations.
    -- Here we look for generic "No Tag" high spenders to investigate manually.
    (resource_tags_user_project IS NULL OR resource_tags_user_project = '')
    AND line_item_usage_start_date >= DATE_ADD('day', -30, CURRENT_DATE)
GROUP BY 
    line_item_resource_id,
    line_item_usage_type
ORDER BY 
    wasted_cost DESC
LIMIT 50;
