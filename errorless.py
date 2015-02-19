#!/usr/bin/env python

import sys
import re
import subprocess
import cmd

error_regexps = [
    "error:",
    "warning:",
]

print_error_format = "{id}) {summary}"

class Error():
    def __init__(self,
                 id,
                 error_type,
                 match_position):
        self.id = id
        self.type = error_type
        self.match_position = match_position

        self.lines = []

    def summary(self):
        print_error_format = "{id}) {summary}"

        summary_string = print_error_format.format(
            id=self.id,
            summary=self.lines[0][:self.match_position + len(error_regexps[self.type])]
        )

        return summary_string

class CommandLoop(cmd.Cmd):
    prompt = "(errorless) "

    def __init__(self, compile_fn):
        cmd.Cmd.__init__(self)
        self.compile_fn = compile_fn
        self.errors = compile_fn()


    def do_list(self, line):
        """list
        List all errors and warnings.
        """
        list_errors(self.errors)

    def do_show(self, line):
        """show [error no]
        Show all information for a particular error.
        """
        try:
            error_no = int(line) - 1
            print_error(self.errors[error_no])
        except ValueError:
            print("Syntax: show <error number>")
        except IndexError:
            print("Error doesn't exist.")

    def do_make(self, line):
        """make
        Re-run compilation.
        """
        self.errors = self.compile_fn()

    def do_quit(self, line):
        """
        Exit program.
        """
        return True

    def do_EOF(self, line):
        """
        Exit program.
        """
        return True

def list_errors(errors):
    for error in errors:
        print(error.summary())

def print_error(error):
    print("Error: {}".format(error.id))

    for line in error.lines:
        print(line)

def capture_compiler_output(compiler_shell_command):
    """
    Runs the compiler command passed as command line argument and returns
    a boolean indicating whether the compilation was successful (i.e. the
    subprocess returned 0) as well as the resulting lines.

    Returns
    -------

    The lines (note, doesn't return success yet.)
    """
    compile_process = subprocess.Popen(
        compiler_shell_command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    stdout_data, stderr_data = compile_process.communicate()
    lines = stderr_data.split('\n')

    print("stdout:")
    print(stdout_data)

    print("stderr:")
    print(stderr_data)

    # lines = []
    # while compile_process.poll() is None:
    #     stdout_line = compile_process.stdout.readline()
    #     if stdout_line != '':
    #         print(stdout_line)
    #     stderr_line = compile_process.stderr.readline()
    #     if stderr_line != '':
    #         print(stderr_line)
    #         lines.append(stderr_line)

    return lines

def parse_errors(compiler_output):
    errors = []
    regexp_objects = [re.compile(error_regexp) for error_regexp in error_regexps]


    for line_ind, line in enumerate(compiler_output):
        for errtype_ind, regexp_object in enumerate(regexp_objects):
            match_object = regexp_object.search(line)
            if match_object is not None:
                errors.append(
                    Error(
                        len(errors)+1,
                        errtype_ind,
                        match_object.start()
                    )
                )
        if len(errors) > 0:
            errors[-1].lines.append(line)

    return errors

def main():
    compiler_shell_command = ' '.join(sys.argv[1:])

    def compile_fn():
        print("Executing {}").format(compiler_shell_command)
        compiler_output = capture_compiler_output(compiler_shell_command)
        errors = parse_errors(compiler_output)
        return errors

    CommandLoop(compile_fn).cmdloop()

if __name__ == "__main__":
    main()
