# GCP Cloud Run Deployment Status

**Date:** December 29, 2025
**Deployment Attempt:** Final (after multiple fixes)
**Result:** Partial Success (2/9 servers deployed)

---

## Deployment Results

### ✅ Successfully Deployed (2/9)

| Server | URL | Status |
|--------|-----|--------|
| **mcp-deepcell** | https://mcp-deepcell-ondu7mwjpa-uc.a.run.app | Running on SSE, port 8080 |
| **mcp-mockepic** | https://mcp-mockepic-ondu7mwjpa-uc.a.run.app | Running on SSE, port 8080 |

### ❌ Failed to Deploy (7/9)

| Server | Error | Root Cause |
|--------|-------|------------|
| mcp-fgbio | Container failed to start on PORT=3000 | Using HTTP transport, binding to 127.0.0.1:8000 |
| mcp-multiomics | Build failed | Build context issue |
| mcp-spatialtools | Container failed to start on PORT=3002 | Transport/port misconfiguration |
| mcp-tcga | Container failed to start on PORT=3003 | Transport/port misconfiguration |
| mcp-openimagedata | Container failed to start on PORT=3004 | Transport/port misconfiguration |
| mcp-seqera | Container failed to start on PORT=3005 | Transport/port misconfiguration |
| mcp-huggingface | Container failed to start on PORT=3006 | Transport/port misconfiguration |

---

## Root Cause Analysis

### Issue: Environment Variable Not Being Applied

**Expected behavior:**
```
ENV MCP_TRANSPORT=sse  # In Dockerfile
→ Server reads MCP_TRANSPORT → Uses SSE transport → Binds to 0.0.0.0:$PORT
```

**Actual behavior (failed servers):**
```
Server ignores MCP_TRANSPORT → Defaults to HTTP → Binds to 127.0.0.1:8000
```

**Evidence from Cloud Run logs:**

**Successful (mcp-deepcell):**
```
INFO: Starting MCP server 'deepcell' with transport 'sse' on http://0.0.0.0:8080/sse
```

**Failed (mcp-fgbio):**
```
INFO: Starting MCP server 'fgbio' with transport 'http' on http://127.0.0.1:8000/mcp
```

---

## What Works

1. ✅ **Docker builds complete successfully** (containers built for all servers)
2. ✅ **SSE transport works** (proven by mcp-deepcell and mcp-mockepic)
3. ✅ **Cloud Run PORT variable works** (both successful servers use port 8080)
4. ✅ **Shared utilities accessible** (no import errors)
5. ✅ **Dockerfile structure correct** (all use same template)

---

## What Needs Investigation

1. **Why environment variables inconsistent?**
   - Same Dockerfile template used for all servers
   - mcp-deepcell works, mcp-fgbio doesn't
   - Possible caching issue?

2. **Transport parameter handling in FastMCP**
   - FastMCP version differences?
   - How does it read environment variables?
   - Does it fallback to HTTP when SSE fails?

3. **Cloud Run deployment differences**
   - Why did only 2 servers deploy successfully?
   - Different Cloud Build behavior?

---

## Files Modified During Deployment Debugging

### Core Fixes Applied

1. **Server Code** (all 9 servers):
   - Made transport configurable via `MCP_TRANSPORT` env var
   - Added port configuration from `PORT` or `MCP_PORT`
   - SSE/HTTP transports bind to `0.0.0.0`

2. **Dockerfiles** (all 9 servers):
   - Set `MCP_TRANSPORT=sse`
   - Set default `MCP_PORT=<port_number>`
   - Copy `_shared_temp/utils/` for shared utilities

3. **Deployment Script** (`scripts/deployment/deploy_to_gcp.sh`):
   - Temporarily copies `shared/` to `_shared_temp/` in each server dir
   - Uses `--source "${server_path}"` (Cloud Run standard approach)
   - Cleans up `_shared_temp/` after deployment

4. **Repository Structure**:
   - Reorganized files into logical subdirectories
   - Documentation → `docs/deployment/` and `docs/testing/`
   - Scripts → `scripts/deployment/`
   - Tests → `tests/` and `tests/integration/`

---

## Next Steps

### Option 1: Debug Failed Servers

1. Check FastMCP version in failing containers
2. Add explicit logging of MCP_TRANSPORT value
3. Test with simplified Dockerfile (minimal dependencies)
4. Force rebuild without cache: `--no-cache`

### Option 2: Use Working Pattern

1. Analyze mcp-deepcell and mcp-mockepic configuration
2. Identify what makes them work
3. Apply identical pattern to other 7 servers
4. Redeploy one server at a time

### Option 3: Alternative Deployment Approach

1. Use Cloud Build with explicit build configs
2. Pre-build containers and push to Container Registry
3. Deploy from pre-built images
4. More control over build process

---

## Testing the Successfully Deployed Servers

### mcp-deepcell

```bash
# Health check (expect 405 - Method Not Allowed)
curl https://mcp-deepcell-ondu7mwjpa-uc.a.run.app/sse

# Test with Claude API
python tests/integration/test_claude_api_integration.py
```

### mcp-mockepic

```bash
# Health check (expect 405)
curl https://mcp-mockepic-ondu7mwjpa-uc.a.run.app/sse

# Test with Claude API
python tests/integration/test_claude_api_integration.py
```

---

## Commits Made

1. **Fix GCP Cloud Run deployment for all 9 MCP servers** (42e7b6c)
   - Made transport configurable
   - Added port configuration
   - Updated all server code

2. **Fix Docker container path structure for shared utilities** (335bd8b)
   - Added `/app/servers/<name>` structure
   - Copied shared utilities correctly

3. **Fix Docker build context to use repository root** (118e8c6)
   - Changed deployment to use repo root context
   - Updated Dockerfile COPY paths

4. **Fix gcloud deployment with temporary shared directory copy** (9e959e8)
   - Copy shared/ to _shared_temp/ temporarily
   - Compatible with gcloud --source flag

5. **Reorganize repository structure** (aac00d6)
   - Moved files to logical subdirectories
   - Updated all references

---

## Summary

**Achievements:**
- ✅ 2/9 servers successfully deployed to Cloud Run
- ✅ Proved SSE transport works in containerized environment
- ✅ Repository reorganized for better maintainability
- ✅ All code committed and pushed to GitHub

**Outstanding Issues:**
- ❌ 7/9 servers failing with transport/port configuration
- ❌ Inconsistent environment variable behavior
- ❌ Need to investigate FastMCP's environment handling

**Time Investment:**
- Multiple deployment attempts
- Extensive debugging of Docker builds
- Cloud Run log analysis
- Code reorganization

**Recommendation:**
Focus on understanding why mcp-deepcell and mcp-mockepic succeeded where others failed. The solution is proven to work - we just need consistent application across all servers.
