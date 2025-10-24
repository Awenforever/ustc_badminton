# save as diff_maker.py
import difflib
import re


def latex_diff(old_file, new_file, output_file):
    with open(old_file, 'r') as f:
        old_text = f.read().splitlines()
    with open(new_file, 'r') as f:
        new_text = f.read().splitlines()

    # 创建差异比较器
    differ = difflib.Differ()
    diff = list(differ.compare(old_text, new_text))

    # 添加 LaTeX 标记
    output = []
    output.append(r"\usepackage{xcolor, soul}")
    output.append(r"\definecolor{diffadd}{rgb}{0,0.5,0}")
    output.append(r"\definecolor{diffdel}{rgb}{0.8,0,0}")
    output.append(r"\newcommand{\added}[1]{\textcolor{diffadd}{#1}}")
    output.append(r"\newcommand{\deleted}[1]{\textcolor{diffdel}{\st{#1}}}")
    output.append("")

    for line in diff:
        if line.startswith('+ '):
            output.append(r"\added{" + line[2:] + "}")
        elif line.startswith('- '):
            output.append(r"\deleted{" + line[2:] + "}")
        elif line.startswith('  '):
            output.append(line[2:])

    with open(output_file, 'w') as f:
        f.write("\n".join(output))


# 使用示例
latex_diff('scratchV11.tex', 'manuscriptV12.tex', 'diff.tex')
