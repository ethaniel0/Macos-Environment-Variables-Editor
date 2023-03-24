import streamlit as st
from pathlib import Path
import os

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

edit_file = st.selectbox('Edit files', paths)

def get_lines(path: str):
    path = str(path)
    table = []
    if 'zsh' in os.environ.get("SHELL", ""):
        with open(path, 'r') as file:
            lines = [l.strip() for l in file.readlines()]
            flines = []
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
    del st.session_state.table
    del st.session_state.lines
    # delete from file
    with open(edit_file, 'r') as file:
        lines = file.readlines()
        for ind in line:
            lines[ind] = '# ' + lines[ind]
        
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

def make_edit_checkbox(col, name):
    edit_container = col.container()
    edit_checkbox = edit_container.checkbox('Edit', key=name)
    
    if edit_checkbox:
        edit_container.button('Save', key=name+'_save')
        edit_container.button('Cancel', key=name+'_cancel')
        
    return edit_checkbox

for i in range(len(table)):
    row = table[i]
    if row[0] == 'export':
        cols = exports.columns([5, 1, 1])
        
        editing = make_edit_checkbox(cols[1], f'edit_exp_{i}')
        make_del_btn(cols[2], f'del_exp_{i}', lines[i])
        
        if editing:
            cols[0].text_input("", value=row[2])
        else:
            cols[0].text(row[2])
        
        
    elif row[0] == 'alias':
        cols = aliases.columns([2.5, 2.5, 1, 1])
        
        editing = make_edit_checkbox(cols[2], f'edit_a_{i}')
        make_del_btn(cols[3], f'del_a_{i}', lines[i])
        
        
        if editing:
            cols[0].text_input("", value=row[1])
            cols[1].text_input("", value=row[2])
        else:
            cols[0].text(row[1])
            cols[1].text(row[2])
            
    
    elif row[0] == '.':
        cols = sources.columns([5, 1, 1])
        
        editing = make_edit_checkbox(cols[1], f'edit_s_{i}')
        make_del_btn(cols[2], f'del_s_{i}', lines[i])
        
        if editing:
            cols[0].text_input("", value=row[1])
        else:
            cols[0].text(row[1])
