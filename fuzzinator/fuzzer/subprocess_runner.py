# Copyright (c) 2016 Renata Hodovan, Akos Kiss.
#
# Licensed under the BSD 3-Clause License
# <LICENSE.rst or https://opensource.org/licenses/BSD-3-Clause>.
# This file may not be copied, modified, or distributed except
# according to those terms.

import json
import shutil
import subprocess
import os


class SubprocessRunner(object):
    """
    Wrapper around a fuzzer that is available as an executable and can generate
    its test cases as file(s) in a directory. First, the external executable is
    invoked as a subprocess, and once it has finished, the contents of the
    generated files are returned one by one.

    **Mandatory parameters of the fuzzer:**

      - ``command``: string to pass to the child shell as a command to run (all
        occurrences of ``{uid}`` in the string are replaced by an identifier
        unique to this fuzz job).
      - ``outdir``: path to the directory containing the files generated by the
        external fuzzer (all occurrences of ``{uid}`` in the path are replaced
        by the same identifier as described at the ``command`` parameter).

    **Optional parameters of the fuzzer:**

      - ``cwd``: if not ``None``, change working directory before the command
        invocation.
      - ``env``: if not ``None``, a dictionary of variable names-values to
        update the environment with.

    **Example configuration snippet:**

        .. code-block:: ini

            [sut.foo]
            # see fuzzinator.call.*

            [fuzz.foo-with-bar]
            sut=sut.foo
            fuzzer=fuzzinator.fuzzer.SubprocessRunner
            batch=50

            [fuzz.foo-with-bar.fuzzer.init]
            outdir=${fuzzinator:work_dir}/bar/{uid}
            command=barfuzzer -n ${fuzz.foo-with-bar:batch} -o ${outdir}
    """

    def __init__(self, outdir, command, cwd=None, env=None, **kwargs):
        # uid is used to make sure we create unique directory for the generated test cases.
        self.uid = '{pid}-{id}'.format(pid=os.getpid(), id=id(self))

        self.outdir = outdir.format(uid=self.uid)
        self.command = command
        self.cwd = cwd or os.getcwd()
        self.env = dict(os.environ, **json.loads(env)) if env else None

        self.tests = []

    def __enter__(self):
        os.makedirs(self.outdir, exist_ok=True)
        with open(os.devnull, 'w') as FNULL:
            with subprocess.Popen(self.command.format(uid=self.uid),
                                  cwd=self.cwd,
                                  env=self.env,
                                  shell=True,
                                  stdout=FNULL,
                                  stderr=FNULL) as proc:
                proc.wait()
        self.tests = [os.path.join(self.outdir, test) for test in os.listdir(self.outdir)]
        return self

    def __exit__(self, *exc):
        shutil.rmtree(self.outdir, ignore_errors=True)
        return None

    # Although kwargs is not used here but the 'index' argument will be passed anyhow
    # and it has to be accepted.
    def __call__(self, **kwargs):
        if not self.tests:
            return None

        test = self.tests.pop()
        with open(test, 'rb') as f:
            return f.read()
