from DSLTools.core.wirth_diagram_generation import generate_dot
from DSLTools.utils.wirth_render import render_dot_to_png

names = ["Alternative", "Element", "Group", "Iteration", "Optional", "Rule", "RuleElement", "Sequence"]
directory_to_save = r"C:\Users\Hp\PycharmProjects\DSL\DSLTools\examples\rbnf"
for name in names:
    cur_path = fr"{directory_to_save}\wirth\{name}.gv"
    render_dot_to_png(cur_path, fr"{directory_to_save}\wirthpng")