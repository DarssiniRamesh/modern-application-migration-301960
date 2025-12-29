Auth tests overview

- Scope:
  - User: POST /auth/register, POST /auth/login, GET /users/me (Bearer)
  - Negative: login with wrong password
  - Admin: POST /admin/auth/register, POST /admin/auth/login, GET /admin/me (Bearer), GET /admin/admins (Bearer)
- Bearer in Swagger/OpenAPI is verified by using Authorization: Bearer <token> header in tests.
- Each test module sets DATABASE_URL to a dedicated sqlite file for isolation and sets JWT_SECRET_KEY for deterministic tokens.
- TestClient uses lifespan to execute app startup which creates tables and seeds baseline data.

Run only auth tests:
  pytest -q tests/auth -k "auth" --maxfail=1

Results summary template (fill after running):
  - Total tests: <N>
  - Passed: <P>, Failed: <F>, Skipped: <S>, XFailed: <XF>, XPassed: <XP>
  - Key verifications:
    - User register/login/me OK
    - Bearer token required for protected endpoints
    - Wrong password yields 401 Invalid credentials
    - Admin register/login/me OK
    - Admin list requires Bearer and returns array including current admin
  - Notes:
    - Test DB file(s): sqlite:///.../test_auth.db, test_auth_admin.db
    - Any flakiness or setup concerns:
