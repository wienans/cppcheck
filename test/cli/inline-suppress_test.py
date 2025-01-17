
# python -m pytest test-inline-suppress.py

import json
import os
import pytest
from testutils import cppcheck

__script_dir = os.path.dirname(os.path.abspath(__file__))
__proj_inline_suppres_path = 'proj-inline-suppress' + os.path.sep


def __create_unused_function_compile_commands(tmpdir):
    prjpath = os.path.realpath(os.path.join(__script_dir, 'proj-inline-suppress-unusedFunction'))
    j = [{'directory': prjpath,
          'command': '/usr/bin/c++ -I"' + prjpath + '" -o "' + os.path.join(prjpath, 'B.cpp.o') + '" -c "' + os.path.join(prjpath, 'B.cpp') + '"',
          'file': os.path.join(prjpath, 'B.cpp')},
         {'directory': prjpath,
          'command': '/usr/bin/c++ -I"' + prjpath + '" -o "' + os.path.join(prjpath, 'A.cpp.o') + '" -c "' + os.path.join(prjpath, 'A.cpp') + '"',
          'file': os.path.join(prjpath, 'A.cpp')}]
    compdb_path = os.path.join(tmpdir, 'proj-inline-suppress-unusedFunction')
    os.makedirs(compdb_path)
    compile_commands = os.path.join(compdb_path, 'compile_commands.json')
    with open(compile_commands, 'wt') as f:
        f.write(json.dumps(j, indent=4))
    return compile_commands


def __test1(use_j):
    args = [
        '-q',
        '--template=simple',
        '--inline-suppr',
        'proj-inline-suppress'
    ]
    if use_j:
        args.append('-j2')
    ret, stdout, stderr = cppcheck(args, cwd=__script_dir)
    assert stderr == ''
    assert stdout == ''
    assert ret == 0, stdout


def test1():
    __test1(False)


def test1_j():
    __test1(True)


def __test2(use_j):
    args = [
        '-q',
        '--template=simple',
        'proj-inline-suppress'
    ]
    if use_j:
        args.append('-j2')
    ret, stdout, stderr = cppcheck(args, cwd=__script_dir)
    lines = stderr.splitlines()
    assert lines == [
        '{}3.cpp:4:19: error: Division by zero. [zerodiv]'.format(__proj_inline_suppres_path)
    ]
    assert stdout == ''
    assert ret == 0, stdout


def test2():
    __test2(False)


def test2_j():
    __test2(True)


def __test_unmatched_suppression(use_j):
    args = [
        '-q',
        '--template=simple',
        '--inline-suppr',
        '--enable=information',
        '--disable=missingInclude',
        '--error-exitcode=1',
        '{}2.c'.format(__proj_inline_suppres_path)
    ]
    if use_j:
        args.append('-j2')
    ret, stdout, stderr = cppcheck(args, cwd=__script_dir)
    lines = stderr.splitlines()
    assert lines == [
        '{}2.c:2:0: information: Unmatched suppression: some_warning_id [unmatchedSuppression]'.format(__proj_inline_suppres_path)
    ]
    assert stdout == ''
    assert ret == 1, stdout


def test_unmatched_suppression():
    __test_unmatched_suppression(False)


def test_unmatched_suppression_j():
    __test_unmatched_suppression(True)


def __test_unmatched_suppression_path_with_extra_stuff(use_j):
    args = [
        '-q',
        '--template=simple',
        '--inline-suppr',
        '--enable=information',
        '--disable=missingInclude',
        '--error-exitcode=1',
        '{}2.c'.format(__proj_inline_suppres_path)
    ]
    if use_j:
        args.append('-j2')
    ret, stdout, stderr = cppcheck(args, cwd=__script_dir)
    lines = stderr.splitlines()
    assert lines == [
        '{}2.c:2:0: information: Unmatched suppression: some_warning_id [unmatchedSuppression]'.format(__proj_inline_suppres_path)
    ]
    assert stdout == ''
    assert ret == 1, stdout


def test_unmatched_suppression_path_with_extra_stuff():
    __test_unmatched_suppression_path_with_extra_stuff(False)


def test_unmatched_suppression_path_with_extra_stuff_j():
    __test_unmatched_suppression_path_with_extra_stuff(True)


def __test_backwards_compatibility(use_j):
    args = [
        '-q',
        '--template=simple',
        '{}3.cpp'.format(__proj_inline_suppres_path)
    ]
    if use_j:
        args.append('-j2')
    ret, stdout, stderr = cppcheck(args, cwd=__script_dir)
    lines = stderr.splitlines()
    assert lines == [
        '{}3.cpp:4:19: error: Division by zero. [zerodiv]'.format(__proj_inline_suppres_path)
    ]
    assert stdout == ''
    assert ret == 0, stdout

    args = [
        '-q',
        '--template=simple',
        '--inline-suppr',
        '{}3.cpp'.format(__proj_inline_suppres_path)
    ]
    if use_j:
        args.append('-j2')
    ret, stdout, stderr = cppcheck(args, cwd=__script_dir)
    lines = stderr.splitlines()
    assert lines == []
    assert stdout == ''
    assert ret == 0, stdout


def test_backwards_compatibility():
    __test_backwards_compatibility(False)


def test_backwards_compatibility_j():
    __test_backwards_compatibility(True)


def __test_compile_commands_unused_function(tmpdir, use_j):
    compdb_file = __create_unused_function_compile_commands(tmpdir)
    args = [
        '-q',
        '--template=simple',
        '--enable=all',
        '--error-exitcode=1',
        '--project={}'.format(compdb_file)
    ]
    if use_j:
        args.append('-j2')
    ret, stdout, stderr = cppcheck(args)
    proj_path_sep = os.path.join(__script_dir, 'proj-inline-suppress-unusedFunction') + os.path.sep
    lines = stderr.splitlines()
    assert lines == [
        "{}B.cpp:6:0: style: The function 'unusedFunctionTest' is never used. [unusedFunction]".format(proj_path_sep)
    ]
    assert stdout == ''
    assert ret == 1, stdout


def test_compile_commands_unused_function(tmpdir):
    __test_compile_commands_unused_function(tmpdir, False)


@pytest.mark.skip  # unusedFunction does not work with -j
def test_compile_commands_unused_function_j(tmpdir):
    __test_compile_commands_unused_function(tmpdir, True)


def __test_compile_commands_unused_function_suppression(tmpdir, use_j):
    compdb_file = __create_unused_function_compile_commands(tmpdir)
    args = [
        '-q',
        '--template=simple',
        '--enable=all',
        '--inline-suppr',
        '--error-exitcode=1',
        '--project={}'.format(compdb_file)
    ]
    if use_j:
        args.append('-j2')
    ret, stdout, stderr = cppcheck(args)
    lines = stderr.splitlines()
    assert lines == []
    assert stdout == ''
    assert ret == 0, stdout


def test_compile_commands_unused_function_suppression(tmpdir):
    __test_compile_commands_unused_function_suppression(tmpdir, False)


@pytest.mark.skip  # unusedFunction does not work with -j
def test_compile_commands_unused_function_suppression_j(tmpdir):
    __test_compile_commands_unused_function_suppression(tmpdir, True)


def __test_unmatched_suppression_ifdef(use_j):
    args = [
        '-q',
        '--template=simple',
        '--enable=information',
        '--disable=missingInclude',
        '--inline-suppr',
        '-DNO_ZERO_DIV',
        'trac5704/trac5704a.c'
    ]
    if use_j:
        args.append('-j2')
    ret, stdout, stderr = cppcheck(args, cwd=__script_dir)
    lines = stderr.splitlines()
    assert lines == []
    assert stdout == ''
    assert ret == 0, stdout


def test_unmatched_suppression_ifdef():
    __test_unmatched_suppression_ifdef(False)


def test_unmatched_suppression_ifdef_j():
    __test_unmatched_suppression_ifdef(True)


def __test_unmatched_suppression_ifdef_0(use_j):
    args = [
        '-q',
        '--template=simple',
        '--enable=information',
        '--disable=missingInclude',
        '--inline-suppr',
        'trac5704/trac5704b.c'
    ]
    if use_j:
        args.append('-j2')
    ret, stdout, stderr = cppcheck(args, cwd=__script_dir)
    lines = stderr.splitlines()
    assert lines == []
    assert stdout == ''
    assert ret == 0, stdout


def test_unmatched_suppression_ifdef_0():
    __test_unmatched_suppression_ifdef_0(False)


def test_unmatched_suppression_ifdef_0_j():
    __test_unmatched_suppression_ifdef_0(True)


def __test_build_dir(tmpdir, use_j):
    args = [
        '-q',
        '--template=simple',
        '--cppcheck-build-dir={}'.format(tmpdir),
        '--enable=all',
        '--inline-suppr',
        '{}4.c'.format(__proj_inline_suppres_path)
    ]
    if use_j:
        args.append('-j2')

    ret, stdout, stderr = cppcheck(args, cwd=__script_dir)
    lines = stderr.splitlines()
    assert lines == []
    assert stdout == ''
    assert ret == 0, stdout

    ret, stdout, stderr = cppcheck(args, cwd=__script_dir)
    lines = stderr.splitlines()
    assert lines == []
    assert stdout == ''
    assert ret == 0, stdout


def test_build_dir(tmpdir):
    __test_build_dir(tmpdir, False)


def test_build_dir_j(tmpdir):
    __test_build_dir(tmpdir, True)


def __test_build_dir_unused_template(tmpdir, use_j):
    args = [
        '-q',
        '--template=simple',
        '--cppcheck-build-dir={}'.format(tmpdir),
        '--enable=all',
        '--inline-suppr',
        '{}template.cpp'.format(__proj_inline_suppres_path)
    ]
    if use_j:
        args.append('-j2')

    ret, stdout, stderr = cppcheck(args, cwd=__script_dir)
    lines = stderr.splitlines()
    assert lines == []
    assert stdout == ''
    assert ret == 0, stdout


def test_build_dir_unused_template(tmpdir):
    __test_build_dir_unused_template(tmpdir, False)


@pytest.mark.xfail(strict=True)
def test_build_dir_unused_template_j(tmpdir):
    __test_build_dir_unused_template(tmpdir, True)


def __test_suppress_unmatched_inline_suppression(use_j):  # 11172
    args = [
        '-q',
        '--template=simple',
        '--enable=information',
        '--disable=missingInclude',
        '--suppress=unmatchedSuppression',
        '--inline-suppr',
        '{}2.c'.format(__proj_inline_suppres_path)
    ]
    if use_j:
        args.append('-j2')
    ret, stdout, stderr = cppcheck(args, cwd=__script_dir)
    lines = stderr.splitlines()
    assert lines == []
    assert stdout == ''
    assert ret == 0, stdout


def test_suppress_unmatched_inline_suppression():
    __test_suppress_unmatched_inline_suppression(False)


def test_suppress_unmatched_inline_suppression_j():
    __test_suppress_unmatched_inline_suppression(True)
