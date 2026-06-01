# System Architecture

<!-- threat-model-system fixture — Intentionally incomplete — do not use as reference -->

## Overview

The application consists of a Node.js API, a React frontend, and a PostgreSQL
database, all deployed on AWS ECS behind an Application Load Balancer.

## Components

- **Frontend** — React SPA served from S3/CloudFront
- **API** — Express.js on ECS Fargate, port 3000
- **Database** — RDS PostgreSQL
- **Cache** — ElastiCache Redis
- **Storage** — S3 for file uploads
- **Auth** — JWT-based, secrets stored in environment variables

## Data Flows

1. Browser → CloudFront → ALB → ECS API → RDS
2. ECS API → S3 (file uploads, unencrypted)
3. ECS API → Redis (session cache, no auth)
4. ECS API → external payment processor (no mutual TLS)

## Trust Boundaries

Trust boundaries have not been formally defined. The following is approximate:

- Internet traffic enters at CloudFront
- Internal VPC traffic is not further segmented
- Database is accessible from all ECS tasks (no per-service credentials)

## Security Assumptions

- No abuse cases or threat scenarios have been documented
- No data classification exists for user PII or financial records
- Authorization model is role-based but no privilege separation between tenants
- Session tokens stored in localStorage (XSS risk not assessed)
- No rate limiting on authentication endpoints
- No documented incident response or detection plan
- Logging does not feed into a SIEM
- No security review has been conducted on third-party integrations

## Known Gaps

- ASVS compliance mapping: not started
- Penetration test: not scheduled
- Dependency vulnerability scan: manual, infrequent
- Secrets rotation: not automated
