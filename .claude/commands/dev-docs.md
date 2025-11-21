# /dev-docs - Development Documentation Command

Creates structured development documentation for tracking complex features or bugs.

## Usage

```
/dev-docs [feature-name]
```

This command creates a `dev/active/[feature-name]/` directory with three files:

### TASK.md
The what and why:
- What are we building?
- Why are we building it?
- What's the user story or requirement?
- Success criteria

### CONTEXT.md
The current state:
- Relevant file locations
- Existing patterns in the codebase
- Dependencies and constraints
- Related code sections

### PLAN.md
The how:
- Step-by-step implementation plan
- Technical decisions
- Testing strategy
- Rollout plan

## Example

After running `/dev-docs user-authentication`:

```
dev/active/user-authentication/
├── TASK.md
├── CONTEXT.md
└── PLAN.md
```

## TASK.md Template

```markdown
# Task: User Authentication

## Objective
Implement JWT-based authentication for the API

## Requirements
- [ ] User registration endpoint
- [ ] Login endpoint with JWT token generation
- [ ] Token refresh mechanism
- [ ] Protected route decorator
- [ ] Password hashing with bcrypt

## User Story
As an API consumer, I need to authenticate users so that I can secure protected endpoints.

## Success Criteria
- Users can register with email/password
- Users can login and receive a JWT token
- Protected endpoints reject unauthenticated requests
- Tokens expire after 24 hours
- All tests pass
```

## CONTEXT.md Template

```markdown
# Context: User Authentication

## Current State
- No authentication currently implemented
- Database has users table
- Using SQLAlchemy for ORM
- FastAPI framework

## Relevant Files
- `app/models/user.py` - User model
- `app/routes/` - API routes location
- `app/database.py` - Database setup

## Dependencies
- `python-jose[cryptography]` - JWT handling
- `passlib[bcrypt]` - Password hashing
- `python-multipart` - Form data parsing

## Constraints
- Must work with existing user model
- Need to maintain backward compatibility
- PostgreSQL database in production

## Related Patterns
Similar auth implementation in project X
```

## PLAN.md Template

```markdown
# Plan: User Authentication

## Phase 1: Setup
1. Install dependencies
   ```bash
   pip install python-jose[cryptography] passlib[bcrypt]
   ```

2. Create auth utilities
   - `app/utils/auth.py` - JWT and password functions

3. Update user model
   - Add `hashed_password` field
   - Create migration

## Phase 2: Implementation
1. Create auth schemas (`app/schemas/auth.py`)
   - UserRegister
   - UserLogin
   - Token

2. Create auth service (`app/services/auth_service.py`)
   - register_user()
   - authenticate_user()
   - create_access_token()

3. Create auth routes (`app/routes/auth.py`)
   - POST /register
   - POST /login
   - POST /refresh

4. Create auth dependency (`app/dependencies.py`)
   - get_current_user()

## Phase 3: Testing
1. Unit tests for auth service
2. Integration tests for endpoints
3. Security tests

## Phase 4: Documentation
1. Update API docs
2. Add usage examples
3. Security best practices

## Technical Decisions
- JWT algorithm: HS256
- Token expiry: 24 hours
- Password hashing: bcrypt (cost factor 12)

## Testing Strategy
- Pytest fixtures for test users
- Mock JWT tokens for testing
- Integration tests with test database

## Rollout
1. Deploy to staging
2. Test with staging database
3. Deploy to production
4. Monitor for issues
```

## Benefits

✅ Keeps complex features organized
✅ Provides context for future developers
✅ Makes it easy to resume work after interruptions
✅ Documents decisions and reasoning
✅ Serves as a handoff document

## Best Practices

- Create dev docs BEFORE starting complex features
- Update as you learn more
- Delete from `dev/active/` when complete
- Archive to `dev/archive/` if needed for reference
- Keep TASK.md focused on "what"
- Keep CONTEXT.md focused on "current state"
- Keep PLAN.md focused on "how"

## Integration with Claude

When resuming work on a feature:
1. Read the three dev docs files
2. Update PLAN.md as you progress
3. Mark items complete in TASK.md
4. Add new learnings to CONTEXT.md

This gives Claude complete context instantly!
