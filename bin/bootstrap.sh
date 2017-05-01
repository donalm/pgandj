#!/bin/zsh

bin_directory=$(cd -P -- "$(dirname -- "$0")" && printf '%s\n' "$(pwd -P)")
export BASEDIR=$(dirname $bin_directory)

bootstrap_script=${(%):-%N}
bindir=`dirname $bootstrap_script`
bindir_abs=`cd $bindir && pwd`
basedir=`dirname $bindir_abs`
scriptname=`basename $0`
source "${basedir}/venv/bin/activate"

export PYTHONPATH="$basedir"
export PYTHONDONTWRITEBYTECODE=1

exec $bindir_abs/_$scriptname.py $@
