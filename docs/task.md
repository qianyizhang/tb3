
Start by reading:
- Terminal-Bench 3 Contribution Call: https://www.tbench.ai/news/tb3-contribution-call
- Repository Contributing Guide: https://github.com/harbor-framework/terminal-bench/blob/main/CONTRIBUTING.md

Please read the contributing guide and the repository’s CI and review documentation carefully and follow them in full. Understanding and applying these requirements independently is part of the assignment; the summary below is not a substitute for the documentation.
Your final task must meet the requirements defined by the current TB3 CI:
Automated checks: Pass all required static checks, implementation-rubric checks, Docker build, oracle validation, and nop validation.
Standard agent trials (/run): Run codex (gpt 5.6 sol xhigh) and claude code (opus 5 max) agent/model configuration specified by the current TB3 CI three times. For each configuration, all three trials must genuinely fail to pass the verifier. Agent crashes, API or rate-limit failures, container failures, timeouts, and other execution or infrastructure errors do not count as model failures.
Adversarial trials (/cheat): Run codex (gpt 5.6 sol xhigh) and claude code (opus 5 max) once. Every adversarial trial must receive zero reward. Any nonzero reward means this requirement has not been met, and the verifier must not be exploitable or bypassable.
The current TB3 CI configuration and review automation are the source of truth for the default agent/model configurations, trial count, and /run and /cheat behavior.
Please send us a GitHub repo within seven days. Document the check results, trial results, and a brief failure analysis in the repository. Your repository should include the task and clearly document the commands, configurations, and results for all required checks and evaluation runs.
You are responsible for running all standard and adversarial trials yourself using the current Terminal-Bench 3 CI defaults. You do not need to create a PR to do this.
You may use LLMs and coding agents extensively. Please be prepared to discuss your task design, verification strategy, iteration process, and analysis of the model failures.
You do not need to pay API price for this. Below are sample instructions for using claude code and codex subscriptions.
Codex: First login into codex, then
```
harbor run -p tasks/hello-world \
  --agent codex --model openai/gpt-5.6-sol \
  --env docker --yes --ae CODEX_FORCE_AUTH_JSON=1 --ak reasoning_effort=xhigh
```
