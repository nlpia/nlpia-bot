# 2019-12 install failures

`conda` `environment.yml` file fails on Mac.

## `anaconda` channel is bad

The `anaconda` channel is incompatible with `conda-forge` and `defaults` channels.

```bash
$ conda install -c anaconda jupyter_client==5.2.0
Collecting package metadata (current_repodata.json): done
Solving environment: failed with initial frozen solve. Retrying with flexible solve.
Collecting package metadata (repodata.json): done
Solving environment: failed with initial frozen solve. Retrying with flexible solve.
Solving environment: \
Found conflicts! Looking for incompatible packages.
This can take several minutes.  Press CTRL-C to abort.
failed

UnsatisfiableError: The following specifications were found to be incompatible with each other:



Package wheel conflicts for:
jupyter_client==5.2.0 -> python=2.7 -> pip -> wheel
python=3.7 -> pip -> wheel
Package certifi conflicts for:
python=3.7 -> pip -> setuptools -> certifi[version='>=2016.09|>=2016.9.26']
jupyter_client==5.2.0 -> python=2.7 -> pip -> setuptools -> certifi[version='>=2016.09|>=2016.9.26']
Package pip conflicts for:
python=3.7 -> pip
jupyter_client==5.2.0 -> python=2.7 -> pip
Package ca-certificates conflicts for:
python=3.7 -> openssl[version='>=1.1.1a,<1.1.2a'] -> ca-certificates
jupyter_client==5.2.0 -> python=2.7 -> ca-certificates
Package setuptools conflicts for:
jupyter_client==5.2.0 -> python=2.7 -> pip -> setuptools
python=3.7 -> pip -> setuptools
Package python conflicts for:
python=3.7
Package ipython_genutils conflicts for:
jupyter_client==5.2.0 -> jupyter_core -> ipython_genutils==0.1.0
Package python-dateutil conflicts for:
jupyter_client==5.2.0 -> python-dateutil[version='>=2.1']
```

## `.condarc` must remove the anaconda channel

```file: ~/.condarc
channels:
  - defaults  # top priority: https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-channels.html#managing-channels
  - conda-forge
  # - anaconda  # bad idea: https://github.com/conda/conda/issues/9462
add_pip_as_python_dependency: true
always_yes: false
report_errors: true
channel_priority: false
```


## jupyter_client-ipython dependency conflict

It looks like `ipython 7.10.1` requires `prompt-toolkit 1.0.18` but `jupyter-client 5.3.4` and/or `jupyter-console 5.2.0` requires prompt-toolkit >=2.0.0 or >=3.0.2

```bash
$ bot hello
pkg_resources.ContextualVersionConflict: (prompt-toolkit 1.0.18 (/Users/hobs/opt/anaconda3/envs/nlpenv/lib/python3.7/site-packages), Requirement.parse('prompt-toolkit!=3.0.0,!=3.0.1,<3.1.0,>=2.0.0'), {'ipython'})
```

spacy 2.2.2 breaks ipython and jupyter_client due to dependency conflict (they can't both use prompt-toolkit 3.0.2)

```
$ pip install 'prompt-toolkit!=3.0.0,!=3.0.1,<3.1.0,>=2.0.0'
# ERROR: jupyter-console 5.2.0 has requirement prompt-toolkit<2.0.0,>=1.0.0, but you'll have prompt-toolkit 3.0.2 which is incompatible.
$ bot hello
pkg_resources.ContextualVersionConflict: (prompt-toolkit 3.0.2 (/Users/hobs/opt/anaconda3/envs/nlpenv/lib/python3.7/site-packages), Requirement.parse('prompt-toolkit<2.0.0,>=1.0.0'), {'jupyter-console'})
pkg_resources.DistributionNotFound: The 'prompt-toolkit<2.0.0,>=1.0.0' distribution was not found and is required by jupyter-console
$ pip list | grep -i prompt
prompt-toolkit       3.0.2
```
