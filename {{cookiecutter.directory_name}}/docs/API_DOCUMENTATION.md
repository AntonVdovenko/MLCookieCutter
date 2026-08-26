# API Documentation - {{ cookiecutter.project_name }}

This document is mandatory for production services. It should be the only
document external developers or teams need in order to integrate with this
service.

If this repository is experiment-only and exposes no public API, state that
clearly here and point readers to `README.md`,
`docs/SETUP_AND_TESTING_GUIDE.md`, and the experiment docs.

## Integration Status

- Service type: library | batch job | internal service | external service
- Public API: yes | no
- Owner:
- Support channel:

## Base URLs

| Environment | Base URL | Notes |
|---|---|---|
| Local | `http://localhost:<port>/` | Local development |
| Dev |  |  |
| Stage |  |  |
| Prod |  |  |

## Authentication and Authorization

- Authentication mechanism:
- Required headers:
- Required roles or scopes:
- Unauthenticated endpoints:

## Route Index

| Method | Path | Summary | Auth | Stability |
|---|---|---|---|---|
| `GET` | `/health` | Health check | No | Stable |

## Request and Response Contracts

Document each externally callable route with:

- method and path;
- content type;
- path/query/header/body fields;
- required vs optional fields;
- response schema;
- error schema;
- idempotency and retry behavior;
- timeout expectations;
- example request and response.

## Error Handling

| Status | Meaning | Caller action |
|---|---|---|
| `400` | Invalid request | Fix request fields and retry |
| `401` | Missing authentication | Send credentials |
| `403` | Unauthorized | Check caller permissions |
| `404` | Resource not found | Check identifiers |
| `409` | Conflict | Refresh state or retry safely |
| `429` | Rate limited | Back off and retry |
| `500` | Server error | Escalate with trace/log context |

## Versioning and Compatibility

- API versioning scheme:
- Backward compatibility policy:
- Deprecation process:
- Known breaking changes:

## Integration Checklist

- Required environment variables and secrets are documented.
- Caller-owned identifiers are clearly named.
- Response fields used by external teams are stable or versioned.
- Smoke-test commands are linked from `docs/SETUP_AND_TESTING_GUIDE.md`.
- Contract changes are reflected in `docs/ENGINEERING_LOGS.md`.
