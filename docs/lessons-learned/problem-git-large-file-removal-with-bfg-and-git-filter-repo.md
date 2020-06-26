# BFG Problem (Big File removal on qary)

## GitHub and GitLab prevent --force

Can't push bfg-cleaned repos (large files removed) to branches that have MRs on gitlab or PRs on github. Gitlab seems to also prohibit force pushes to tags.

```bash
du -hs qary  # fresh clone
# 1.1G
du -hs qary-clean  # old repo after several BFG runs and one git-filter-repo run.
# 217M
```

#### *`git config -e`*
```ini
[core]
        repositoryformatversion = 0
        filemode = true
        bare = false
        logallrefupdates = true
        ignorecase = true
        precomposeunicode = true
[remote "github"]
        url = git@github.com:nlpia/nlpia-bot
        fetch = +refs/heads/*:refs/remotes/github/*
[branch "master"]
        remote = all
        merge = refs/heads/master
[remote "old-origin"]
        url = git@gitlab.com:tangibleai/qary.git
        fetch = +refs/heads/*:refs/remotes/old-origin/*
[remote "gitlab"]
        url = git@gitlab.com:tangibleai/qary.git
        fetch = +refs/heads/*:refs/remotes/gitlab/*
[remote "all"]
    url=git@gitlab.com:tangibleai/qary-clean.git
    url=git@github.com:nlpia/qary-clean.git

[branch "develop"]
        remote = all
        merge = refs/heads/develop
[branch "master"]
        remote = all
        merge = refs/heads/master
```
Remotes on qary-clean need to be reset to prevent accidental pull of large files.

The github api shows the repo size at 30MB.

```bash
$ curl https://api.github.com/repos/nlpia/qary-clean | grep size
"size": 30742,
$ curl https://api.github.com/repos/nlpia/nlpia-bot | grep size
"size": 30669
```

```bash
$ git clone git@gitlab.com:tangibleai/qary-clean qary-clean.size
$ du -hs qary-clean.size
123M    qary-clean.size
$ git clone git@gitlab.com:tangibleai/qary qary.size
$ du -hs qary.size
516M    qary.size





```
