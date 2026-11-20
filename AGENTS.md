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

Some calls must block: a validator, a build or a test whose output decides the
next edit cannot be skipped. The rule is to avoid idle round trips, not to run
commands without their results.
