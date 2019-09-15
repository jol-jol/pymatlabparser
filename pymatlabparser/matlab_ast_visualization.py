def display_tree(matlab_node, indent_str=''):
    if len(matlab_node) == 1:
        return str(matlab_node[0]) + '\n'

    node_name_string = matlab_node[0]
    childens_indent_str = len(node_name_string) * ' '

    if len(matlab_node[1]) == 1:
        display_string = node_name_string + ' ──── ' + \
                         display_tree(matlab_node[1][0], indent_str=indent_str+childens_indent_str+'      ')
    else:
        display_string = node_name_string + ' ─┬── ' + \
                         display_tree(matlab_node[1][0], indent_str=indent_str + childens_indent_str + '  │   ')
        for child_node in matlab_node[1][1:-1]:
            display_string += indent_str + len(node_name_string) * ' ' + '  ├── ' + \
                              display_tree(child_node, indent_str=indent_str+childens_indent_str+'  │   ')
        display_string += indent_str + len(node_name_string) * ' ' + '  └── ' + \
                          display_tree(matlab_node[1][-1], indent_str=indent_str+childens_indent_str+'      ')
    return display_string