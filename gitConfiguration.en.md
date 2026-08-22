# Git Configuration

## Configure global identity

The following commands write identity information to the current operating system user's global Git configuration and use it by default for all repositories handled by that user. Replace the placeholders with your real name and email address. These values become author and committer metadata in new commits; they are not credentials for GitHub, GitLab, or another hosting service.

```bash
# Set the default commit author name for all repositories.
git config --global user.name "Your Name"

# Set the default commit author email for all repositories.
git config --global user.email "your-email@example.com"
```

For example:

The following values only demonstrate the format. Re-running the same `git config` command replaces the previous value for that key instead of appending another entry.

```bash
# Example name; replace it as needed.
git config --global user.name "y"

# Example email; replace it as needed.
git config --global user.email "y@example.com"
```

Verify the configuration:

This command is read-only and does not modify repositories or global settings. Its output may also contain other global options, such as a credential helper or default branch name.

```bash
# List all global Git settings for the current user.
git config --global --list
```

The output should include:

```text
user.name=y
user.email=y@example.com
```

The actual values should match the name and email address entered in the previous step. You can then retry the commit. Existing commits in the repository history are not rewritten automatically by these settings.

## Configure only the current repository

To avoid affecting other repositories, enter the target repository first and omit `--global`. The values are stored in that repository's `.git/config` and override matching global values. The commands fail if the current directory is not inside a Git repository.

```bash
# Set the commit author name only for the current repository.
git config user.name "y"

# Set the commit author email only for the current repository.
git config user.email "y@example.com"
```

Re-running these commands updates the corresponding keys for the current repository and does not create duplicate settings.

## Configure a global proxy

The following example assumes that a proxy service is listening on the local loopback address `127.0.0.1`, port `7890`. Before running it, make sure the proxy application is active and replace the host, port, and scheme with the actual values. Because `--global` is used, the settings affect every Git repository accessed by the current user. Network operations such as fetch, push, and clone may fail while the proxy is unavailable.

```bash
# Set the global proxy for Git connections that use HTTP URLs.
git config --global http.proxy "http://127.0.0.1:7890"

# Write the existing example's global https.proxy key; whether it is read depends on Git configuration support.
git config --global https.proxy "http://127.0.0.1:7890"
```

These commands are repeatable: a new value replaces the existing value for the same key. If a proxy URL includes a username or password, it is stored as plain text in the user's configuration, so never commit a configuration file containing sensitive data.
