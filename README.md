<h1 align=center>Hydra AI</h1>
<image src="https://mlgktt2y6f.ufs.sh/f/6YinM32zuOKM4ZAHjpG5qeAa6DOTBnZPC9NH78RvV3ho1UiM" alt="Hydra AI Design Preview"/>

<p>
  Hydra AI is a revolutionary autonomous DevOps platform that combines advanced AI reasoning with real-time telemetry analysis to detect, diagnose, and resolve infrastructure incidents before they impact your users. Built on TiDB's cutting-edge HTAP architecture, it processes massive telemetry streams while maintaining institutional memory of every incident.
</p>

### The Problem

- Mean Time to Recovery (MTTR): 2-8 hours typical
- Downtime Cost: $5.6M per hour on average
- Context Switching: Engineers juggle 15+ tools during incidents
- Knowledge Loss: Solutions forgotten after engineer turnover
- Alert Fatigue: 90% of alerts are noise or false positives

### The Solution

Hydra AI transforms your infrastructure into a self-aware, self-healing system that learns from every incident and gets smarter over time.

### Key Features

**Autonomous AI Agents**

- Context Gathering Agent: Correlates metrics, logs, and traces in real-time
- Pattern Recognition Agent: Finds similar historical incidents using vector search
- Root Cause Analysis Agent: Performs intelligent causal reasoning
- Solution Planning Agent: Generates and validates resolution strategies
- Execution Agent: Safely implements fixes with rollback capabilities

**Institutional Memory**

- Vector-based Incident Search: Semantic matching of error patterns
- Learning System: Every resolution improves future performance
- Knowledge Graphs: Maps service dependencies and failure patterns
- Confidence Scoring: AI rates its own solution certainty

**Real-time Intelligence**

- Sub-second Anomaly Detection: Process 100K+ events per second
- Hybrid Queries: Combine time-series, vector, and full-text search
- Predictive Analytics: Forecast incidents before they happen
- Multi-dimensional Correlation: Connect seemingly unrelated signals

**Safe Automation**

- Gradual Rollouts: Canary deployments for high-risk changes
- Confidence Thresholds: Human approval for uncertain scenarios
- Automatic Rollback: Instant reversion if fixes fail
- Safety Circuits: Multiple layers of protection

## Database Schema
```mermaid
classDiagram
    direction LR

    class users {
        -id : VARCHAR
        -clerk_id : VARCHAR
        -created_at : DATETIME
        -updated_at : DATETIME
        -deleted_at : DATETIME
    }

    class user_preferences {
        -id : VARCHAR
        -user_id : VARCHAR
        -theme : VARCHAR
        -timezone : VARCHAR
        -language : VARCHAR
        -show_notification : BOOLEAN
    }

    class organizations {
        -id : VARCHAR(255)
        -name : VARCHAR(255)
        -description : VARCHAR(255)
        -avatar_url : VARCHAR(255)
        -website : VARCHAR(255)
        -created_at : DATETIME
        -updated_at : DATETIME
        -deleted_at : DATETIME
    }

    class organization_members {
        -id : VARCHAR
        -organization_id : VARCHAR
        -user_id : VARCHAR
        -role_id : VARCHAR
        -joined_at : DATETIME
        -left_at : DATETIME
        -granted_by : VARCHAR
        -role_expires_at : DATETIME
    }

    class organization_invites {
        -id : VARCHAR
        -organization_id : VARCHAR
        -sender_id : VARCHAR
        -recipient_email : VARCHAR
        -role_id : VARCHAR
        -status : VARCHAR(8)
        -message : VARCHAR
        -created_at : DATETIME
        -updated_at : DATETIME
        -expires_at : DATETIME
    }

    class organization_credentials {
        -created_at : DATETIME
        -updated_at : DATETIME
        -id : VARCHAR
        -organization_id : VARCHAR
        -secret_hash : VARCHAR
        -is_active : BOOLEAN
        -expires_at : DATETIME
    }

    class agents {
        -id : VARCHAR
        -name : VARCHAR
        -description : VARCHAR
        -avatar_url : VARCHAR
        -agent_status : VARCHAR(11)
        -is_system : BOOLEAN
        -created_at : DATETIME
        -updated_at : DATETIME
        -deleted_at : DATETIME
    }

    class agent_configs {
        -id : VARCHAR
        -agent_id : VARCHAR
        -model : VARCHAR
        -version : VARCHAR
        -system_prompt : VARCHAR
        -created_at : DATETIME
        -updated_at : DATETIME
    }

    class organization_agents {
        -id : VARCHAR
        -organization_id : VARCHAR
        -agent_id : VARCHAR
        -role_id : VARCHAR
        -status : VARCHAR(8)
        -added_at : DATETIME
        -removed_at : DATETIME
        -role_expires_at : DATETIME
    }

    class roles {
        -id : VARCHAR
        -organization_id : VARCHAR
        -name : VARCHAR
        -description : VARCHAR
        -is_default : BOOLEAN
        -is_system : BOOLEAN
        -level : INTEGER
    }

    class role_permissions {
        -id : VARCHAR
        -role_id : VARCHAR
        -action : VARCHAR(15)
        -created_at : DATETIME
    }

    class sessions {
        -created_at : DATETIME
        -updated_at : DATETIME
        -id : VARCHAR
        -token_jti : VARCHAR(255)
        -organization_id : VARCHAR
        -status : VARCHAR(7)
        -expires_at : DATETIME
        -last_used_at : DATETIME
        -ip_address : VARCHAR(45)
    }

    class revoked_tokens {
        -token_jti : VARCHAR(255)
        -organization_id : VARCHAR
        -revoked_at : DATETIME
        -expires_at : DATETIME
    }

    class metrics {
        -id : VARCHAR
        -metric_id : VARCHAR
        -timestamp : DATETIME
        -service_name : VARCHAR(128)
        -metric_name : VARCHAR(64)
        -value : FLOAT
        -labels : JSON
        -unit : VARCHAR(32)
        -anomaly_score : FLOAT
        -organization_id : VARCHAR
    }

    class logs {
        -id : VARCHAR
        -log_id : VARCHAR
        -timestamp : DATETIME
        -service_name : VARCHAR(128)
        -level : VARCHAR(5)
        -message : TEXT
        -trace_id : VARCHAR(64)
        -span_id : VARCHAR(64)
        -structured_data : JSON
        -embedding : VARCHAR(8192)
        -organization_id : VARCHAR
    }

    class incidents {
        -id : VARCHAR
        -incident_id : VARCHAR
        -timestamp : DATETIME
        -service_name : VARCHAR(128)
        -severity : VARCHAR(8)
        -status : VARCHAR(9)
        -title : VARCHAR(512)
        -description : TEXT
        -error_signature : VARCHAR(256)
        -embedding : VARCHAR(8192)
        -context_data : JSON
        -resolution_data : JSON
        -root_cause : TEXT
        -resolution_time_seconds : INTEGER
        -confidence_score : FLOAT
        -auto_resolved : BOOLEAN
        -organization_id : VARCHAR
        -assigned_agent_id : VARCHAR
    }

    class agent_memories {
        -created_at : DATETIME
        -updated_at : DATETIME
        -id : VARCHAR
        -incident_id : VARCHAR
        -agent_id : VARCHAR
        -memory_type : VARCHAR(17)
        -content : JSON
        -embedding : VARCHAR(8192)
        -confidence : FLOAT
        -usage_count : INTEGER
        -success_rate : FLOAT
        -organization_id : VARCHAR
    }

    class traces {
        -id : VARCHAR
        -trace_id : VARCHAR(64)
        -span_id : VARCHAR(64)
        -parent_span_id : VARCHAR(64)
        -operation_name : VARCHAR(255)
        -start_time : INTEGER
        -end_time : INTEGER
        -duration_ms : FLOAT
        -status : VARCHAR(32)
        -attributes : JSON
        -events : JSON
        -service_name : VARCHAR(128)
        -organization_id : VARCHAR
    }

    class events {
        -id : VARCHAR
        -timestamp : DATETIME
        -event_type : VARCHAR(64)
        -source : VARCHAR(128)
        -severity : VARCHAR(8)
        -title : VARCHAR(512)
        -description : TEXT
        -event_metadata : JSON
        -organization_id : VARCHAR
    }

    class agent_execution_logs {
        -id : VARCHAR
        -incident_id : VARCHAR
        -agent_id : VARCHAR
        -execution_stage : VARCHAR(12)
        -action_type : VARCHAR(64)
        -input_data : JSON
        -output_data : JSON
        -execution_time_ms : INTEGER
        -confidence_score : FLOAT
        -success : BOOLEAN
        -error_message : TEXT
        -timestamp : DATETIME
        -organization_id : VARCHAR
    }

    class metric_aggregations_1m {
        -timestamp : DATETIME
        -service_name : VARCHAR(128)
        -metric_name : VARCHAR(64)
        -avg_value : DOUBLE
        -min_value : DOUBLE
        -max_value : DOUBLE
        -count_values : BIGINT
        -sum_values : DOUBLE
        -p50_value : DOUBLE
        -p95_value : DOUBLE
        -p99_value : DOUBLE
        -stddev_value : DOUBLE
        -created_at : DATETIME
        -organization_id : VARCHAR
    }

    class metric_aggregations_1h {
        -timestamp : DATETIME
        -service_name : VARCHAR(128)
        -metric_name : VARCHAR(64)
        -avg_value : DOUBLE
        -min_value : DOUBLE
        -max_value : DOUBLE
        -count_values : BIGINT
        -sum_values : DOUBLE
        -p95_value : DOUBLE
        -p99_value : DOUBLE
        -organization_id : VARCHAR
        -created_at : DATETIME
    }

    class log_aggregations_1m {
        -timestamp : DATETIME
        -service_name : VARCHAR(128)
        -total_logs : BIGINT
        -error_count : BIGINT
        -warn_count : BIGINT
        -info_count : BIGINT
        -debug_count : BIGINT
        -error_rate : DOUBLE
        -unique_traces : BIGINT
        -organization_id : VARCHAR
        -created_at : DATETIME
    }

    class incident_aggregations_1h {
        -timestamp : DATETIME
        -service_name : VARCHAR(128)
        -total_incidents : BIGINT
        -critical_incidents : BIGINT
        -high_incidents : BIGINT
        -medium_incidents : BIGINT
        -low_incidents : BIGINT
        -avg_resolution_time : DOUBLE
        -auto_resolved_count : BIGINT
        -organization_id : VARCHAR
        -created_at : DATETIME
    }

    class mcp_servers {
        -created_at : DATETIME
        -updated_at : DATETIME
        -id : VARCHAR
        -name : VARCHAR
        -description : VARCHAR
        -icon : VARCHAR
        -auth_token : BLOB
        -url : VARCHAR
        -is_active : BOOLEAN
        -organization_id : VARCHAR
    }

    class seed {
        -id : INTEGER
        -name : VARCHAR
    }

    class incident_patterns {
        -id : VARCHAR(255)
        -service_name : VARCHAR(128)
        -time_bucket : DATETIME
        -aggregation_level : ENUM
        -pattern_hash : VARCHAR(64)
        -error_signatures : JSON
        -incident_count : INTEGER
        -incident_frequency : FLOAT
        -avg_resolution_time : FLOAT
        -avg_severity : FLOAT
        -auto_resolution_rate : FLOAT
        -is_recurring : TINYINT
        -trend_direction : VARCHAR(16)
        -seasonality_detected : TINYINT
        -organization_id : VARCHAR(255)
    }

    class metric_aggregations {
        -id : VARCHAR(255)
        -service_name : VARCHAR(128)
        -metric_name : VARCHAR(64)
        -aggregation_level : ENUM
        -time_bucket : DATETIME
        -count : INTEGER
        -min_value : FLOAT
        -max_value : FLOAT
        -avg_value : FLOAT
        -median_value : FLOAT
        -p95_value : FLOAT
        -p99_value : FLOAT
        -stddev_value : FLOAT
        -baseline_avg : FLOAT
        -baseline_stddev : FLOAT
        -deviation_score : FLOAT
        -has_anomaly : TINYINT
        -anomaly_severity : FLOAT
        -anomaly_type : VARCHAR(32)
        -organization_id : VARCHAR(255)
        -created_at : DATETIME
    }

    user_preferences --> users : user_id
    organization_members --> roles : role_id
    organization_members --> users : user_id
    organization_members --> organizations : organization_id
    organization_members --> users : granted_by
    organization_invites --> users : sender_id
    organization_invites --> roles : role_id
    organization_invites --> organizations : organization_id
    organization_credentials --> organizations : organization_id
    agent_configs --> agents : agent_id
    organization_agents --> organizations : organization_id
    organization_agents --> roles : role_id
    organization_agents --> agents : agent_id
    roles --> organizations : organization_id
    role_permissions --> roles : role_id
    sessions --> organizations : organization_id
    revoked_tokens --> organizations : organization_id
    metrics --> organizations : organization_id
    logs --> organizations : organization_id
    incidents --> agents : assigned_agent_id
    incidents --> organizations : organization_id
    agent_memories --> incidents : incident_id
    agent_memories --> organizations : organization_id
    agent_memories --> agents : agent_id
    traces --> organizations : organization_id
    events --> organizations : organization_id
    agent_execution_logs --> organizations : organization_id
    agent_execution_logs --> agents : agent_id
    agent_execution_logs --> incidents : incident_id
    metric_aggregations_1m --> organizations : organization_id
    metric_aggregations_1h --> organizations : organization_id
    log_aggregations_1m --> organizations : organization_id
    incident_aggregations_1h --> organizations : organization_id
    mcp_servers --> organizations : organization_id
    incident_patterns --> organizations : organization_id
    metric_aggregations --> organizations : organization_id
    ```
