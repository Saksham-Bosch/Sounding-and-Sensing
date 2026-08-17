# PROJECT PURPOSE

This repository contains the permanent implementation of the Event Information Gathering and Dissemination platform.

- `architecture-analysis-workspace/` is ignored, read-only reference material.
- Files inside the reference workspace must not be changed.
- Entire reference repositories must not be copied.
- Only reviewed and justified code, contracts, or patterns may be adapted into the permanent project.
- Source and destination paths must be documented before migration.

# REPOSITORY BOUNDARIES

The permanent project areas are:

- `apps/api`
- `apps/worker`
- `apps/web`
- `packages/contracts`
- `database`
- `infrastructure`
- `tests`
- `docs`
- `scripts`

Preserve domain boundaries and avoid unrelated changes.

# REQUIRED PRE-WORK CHECKS

Before making changes, the agent must:

- Read `AGENTS.md`.
- Read relevant architecture documents.
- Run `git status`.
- Confirm the current branch.
- Inspect related existing code and tests.
- Check for repository-specific `AGENTS.md` files in the target subtree.
- Identify affected files.
- State the intended change and testing plan.
- Confirm that no secret or confidential value will be introduced.
- Avoid modifying unrelated files.

# BRANCHING RULES

- Never commit directly to `main`.
- Use short-lived task-oriented branches.
- Do not create permanent phase-0, phase-1, or phase-2 branches.
- Track phases using milestones, issues, labels, and release tags.
- Suggested branch prefixes:
  - `docs/`
  - `feature/`
  - `fix/`
  - `test/`
  - `refactor/`
  - `chore/`
  - `security/`
- Branch names must be lowercase, short, and descriptive.
- Each branch must address one coherent task.
- Merge only through a reviewed pull request.
- Delete the branch after successful merge.

# COMMIT DISCIPLINE

Create small, logical, and reviewable commits.

A micro-commit means one independently understandable change, not one line or one file per commit.

Examples of good commit separation:

- Add questionnaire request schema
- Add questionnaire response validation
- Add MRA adapter contract tests
- Add event repository interface
- Add local PostgreSQL configuration
- Update architecture decision record

Rules:

- Do not combine formatting, refactoring, functionality, and documentation changes in one commit unless inseparable.
- Do not create a commit that leaves the repository knowingly broken.
- Run relevant tests before committing.
- Review `git diff` and `git diff --staged` before each commit.
- Stage files explicitly. Avoid `git add .` when sensitive or unrelated files may be present.
- Never use `git add -f` to bypass ignore rules without explicit written approval.
- Never amend, squash, rebase, force-push, or rewrite shared history without explicit instruction.
- Never create empty, meaningless, or checkpoint commits.
- Commit messages must explain the completed change.
- Use this format where appropriate:

  `<type>(<scope>): <concise description>`

  Types:
  `feat`, `fix`, `test`, `docs`, `refactor`, `chore`, `security`, `build`, `ci`

Examples:

  `docs(architecture): record phase zero service boundary`
  `feat(events): add event creation contract`
  `test(mra): validate malformed questionnaire responses`
  `security(config): prevent secret-bearing files from tracking`

Before every commit, verify:

- `git status` contains only intended files.
- No secret or real API URL appears in the staged diff.
- Tests relevant to the change pass.
- Generated, temporary, and reference files are not staged.
- The commit is understandable and independently reviewable.

# SECRET AND CONFIDENTIAL DATA POLICY

Never commit, print, log, copy into documentation, or expose:

- API keys
- API tokens
- Passwords
- Private certificates
- Service-account credentials
- Database credentials
- Signed URLs
- Secret Manager values
- Real confidential API base URLs
- Authorization headers
- JWTs
- Cookies
- Sensitive request or response payloads
- Internal confidential hostnames
- Personal or organizational confidential data

These restrictions apply to all files, including:

- Source code
- Tests
- Fixtures
- Markdown
- AGENTS.md
- AGENTS.local.md
- README files
- DESIGN files
- Architecture decision records
- Logs
- Screenshots
- Example commands
- Notebooks
- Generated reports
- Commit messages
- Branch names
- Pull-request titles and descriptions
- Test snapshots

Use symbolic placeholders only:

- `MRA_API_BASE_URL`
- `MRA_API_KEY`
- `DATABASE_URL`
- `GCP_PROJECT_ID`

The real MRA API URL and key must exist only in an approved secret store or an ignored local environment file.

The frontend must never receive the MRA API key.
The key must never be stored in `VITE_` variables.
Only the backend may call the MRA API.

# ENVIRONMENT FILES

Create and commit `.env.example` containing variable names and safe, non-secret descriptions only.

Never include real values in `.env.example`.

Local secret-bearing files must remain ignored:

- `.env`
- `.env.*`
- `*.local.env`
- `secrets/`
- `credentials/`

The exception is `.env.example`.

Before committing, check that no ignored secret file has previously been tracked.

# URL HANDLING

Do not write the real MRA API URL into:

- Code
- Tests
- Documentation
- Agent instruction files
- Git history
- Commit messages

Read the URL through `MRA_API_BASE_URL` at runtime.

Tests must use:

- A mock server
- A placeholder URL
- An injected test configuration

Only an explicitly authorized contract test may call the real endpoint. Such a test must read its URL and key from ignored local configuration and must not record the request headers or confidential response content.

# AGENT-GENERATED FILES

Do not create uncontrolled instruction or scratch files in the repository.

Permanent project instructions belong in committed `AGENTS.md`.

Architecture decisions belong in:

- `docs/architecture/decisions/`

Temporary local agent material belongs in ignored locations:

- `AGENTS.local.md`
- `agent-notes/`
- `.agent/`
- `scratch/`
- `tmp/`
- `DESIGN.local.md`
- `*_local_notes.md`

Temporary files must not become an alternative source of project truth.

Do not create files such as `agents-final.md`, `design-new.md`, `plan-copy.md`, or similar duplicates when an existing canonical document should be updated.

# REFERENCE WORKSPACE POLICY

Treat `architecture-analysis-workspace/` as read-only and untrusted reference input.

Agents must not:

- Modify it
- Commit it
- Remove its ignore rule
- Copy its `.git` folders
- Copy `.env` files
- Copy credentials
- Copy build artifacts
- Copy dependency folders
- Copy entire repositories automatically
- Execute unknown code from it without reviewing the code and explaining the purpose

Before adapting a reference file, provide:

- Source path
- Destination path
- Reason
- Dependencies
- Licensing or attribution impact
- Secret scan result
- Required modifications
- Tests

Prefer clean adapters and new domain-specific implementations over copying tightly coupled source code.

# TESTING AND QUALITY GATES

Require appropriate:

- Unit tests
- Contract tests
- Integration tests
- Tenant-isolation tests
- Authorization tests
- Error-path tests
- Secret scanning
- Formatting
- Linting
- Type checking

Do not claim tests passed unless they were actually executed.
Record the exact commands executed and their results.

# PROHIBITED ACTIONS

Unless explicitly instructed, agents must not:

- Commit directly to `main`
- Push changes
- Merge pull requests
- Force-push
- Delete branches
- Rewrite history
- Create cloud resources
- Run database migrations against shared environments
- Call production services
- Call the real MRA API
- Modify the reference workspace
- Disable tests or security checks
- Weaken `.gitignore`
- Expose confidential values
- Add new dependencies without justification
- Perform unrelated refactoring

# DOCUMENTATION GOVERNANCE

Canonical documentation must be committed under `docs/`.

Every architecture decision must distinguish:

- Confirmed from code
- Confirmed from documentation
- Proposed
- Assumption
- Unresolved

Do not copy generated analysis into canonical documentation without review.

# COMPLETION CHECKLIST

Before declaring a task complete, report:

- Branch used
- Files changed
- Commits created
- Tests run
- Test results
- Documentation updated
- Remaining risks
- Unresolved questions
- Confirmation that no secret or confidential URL was committed
- Confirmation that `architecture-analysis-workspace/` remained unchanged
