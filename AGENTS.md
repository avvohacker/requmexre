# Working conventions

## Keep the work moving

Billing is by time, not by token, so idle round trips cost real money. Do not
stop at a command, a workflow or a deploy when the next step is already known.

- Put every independent read, search, edit and command in the same response.
- While a check runs, start the next piece of work that does not depend on it.
- Do not end a turn to report intermediate progress. End it when the task is
  finished, a result is genuinely needed before the next step, or a question
  needs an answer.
- Prefer one batched verification command over several sequential ones.
- Do not poll CI, deploys or other external asynchronous results unless the
  user asks. Push or start the job, report that the result is pending, and
  continue with independent work.
- If a task requires waiting — a long build or test, a deploy, or a CI check
  the user asked to verify — hand it to a subagent so the main agent can keep
  working on independent steps. Collect the result before the step that depends
  on it; do not sit idle.

Some calls cannot be skipped: a validator, a build or a test whose output decides
the next edit must still run. If it is slow, run it in a subagent and keep
working on independent steps; collect the result before the dependent edit. The
rule is to avoid idle round trips, not to skip checks.
