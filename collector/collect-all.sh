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


do_collect answer AnswerGitCollector.py
do_collect gitlab GitlabCollector.py
do_collect grade GradeGitCollector.py
do_collect piazza PiazzaCollector.py
