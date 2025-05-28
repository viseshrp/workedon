# Contributing to `workedon`

Contributions are welcome, and they are greatly appreciated!
Every little bit helps, and credit will always be given.

You can contribute in many ways:

## Types of Contributions

### Report Bugs

Report bugs at <https://github.com/viseshrp/workedon/issues>

If you are reporting a bug, please include:

- Your operating system name and version.
- Any details about your local setup that might be helpful in troubleshooting.
- Detailed steps to reproduce the bug.

### Fix Bugs

Look through the GitHub issues for bugs.
Anything tagged with "bug" and "help wanted" is open to whoever wants to
implement a fix for it.

### Implement Features

Look through the GitHub issues for features.
Anything tagged with "enhancement" and "help wanted" is open to whoever
wants to implement it.

### Write Documentation

`workedon` could always use more documentation, whether as part of the official docs,
in docstrings, or even on the web in blog posts, articles, and such.

### Submit Feedback

The best way to send feedback is to file an issue at
<https://github.com/viseshrp/workedon/issues>.

If you are proposing a new feature:

- Explain in detail how it would work.
- Keep the scope as narrow as possible, to make it easier to implement.
- Remember that this is a volunteer-driven project, and that
  contributions are welcome :)

## Get Started

Ready to contribute? Here's how to set up `workedon` for local development.
Please note this documentation assumes you already have `uv` and `Git` installed.

1. Fork the `workedon` repo on GitHub.

2. Clone your fork locally:

    ```bash
    cd <directory_in_which_repo_should_be_created>
    git clone git@github.com:YOUR_NAME/workedon.git
    ```

3. Navigate into the project folder:

    ```bash
    cd workedon
    ```

4. Install and activate the environment:

    ```bash
    uv sync
    ```

5. Install pre-commit to run linters/formatters at commit time:

    ```bash
    uv run pre-commit install
    ```

6. Create a branch for local development:

    ```bash
    git checkout -b name-of-your-bugfix-or-feature
    ```

7. Add test cases for your changes in the `tests` directory.

8. Check formatting and style:

    ```bash
    make check
    ```

9. Run unit tests:

    ```bash
    make test
    ```

10. (Optional) Run `tox` to test against multiple Python versions:

    ```bash
    tox
    ```

11. Commit your changes and push your branch:

    ```bash
    git add .
    git commit -m "Your detailed description of your changes."
    git push origin name-of-your-bugfix-or-feature
    ```

12. Submit a pull request through the GitHub website.

## Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.

2. If the pull request adds functionality, update the documentation.
   Add a docstring, and update the feature list in `README.md`.
