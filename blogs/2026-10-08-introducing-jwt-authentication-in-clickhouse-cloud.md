---
title: "Introducing JWT authentication in ClickHouse Cloud"
date: "2026-10-08T13:55:14.508Z"
category: "Product"
excerpt: "Connect to ClickHouse Cloud with short-lived tokens from your identity provider instead of database passwords."
---

# Introducing JWT authentication in ClickHouse Cloud

> TL;DR
> Connect to ClickHouse Cloud with short-lived tokens from your identity provider instead of database passwords.

Long-lived database credentials are difficult to govern. Every person, pipeline, and application needs a password or certificate that must be stored, rotated, and revoked as access changes.

JWT authentication for ClickHouse Cloud Services (26.4 or later) replaces that workflow with short-lived JWT tokens from an existing OpenID Connect provider, including Okta and Microsoft Entra. Identity and roles stay in the provider, while ClickHouse Cloud accepts the token instead of a separate database password. When the token expires, so does the access it provides.

This reduces the number of credentials security and platform teams have to manage and removes the need to provision a persistent database user for every person or workload. It is part of our broader security and governance work in ClickHouse Cloud.

## How it works

When a client presents a JWT token, ClickHouse verifies its signature and required claims against the configured provider. It then creates an ephemeral user and applies the roles and grants in the token within the service’s permission limit.

A token carries the standard JWT claims, along with optional ClickHouse claims for roles and grants:

- `iss`, who issued the token
- `aud`, which service the token is meant for
- `sub`, who the user is
- `iat` and `exp`, when the token was issued and when it expires
- `clickhouse:roles`, an optional list of existing role names to activate

If your identity provider uses a different claim name for roles (eg. `groups`), you can tell ClickHouse which one to read.

```json
{
  "iss": "https://your-tenant.okta.com",
  "sub": "jane.doe",
  "aud": "my-clickhouse-service",
  "exp": 1719504000,
  "iat": 1719500400,
  "clickhouse:roles": ["analyst", "reader"]
}
```

When a valid token arrives, ClickHouse creates an ephemeral user in memory, gives it the access the token asked for, and runs the query. Usernames follow a fixed pattern, where the hash covers the issuer, subject, audience, and the roles claim:

```text
JWT::<subject>::<claims_hash>
```

Two tokens for the same person with different roles produce two different users, so you can tell the sessions apart in `system.users` even though they belong to the same identity. In a multi-replica service, the token travels with forwarded queries and each node verifies it independently.

## No more user provisioning

Ephemeral users change what managing users means on the database side. With password or certificate users, someone runs `CREATE USER` and a set of `GRANT` statements for every new hire, keeps that in sync with the identity provider, and remembers to `DROP USER` when they leave. Most teams end up scripting it, and the scripts drift.

<!-- Editorial note from Notion: Consider linking readers to the security docs and explicitly recommending IdP-issued JWTs over older ephemeral passwords and certificate users. -->

With JWT authentication there is nothing to script. A user appears in memory the first time a valid token is presented, carries the roles from that token, and is removed by a background task after the token's `exp` passes. The user itself is never written to disk. There is no `CREATE USER` step, and `CREATE USER ... IDENTIFIED WITH jwt` raises an exception on purpose, because the token lifecycle is the user lifecycle. `ALTER USER` and `DROP USER` do not apply either, and JWT users are not included in backups, since there is nothing to restore.

What you manage in ClickHouse is the roles. Create `analyst`, `pipeline_writer`, or whatever your team needs once, and let the identity provider decide who gets them by putting role names in the token. Onboarding is a group assignment in your provider. Offboarding is removing it. And `system.users` shows who is active right now rather than everyone who has ever been granted access.

## Bring your own identity provider

If your identity provider speaks OpenID Connect, you already have everything ClickHouse asks for. An OIDC provider publishes its issuer and a `jwks_uri` in its discovery document and signs tokens that already carry `iss`, `aud`, `sub`, `exp`, and `iat`. Those are the values ClickHouse checks. We have verified the setup with Okta and Microsoft Entra, and any provider that follows the standard works the same way. For a custom provider, ClickHouse does not run the login flow itself. Your provider issues the token, your client presents it, and ClickHouse verifies it.

On the Enterprise plan, with a service running 26.4 or later, open your service in the Cloud console and go to Settings → Security → JWT authentication. Each provider needs a name, the issuer and audience values your provider puts in its tokens, and the HTTPS URL where it publishes its JSON Web Key Set (JWKS). If your provider puts group membership in a claim other than `clickhouse:roles`, such as a `groups` claim, set the Roles claim field to that name. The values must match role names that exist on the service. ClickHouse fetches the JWKS URL when you save, so a typo fails at configuration time rather than at someone's first login.

JWKS providers accept RSA keys (`RS256`). From version 26.8, EC keys on the P-256, P-384, and P-521 curves (`ES256`, `ES384`, `ES512`) work as well. The JWKS URL has to be a public HTTPS endpoint.

## Connecting

A client can hold one of two kinds of token, and they are worth keeping apart: a token issued by your own identity provider, or a token issued by ClickHouse Cloud for your Cloud account.

### Tokens from your identity provider

With a custom provider, your identity provider issues the token and the ClickHouse driver presents it. The easiest way to obtain one is with the OAuth client library you already use for your provider. For a service or pipeline that usually means the client credentials flow through your provider's SDK. For a person it means whatever login flow your provider offers. Once you hold the token string, the official clients accept it in place of a username and password.

```typescript
// clickhouse-js
import { createClient } from '@clickhouse/client'

const client = createClient({
  url: 'https://your-instance.clickhouse.cloud:8443',
  access_token: token,
})
```

```python
# clickhouse-connect
import clickhouse_connect

client = clickhouse_connect.get_client(
    host='your-instance.clickhouse.cloud',
    port=443,
    secure=True,
    access_token=token,
)
```

Tokens expire, so most clients also let you plug in your refresh logic. `clickhouse-connect` accepts a `token_provider` callable that it calls for the first token and again whenever the server rejects an expired one. The Go client takes a `GetJWT` callback in its options. The Java client has `useBearerTokenAuth` on the builder and `updateBearerToken` to swap the token on a live client. For ad hoc queries, `clickhouse-client` and plain HTTP work too:

```bash
clickhouse-client --host your-instance.clickhouse.cloud --secure --jwt "$TOKEN"

curl -H "Authorization: Bearer $TOKEN" \
    'https://your-instance.clickhouse.cloud:8443/?query=SELECT+currentUser()'
```

In every client the token replaces the username and password rather than adding to them. Passing both is an error.

### Tokens from ClickHouse Cloud

Every Cloud service also has a built-in authenticator whose tokens ClickHouse Cloud issues for your Cloud account. You never handle these tokens yourself. SQL Console uses them automatically, and `clickhouse-client --login` runs an OAuth2 device code flow against your Cloud login, exchanges the result for a ClickHouse token, refreshes it in the background, and reconnects when a new token arrives.

```bash
clickhouse-client --host your-instance.clickhouse.cloud --login
```

## Quotas and row policies on users that come and go

If a JWT user only exists while its token is valid, what happens to everything ClickHouse normally attaches to a user? Regular users anchor a lot of configuration. A settings profile caps how much memory an analyst's queries may use. A quota limits how many queries a dashboard can run per hour. A row policy makes sure a regional team sees only its own region's rows. All of these are assigned to a user by name, and if the user vanished every few hours you would expect the assignments to vanish with it.

They do not, because a JWT user has two names. The visible username you saw earlier changes whenever the roles in the token change. Underneath it, ClickHouse gives every identity a UUID computed from the issuer, subject, and audience claims. That UUID is the same every time the same person logs in through the same provider, no matter which roles the token carries or how many times the user has expired and been recreated.

Settings profiles, quotas, row policies, and column masking policies attach to that UUID. You assign them with the same statements you use for regular users, referencing the user's current name from `system.users` while they are active:

```sql
ALTER SETTINGS PROFILE readonly_profile ADD TO 'JWT::jane.doe::<claims_hash>';
```

The assignment is recorded on the profile, quota, or policy itself, in the same replicated access storage that holds your roles and other SQL-created objects, backed by Keeper in ClickHouse Cloud. Nothing is written to the ephemeral user, which stays in memory. So the assignment survives the token expiring, the user being removed, and the next login creating a fresh one. In practice most teams will not assign anything per user at all. Profiles, quotas, and row policies can also be attached to a role, and since roles are what the token carries, attaching controls to the `analyst` role covers every analyst automatically.

<!-- Editorial note from Notion: Add explicit best-practice guidance for assigning profiles, quotas, and row policies to roles instead of inferred JWT users. -->

The same question applies to views. A view created with `SQL SECURITY DEFINER` runs with the permissions of whoever created it rather than whoever queries it. If the creator were an ephemeral user, the view would break the moment that user's token expired. So when a JWT user creates a definer view, ClickHouse writes a persistent shadow copy of the user, named after the original with a `:definer` suffix, holding the creator's rights at that moment and with no way to log in. The view runs as the shadow user from then on and keeps working after the original token is gone.

## Availability

|  | Built-in ClickHouse authenticator | Custom identity provider |
| --- | --- | --- |
| Used by | SQL Console, `clickhouse-client --login` | Any client with a token from your OIDC provider |
| Plans | All | Enterprise |
| Minimum version | Any | 26.4 (26.8 for EC keys) |
| Setup | None, provisioned with the service | Cloud console, Settings → Security |

## A foundation to build on

JWT authentication comes down to one idea: ClickHouse trusts a signed statement about who you are and which roles you hold, for as long as that statement is valid. Your identity provider decides access. Database users stop being things you create and delete. A token can be as narrow as one role and as short as one job, for a person at a terminal, a pipeline, or an agent that lives for a few minutes.

We think of JWT authentication as a foundation we can keep building on. A signed claim is a general way to hand ClickHouse a verified identity, and we can keep extending what a token carries, where it comes from, and what that identity can do.

The [JWT authentication reference](https://clickhouse.com/docs/concepts/features/security/external-authenticators/jwt) covers claims, ephemeral users, and client usage in detail.
