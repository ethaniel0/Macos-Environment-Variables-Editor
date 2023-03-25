import streamlit as st
from pathlib import Path
from pprint import pprint
import os
import sys
    
paths = [Path.home() / '.zshrc', Path.home() / '.zprofile', Path.home() / '.bash_profile', Path.home() / '.profile', '/etc/paths', '/etc/bashrc', '/etc/profile']

paths += ['/etc/paths.d/' + f for f in os.listdir('/etc/paths.d')]
    
keywords = ['export', 'alias', '.']

st.set_page_config(layout="wide")
st.markdown('# Environment Variable Editor')

st.markdown("""
<style>
    div[data-testid=stVerticalBlock] {
        gap: 0;
    }
    div[data-testid=stHorizontalBlock] {
        border: 1px solid lightgray;
        padding: 10px 10px;
        border-bottom: none;
    }
    div[data-testid=stHorizontalBlock]:last-child {
        border-bottom: 1px solid lightgray;
    }
    div[data-testid=stHorizontalBlock] > div {
        border-right: 1px solid lightgray;
        # padding: 0 10px;
    }
    div[data-testid=stHorizontalBlock] > div:last-child {
        border-right: none;
    }
    div.stTextInput > label {
        display: none;
    }
    div[data-testid=column] {
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    div[data-testid=column] > div:first-child {
        flex: unset !important;
    }

    
</style>
""", unsafe_allow_html=True)

edit_file = str(st.selectbox('Edit files', paths))

def get_lines(path: str):
    table = []
    flines = []
    
    with open(path, 'r') as file:
        lines = [l.strip() for l in file.readlines()]
        pathvar = ''
        pathvarnum = -1
        for i in range(len(lines)):
            line = lines[i]
            if line.startswith("PATH="):
                pathvar = line.split("=", 1)[1]
                pathvarnum = i
            elif line.strip() == "export PATH" and pathvar:
                line = 'export PATH=' + pathvar
                pathvar = ''
                
            if line.split(" ")[0] in keywords:
                if pathvar:
                    flines.append([line, i, pathvarnum])
                else:
                    flines.append([line, i])
                    
                pathvar = ''
                
        if path == '/etc/paths' or path.startswith('/etc/paths.d/'):
            flines = [['export PATH=' + line.strip(), i] for i, line in enumerate(lines)]
            
        for line in flines:
            split = line[0].split(' ', 1)
            path_type = split[0]
            # name, value
            pts = split[1].split('=', 1)
            table.append([path_type, *pts])
            
    return flines, table

if 'path' not in st.session_state:
    st.session_state.path = edit_file

if 'lines' not in st.session_state or st.session_state.path != edit_file:
    st.session_state.path = edit_file
    lines, table  = get_lines(edit_file)
    st.session_state.lines = lines
    st.session_state.table = table


def delete_row(line):
    line = line[1:]
    
    # make the page reload the table and lines from the file
    del st.session_state.table
    del st.session_state.lines
    # delete from file
    with open(edit_file, 'r') as file:
        lines = file.readlines()
        for ind in line:
            lines[ind] = '# ' + lines[ind]
        
    with open(edit_file, 'w') as file:
        file.write(''.join(lines))

def edit_row(line, new_line):
    if edit_file == '/etc/paths' or edit_file.startswith('/etc/paths.d/'):
        new_line = new_line.split('=', 1)[1]
    
    line = line[1:]
    
    # make the page reload the table and lines from the file
    del st.session_state.table
    del st.session_state.lines
    
    # read file and edit line
    with open(edit_file, 'r') as file:
        lines = file.readlines()
        # comment out PATH=... preceding an export command, since it'll be replaced
        if len(line) > 1:
            for i in range(len(line) - 1):
                lines[line[i]] = '# ' + lines[line[i]]
        # preserve indenting
        ind = line[-1]
        str_line = lines[ind]
        whitespace = str_line[:len(str_line) - len(str_line.lstrip())]
        lines[ind] = whitespace + new_line + '\n'
        
    with open(edit_file, 'w') as file:
        file.write(''.join(lines))

lines, table = st.session_state.lines, st.session_state.table

st.text("Exports")
exports = st.container()
st.button("Add New Export", key="add_exp")

st.text("Aliases")
aliases = st.container()
st.button("Add New Alias", key="add_a")

st.text("Sources")
sources = st.container()
st.button("Add New Source", key="add_s")

def make_del_btn(col, name, line):
    return col.button('Delete', key=name, on_click=lambda: delete_row(line))

def make_edit_checkbox(col, name: str, inputs: list[str], template_str: str, line: list) -> bool:
    '''
    Makes an edit checkbox, with a save and cancel button when editing.
    Returns:
    False if not editing
    True if editing
    '''
    edit_container = col.container()
    
    edit_key = name + '_editing'
    if edit_key not in st.session_state:
        st.session_state[edit_key] = False
    editing = st.session_state[edit_key]
    
    def set_editing():
        st.session_state[edit_key] = not st.session_state[edit_key]
        
    edit_container.button('Cancel' if editing else 'Edit', key=name, on_click=set_editing)
    
    if editing:
        save = edit_container.button('Save', key=name+'_save')
        if save:
            edit_row(line, template_str.format(*inputs))
            set_editing()
            st.experimental_rerun()
    
    return editing

def make_row(container, container_name, parts: list[str], line_num, save_template: str):
    column_sizes = ([ 5/len(parts) ] * len(parts)) + [1, 1]
    cols = container.columns(column_sizes)
    
    inputs = []
    for i in range(len(parts)):
        text_name = f'{container_name}_{line_num}_{i}'
        if text_name in st.session_state:
            inputs.append(st.session_state[text_name])
        else:
            inputs.append("")
    
    make_del_btn(cols[-1], f'del_{container_name}_{line_num}', lines[line_num])
    
    editing = make_edit_checkbox(cols[-2], f'edit_{container_name}_{line_num}', inputs, save_template, lines[line_num])
    
    for i in range(len(parts)):
        text_name = f'{container_name}_{line_num}_{i}'
        if editing:
            cols[i].text_input("Edit", value=parts[i], key=text_name)
        else:
            cols[i].text(parts[i])

for i in range(len(table)):
    row = table[i]
    if row[0] == 'export':
        make_row(exports, 'exp', row[2:], i, 'export PATH={}')
        
    elif row[0] == 'alias':
        make_row(aliases, 'a', row[1:], i, 'alias {}={}')
            
    elif row[0] == '.':
        make_row(sources, 's', row[1:], i, '. {}')
        