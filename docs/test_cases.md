# HCBS Test Cases Summary

## Test Strategy

The HCBS test suite uses a combination of:

- **Unit tests** — test individual functions and model logic in isolation (no network, no DB)
- **Integration tests** — test API endpoints end-to-end using FastAPI's TestClient and an in-memory SQLite database

**Framework:** pytest 8.3  
**Database:** SQLite (in-memory, isolated per test via transaction rollback)  
**Auth:** JWTs generated per test fixture, no real login required for integration tests  

---

## Test Cases Table

| # | ID | Category | Description | Input / Dataset | Expected Output | Status |
|---|-----|----------|-------------|-----------------|-----------------|--------|
| 1 | TC-SEC-01 | Security | Password hash produces valid bcrypt string | `hash_password("MySecret123")` | String starts with `$2b$`, length > 50 | ✅ |
| 2 | TC-SEC-02 | Security | Correct password verifies successfully | Original password + its hash | `verify_password()` returns `True` | ✅ |
| 3 | TC-SEC-03 | Security | Wrong password fails verification | Wrong password + hash | `verify_password()` returns `False` | ✅ |
| 4 | TC-SEC-04 | Security | JWT contains expected claims (sub, role, cinema_id) | `create_access_token(42, "testuser", "admin", 1)` | Payload has all 4 fields + exp | ✅ |
| 5 | TC-SEC-05 | Security | Valid JWT decodes correctly | Freshly created token | `decode_access_token()` returns dict | ✅ |
| 6 | TC-SEC-06 | Security | Expired JWT returns None | Token with -10s expiry | Returns `None` | ✅ |
| 7 | TC-SEC-07 | Security | Tampered JWT returns None | Modified last 4 chars of token | Returns `None` | ✅ |
| 8 | TC-SEC-08 | Security | Garbage token returns None | `""`, `"not.a.jwt"`, `"abc123"` | Returns `None` | ✅ |
| 9 | TC-PRC-01 | Pricing | Lower hall price returned directly | Base price £8.00, seat_type="lower_hall" | £8.00 | ✅ |
| 10 | TC-PRC-02 | Pricing | Upper gallery = lower × 1.20 | Base price £10.00 | £12.00 | ✅ |
| 11 | TC-PRC-03 | Pricing | VIP = lower × 1.44 (spec example) | Base price £10.00 | £14.40 | ✅ |
| 12 | TC-PRC-04 | Pricing | Bristol evening prices correct | Base £8 | Lower £8, Upper £9.60, VIP £11.52 | ✅ |
| 13 | TC-PRC-05 | Pricing | London morning prices correct | Base £10 | Lower £10, Upper £12, VIP £14.40 | ✅ |
| 14 | TC-PRC-06 | Pricing | Birmingham morning prices correct | Base £5 | Lower £5, Upper £6, VIP £7.20 | ✅ |
| 15 | TC-PRC-07 | Pricing | Invalid seat type raises ValueError | seat_type="premium_deluxe" | `ValueError` raised | ✅ |
| 16 | TC-PRC-08 | Pricing | All spec city prices verified | All 4 cities × 3 periods | All match spec table | ✅ |
| 17 | TC-MOD-01 | Models | Film duration display (hours + mins) | 130 mins | `"2h 10m"` | ✅ |
| 18 | TC-MOD-02 | Models | Film duration display (sub-hour) | 45 mins | `"45m"` | ✅ |
| 19 | TC-MOD-03 | Models | User full_name concatenation | "Aisha", "Khan" | `"Aisha Khan"` | ✅ |
| 20 | TC-MOD-04 | Models | Screen seat arithmetic validates | lower=24, upper=56, total=80 | lower + upper == total | ✅ |
| 21 | TC-MOD-05 | Models | VIP seats ≤ 10 | vip_seats=10 | Constraint holds | ✅ |
| 22 | TC-MOD-08 | Models | Booking reference format | HC-2025-00001 | Matches `HC-YYYY-#####` | ✅ |
| 23 | TC-EXC-01 | Exceptions | Base exception carries message + status | `HCBSException("err", 500)` | `.message="err"`, `.status_code=500` | ✅ |
| 24 | TC-EXC-02 | Exceptions | AuthenticationError defaults to 401 | Default constructor | `.status_code == 401` | ✅ |
| 25 | TC-EXC-07 | Exceptions | NotFoundError includes resource name | `NotFoundError("Film")` | `"Film not found"` | ✅ |
| 26 | TC-AUTH-01 | Auth API | Valid credentials return token + user | username/password for teststaff | 200, token + user info | ✅ |
| 27 | TC-AUTH-02 | Auth API | Wrong password returns 401 | Correct user, wrong password | 401 | ✅ |
| 28 | TC-AUTH-03 | Auth API | Non-existent username returns 401 | username="nobody" | 401 | ✅ |
| 29 | TC-AUTH-04 | Auth API | Empty username returns 422 | username="" | 422 (validation) | ✅ |
| 30 | TC-BK-01 | Booking | Availability check returns correct data | Evening showing, 2 lower hall | available=True, unit=£8, total=£16 | ✅ |
| 31 | TC-BK-02 | Booking | Create booking — confirmed status | 2 evening lower hall tickets | Status "confirmed", 2 seats assigned | ✅ |
| 32 | TC-BK-03 | Booking | Booking reference format | Any booking | Matches `HC-YYYY-#####` | ✅ |
| 33 | TC-BK-04 | Booking | Total cost = unit × tickets | 3 tickets @ £8 | total_cost = £24.00 | ✅ |
| 34 | TC-BK-05 | Booking | Look up by reference | Created booking ref | Returns matching booking | ✅ |
| 35 | TC-BK-06 | Booking | Cancel — 50% fee charged | Cancel £14 booking | Fee = £7.00 | ✅ |
| 36 | TC-BK-07 | Booking | Cancel — refund = total - fee | Cancel £14 booking | Refund = £7.00 | ✅ |
| 37 | TC-BK-08 | Booking | Cannot cancel already-cancelled | Cancel twice | Second attempt returns 400 | ✅ |
| 38 | TC-BK-09 | Booking | Cannot book for past date | show_date = yesterday | 400 "past" | ✅ |
| 39 | TC-BK-10 | Booking | Cannot book > 7 days ahead | show_date = today + 8 | 400 "7 days" | ✅ |
| 40 | TC-BK-11 | Booking | Cannot overbook seats | 6 VIP on 5-VIP screen | 400 "available" | ✅ |
| 41 | TC-BK-12 | Booking | No auth returns 403 | No token | 403 | ✅ |
| 42 | TC-BK-13 | Booking | Missing customer name → 422 | Omit customer_name | 422 | ✅ |
| 43 | TC-BK-14 | Booking | VIP pricing on booking | 1 VIP, Bristol evening | £11.52 | ✅ |
| 44 | TC-BK-15 | Booking | Upper gallery pricing | 2 upper, Bristol evening | £19.20 | ✅ |
| 45 | TC-BK-16 | Booking | Availability decreases after booking | Book 3, re-check | Available = before - 3 | ✅ |
| 46 | TC-BK-17 | Booking | Cancelled booking frees seats | Book → cancel → re-check | Available = original | ✅ |
| 47 | TC-BK-19 | Booking | Invalid showing_id → 404 | showing_id=99999 | 404 | ✅ |
| 48 | TC-BK-20 | Booking | Date outside listing window → 400 | +30 days | 400 | ✅ |
| 49 | TC-ROLE-01 | Roles | Staff can list films | GET /films with staff token | 200 | ✅ |
| 50 | TC-ROLE-02 | Roles | Staff cannot create films | POST /films with staff token | 403 | ✅ |
| 51 | TC-ROLE-03 | Roles | Staff cannot create cinemas | POST /cinemas with staff token | 403 | ✅ |
| 52 | TC-ROLE-04 | Roles | Admin can create films | POST /films with admin token | 201 | ✅ |
| 53 | TC-ROLE-05 | Roles | Admin cannot create cinemas | POST /cinemas with admin token | 403 | ✅ |
| 54 | TC-ROLE-06 | Roles | Manager can create cinemas | POST /cinemas with manager token | 201 | ✅ |
| 55 | TC-ROLE-07 | Roles | Manager can create films | POST /films with manager token | 201 | ✅ |
| 56 | TC-ROLE-08 | Roles | Admin can access reports | GET /reports/revenue | 200 | ✅ |
| 57 | TC-ROLE-09 | Roles | Staff cannot access reports | GET /reports/revenue | 403 | ✅ |
| 58 | TC-ROLE-10 | Roles | No token → 403 | GET /films, no header | 403 | ✅ |
| 59 | TC-FLM-01 | Films API | List films returns seeded film | GET /films | List includes "Top Gun" | ✅ |
| 60 | TC-FLM-02 | Films API | Create film returns 201 | POST /films, valid data | 201, is_active=True | ✅ |
| 61 | TC-FLM-03 | Films API | Update film changes title | PATCH /films/{id} | 200, new title | ✅ |
| 62 | TC-FLM-04 | Films API | Soft-delete sets is_active=False | DELETE /films/{id} | is_active=False | ✅ |
| 63 | TC-FLM-07 | Films API | Create listing with showings | POST /listings, 2 showings | 201, 2 showings returned | ✅ |
| 64 | TC-FLM-08 | Films API | Overlapping listing fails | Same screen, overlapping dates | 400 "overlap" | ✅ |
| 65 | TC-FLM-10 | Films API | Film listing display returns enriched data | GET /display/cinema/{id} | Includes prices in showings | ✅ |
| 66 | TC-CIN-01 | Cinemas API | List cinemas | GET /cinemas | Bristol + London | ✅ |
| 67 | TC-CIN-02 | Cinemas API | Cinema includes screens | GET /cinemas/{id} | Screens array with seat counts | ✅ |
| 68 | TC-CIN-03 | Cinemas API | Manager creates cinema (existing city) | POST /cinemas, city_id | 201 | ✅ |
| 69 | TC-CIN-04 | Cinemas API | Manager creates cinema (new city) | POST /cinemas, new_city_name | 201 | ✅ |
| 70 | TC-CIN-05 | Cinemas API | Manager adds screen | POST /cinemas/{id}/screens | 201, seats generated | ✅ |
| 71 | TC-CIN-09 | Cinemas API | Set base price (with derived check) | Set £7.50 morning | upper=£9.00, VIP=£10.80 | ✅ |
| 72 | TC-GEN-01 | General | Health check | GET /health | 200, status=ok | ✅ |
| 73 | TC-GEN-04 | General | Expired token → 401 | Expired JWT | 401 | ✅ |
| 74 | TC-GEN-05 | General | Booking search with filters | name, status filters | Matching results | ✅ |

---

## Running Tests

```bash
cd hcbs/
pip install pytest httpx --break-system-packages
pytest                    # all tests
pytest tests/unit/        # unit tests only
pytest tests/integration/ # integration tests only
pytest -v                 # verbose with test names
pytest --tb=long          # full tracebacks on failure
```