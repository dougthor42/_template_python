# Changelog

This project doesn't really have releases so... this is really just the same
thing as the git commit history.


# 2023-10-24
+ Updated template to use Python 3.10.
+ Updates to CI, both the main project and the template itself.


## 2022-04-04
+ Added a `--version-check / --no-version-check` arg to the CLI. (#28)
+ Projects can now be made with a CLI entry point. (#13)


## 2021-09-30
+ Fixed type annotation issues in `setup.py`. (#26)


## 2021-09-05
+ Added a version check that will inform the user that there is a updated
  version available. (#24)


## 2021-07-30
+ Added `yamllint` to the template's pre-commit-config.yaml. (#16)
  + And also to the main project (#21)
+ Refactored tests a bit so that adding future tests is easier.
+ Added option to include CI files for either GitHub or GitLab. (#17)


## 2021-07-08
+ Added `__about__.py` to the coverage ignore (#11)


## 2021-06-20
+ Updated `py` version. #9.
+ Update `requests` and `urllib3` used by main project. (#10)


## 2021-04-08
+ Started logging changes.
