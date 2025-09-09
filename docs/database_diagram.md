# Database Schema Overview

## Introduction

This database schema is designed to support a platform managing users, organizations, agents, and operational data such as metrics, logs, and incidents. It provides a robust structure for handling user authentication, organizational hierarchies, agent operations, and system monitoring, ensuring data integrity and scalability through well-defined relationships.

## Schema Description

The schema comprises multiple tables representing key entities and their interconnections:

- **Users and Preferences**: The `users` table stores user data (ID, clerk ID, timestamps), while `user_preferences` manages individual settings like theme and timezone, linked via `user_id`.
- **Organizations**: The `organizations` table captures organization details (name, description, website). Related tables include `organization_members` (tracks membership with roles and join/leave dates), `organization_invites` (manages invitations), and `organization_credentials` (stores secure credentials).
- **Roles and Permissions**: The `roles` table defines organizational roles, with `role_permissions` specifying allowed actions. Both link to `organizations` via `organization_id`.
- **Agents**: The `agents` table stores agent metadata, with `agent_configs` for configuration details and `organization_agents` linking agents to organizations with roles.
- **Operational Data**: Tables like `metrics`, `logs`, `incidents`, and their aggregations (`metric_aggregations_1m`, `metric_aggregations_1h`, `log_aggregations_1m`, `incident_aggregations_1h`) track system performance, errors, and incidents, all tied to `organizations`.
- **Incident Management**: The `incidents` table records incident details, linked to `agents` (via `assigned_agent_id`) and supported by `agent_memories` and `agent_execution_logs` for agent-driven resolution tracking.
- **Additional Entities**: Tables like `traces`, `events`, `mcp_servers`, `seed`, and `incident_patterns` provide further operational insights and system management capabilities, with most linked to `organizations`.

## Relationships

Foreign key relationships ensure data consistency:
- One-to-many relationships (e.g., `organizations` to `organization_members`, `roles`, `incidents`) are established via `organization_id`.
- One-to-one relationships (e.g., `user_preferences` to `users` via `user_id`, `agent_configs` to `agents` via `agent_id`) provide direct associations.
- Junction tables like `organization_members` and `organization_agents` manage many-to-many relationships between users, organizations, agents, and roles.

This schema supports a scalable, secure, and efficient system for user management, organizational operations, and automated incident handling, with comprehensive monitoring capabilities.

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
