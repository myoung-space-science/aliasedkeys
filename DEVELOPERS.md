# Developer Notes

## Version Numbers

When incrementing the version number to X.Y.Z, please do the following
* create a new subsection in `CHANGELOG.md`, below **NEXT**, with the title
  format vX.Y.Z (YYYY-MM-DD)
* update the version number in `pyproject.toml`
* commit with the message "Increment version to X.Y.Z"
* create a tag named "vX.Y.Z" with the message "version X.Y.Z"
* push and follow tags

