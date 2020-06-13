# Lessons Learned

## `pip install dotenv`

On Mac OSX with conda installed in base environment with python=3.7


```bash
pip install dotenv
      File "/Users/hobs/opt/anaconda3/lib/python3.7/site-packages/setuptools/installer.py", line 130, in fetch_build_egg
        raise DistutilsError(str(e))
    distutils.errors.DistutilsError: Command '['/Users/hobs/opt/anaconda3/bin/python3.7', '-m', 'pip', '--disable-pip-version-check', 'wheel', '--no-deps', '-w', '/var/folders/q3/wqt5d46x3f9_q45gj67dq_dw0000gq/T/tmp8s7knv1a', '--quiet', 'distribute']' returned non-zero exit status 1.
    ----------------------------------------
ERROR: Command errored out with exit status 1: python setup.py egg_info Check the logs for full command output.
```

### Didn't help

```bash
conda install dotenv
pip install --upgrade pip
```

### Solution

[Stack Overflow to the rescue](https://stackoverflow.com/a/49328725/623735)

```bash
conda install python-dotenv
# OR
pip install python-dotenv
```

Fixed in version 0.5.8



