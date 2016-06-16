#! /bin/bash

do_collect()
{
    collector="collector-$1"
    py_script=$2
    echo "running $collector..."
    (
        cd $collector
        python $py_script
    )
}

# connect to vpn
sudo vpnc supervessal

do_collect answer AnswerGitCollector.py
do_collect gitlab GitlabCollector.py
do_collect grade GradeGitCollector.py

sudo vpnc-disconnect

do_collect piazza PiazzaCollector.py
