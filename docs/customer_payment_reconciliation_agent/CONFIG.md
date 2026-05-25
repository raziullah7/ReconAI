# CONFIG.md

**Feature**: customer_payment_reconciliation_agent  
**Stage**: spec  
**Last updated**: intentionally omitted  
**Owner**: config-designer subagent pattern

See [PRD.md](PRD.md) for product constraints, [ARCH.md](ARCH.md) for architecture context, and [SPEC.md](SPEC.md) for implementation decisions.

## Override Precedence

Runtime configuration resolves in this order: environment variable, tenant override when allowed, tenant tier policy when implemented, then application default. Tenant overrides are disabled for secrets and core security settings.

## Feature Flags

### RECONAI_PROCESSING_ENABLED
**Type**: feature-flag  
**Purpose**: Enables or disables asynchronous processing for transcription, extraction, matching, and reconciliation.

**Default**: enabled in development and staging; enabled in production after health checks.  
**Validation**: boolean.  
**Runtime**: hot-reload.  
**Rollout strategy**: allowlist or all-tenants.  
**Kill switch**: yes, disables new processing jobs while preserving reads.  
**Tenant override**: allowed.  
**Flag dependencies**: requires queue, database, transcription, and LLM settings.  
**Observability**: emit `reconai.flag.processing_enabled`.  
**Deprecation plan**: remove only after processing is permanently core.

### RECONAI_NOTIFICATIONS_ENABLED
**Type**: feature-flag  
**Purpose**: Controls optional mismatch and payment-not-found notifications.

**Default**: disabled.  
**Validation**: boolean.  
**Runtime**: hot-reload.  
**Rollout strategy**: tenant allowlist if notifications enter scope.  
**Kill switch**: yes.  
**Tenant override**: allowed.  
**Flag dependencies**: notification provider settings when implemented.  
**Observability**: emit `reconai.flag.notifications_enabled`.  
**Deprecation plan**: keep while notifications are optional.

### RECONAI_EXPORTS_ENABLED
**Type**: feature-flag  
**Purpose**: Controls CSV/Excel export availability.

**Default**: enabled.  
**Validation**: boolean.  
**Runtime**: hot-reload.  
**Rollout strategy**: all-tenants.  
**Kill switch**: yes, hides export actions and rejects export API requests.  
**Tenant override**: allowed.  
**Flag dependencies**: none.  
**Observability**: emit `reconai.flag.exports_enabled`.  
**Deprecation plan**: remove if exports become mandatory.

## Environment Variables

### DATABASE_URL
**Type**: env-var  
**Purpose**: PostgreSQL connection string.

**Default**: development compose database; staging/production from secret store.  
**Validation**: must be a PostgreSQL URL.  
**Runtime**: restart-required.  
**Tenant override**: not allowed.  
**Secret rotation**: rotate via secret store and restart services.

### REDIS_URL
**Type**: env-var  
**Purpose**: Redis broker and result backend URL.

**Default**: development compose Redis; staging/production from environment.  
**Validation**: must be a Redis URL.  
**Runtime**: restart-required.  
**Tenant override**: not allowed.  
**Secret rotation**: rotate credentials if Redis requires auth.

### OLLAMA_BASE_URL
**Type**: env-var  
**Purpose**: Base URL for local Ollama runtime.

**Default**: local compose service URL.  
**Validation**: valid HTTP URL reachable by workers.  
**Runtime**: restart-required for workers.  
**Tenant override**: not allowed.  
**Secret rotation**: not a secret.

### RECONAI_LLM_MODEL
**Type**: env-var  
**Purpose**: Local LLM model used for agreement extraction.

**Default**: primary small local model selected during deployment.  
**Validation**: non-empty model name installed in Ollama.  
**Runtime**: restart-required for workers unless model reload is implemented.  
**Tenant override**: not allowed for first delivery.  
**Secret rotation**: not a secret.

### TRANSCRIPTION_BACKEND
**Type**: env-var  
**Purpose**: Selects faster-whisper or whisper.cpp adapter.

**Default**: faster-whisper.  
**Validation**: one of `faster_whisper` or `whisper_cpp`.  
**Runtime**: restart-required for workers.  
**Tenant override**: not allowed.  
**Secret rotation**: not a secret.

### STORAGE_ROOT
**Type**: env-var  
**Purpose**: Local storage root or object-storage prefix for call recordings and exports.

**Default**: local compose volume.  
**Validation**: writable path or configured object-storage URI.  
**Runtime**: restart-required.  
**Tenant override**: not allowed.  
**Secret rotation**: not a secret unless object storage credentials are embedded, which is prohibited.

### EXTRACTION_REVIEW_CONFIDENCE_THRESHOLD
**Type**: runtime-option  
**Purpose**: Confidence below this threshold routes extraction to human review.

**Default**: deployment policy value; exact numeric value must be confirmed before implementation.  
**Validation**: decimal between 0 and 1.  
**Runtime**: hot-reload.  
**Tenant override**: allowed if operations approves.  
**Secret rotation**: not a secret.

### WORKER_CONCURRENCY
**Type**: env-var  
**Purpose**: Celery worker concurrency for local resource control.

**Default**: 1 for transcription/extraction workers.  
**Validation**: positive integer; local AI workers should remain conservative.  
**Runtime**: restart-required.  
**Tenant override**: not allowed.  
**Secret rotation**: not a secret.

## Open Questions

- OQ-CONFIG-01: Confirm `EXTRACTION_REVIEW_CONFIDENCE_THRESHOLD` before implementation.
- OQ-CONFIG-02: Confirm exact LLM model name installed on the target server.
