Day 2 | Easy • Web • Directory Enumeration

An Nmap scan was performed to enumerate the target and identify the exposed services. (nmap -sCV -p- -v 10.48.182.139)

The scan revealed an exposed .git repository. The repository was then dumped using: git-dumper http://10.48.182.139:8080/.git dumped_repo

After reviewing the dumped repository, the README.md file contained the flag, completing the challenge.
