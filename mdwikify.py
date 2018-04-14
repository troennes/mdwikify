#!/usr/bin/env python3

"""Create a local wiki from your Markdown files with one click.

This script downloads and automatically configures MDwiki, a CMS/Wiki
system that can run locally in a normal browser. It auto-configures a
navigation panel, config and index files. 

See http://www.mdwiki.info for info and documentation.

Dependencies: none

Todo:
    - add update mode on indexes
    - add support for nested lists in navigation panel (level 2)
    - add error msg for failing downloads
"""
__all__ = []
__version__ = '0.8'
__author__ = 'Kim Trønnes'

import os
import urllib.request
import shutil
import zipfile

# Default settings - change these as required
wiki_title = 'My Wiki'
default_theme = 'bootstrap'
mdwiki_filenames = ['mdwiki.html', 'mdwiki-slim.html', 'mdwiki-debug.html',
    'index.html', wiki_title+'.html']
included_md_files = ['README.md', 'navigation.md','index.md']
url = 'https://github.com/Dynalon/mdwiki/releases/download/0.6.2/mdwiki-0.6.2.zip'

banner = """
    __  _______ _       ___ __   _ ____     
   /  |/  / __ \ |     / (_) /__(_) __/_  __
  / /|_/ / / / / | /| / / / //_/ / /_/ / / /
 / /  / / /_/ /| |/ |/ / / ,< / / __/ /_/ / 
/_/  /_/_____/ |__/|__/_/_/|_/_/_/  \__, /  
                                   /____/
""" # ascii-art generated from http://www.patorjk.com/software/taag/

def create_config(title=None):
    """Create necessary file config.json"""
    if title is None:
        title = wiki_title
    cfg = """{
    "useSideMenu": true,
    "lineBreaks": "gfm",
    "additionalFooterText": "",
    "anchorCharacter": "&#x2693;",
    """
    with open('config.json','w', encoding='utf8') as f:
        f.write(cfg)
        f.write('"title": "'+title+'"\n}')

def create_index(path, title=None, ignore=None):
    """Create index.md based on listed directories and files in dir.

    Separates pages (files) and categories (directories)
    Optionally omit listing files in ignore list
    """
    if title is None:
        title = titlify(path)
    if ignore is None:
        ignore = []
    dirlist = []
    filelist = []
    for f in os.listdir(path):
        filepath = os.path.join(path,f)
        if os.path.isdir(filepath) and is_md_dir(filepath, recursive=True) and f not in ignore:
            dirlist.append(f)
        if is_md_file(filepath) and f not in ignore:
            filelist.append(f)    
    with open(os.path.join(path,'index.md'), 'w', encoding='utf8') as fd:
        fd.write('# '+title+'\n\n')
        if dirlist:
            if filelist:
                fd.write('## Categories\n\n')
            dirlist.sort()
            for d in dirlist:
                fd.write('- ['+titlify(d)+']('+d+'/index.md)\n')
        if dirlist and filelist:
            fd.write('\n## Pages\n\n')
        if filelist:
            filelist.sort()
            for f in filelist:
                base = os.path.basename(f)
                ftitle = titlify(os.path.splitext(base)[0])            
                fd.write('- ['+ftitle+']('+f+')\n')

def create_navigation(navlist, title=None, theme=None):
    """Create necessary file navigation.md"""
    if title is None:
        title = wiki_title
    if theme is None:
        theme = default_theme
    with open('navigation.md', 'w', encoding='utf8') as f:
        f.write('# '+title+'\n\n')
        for item in navlist:
            f.write(item+'\n')
        f.write('\n[gimmick:Theme (inverse: false)]('+theme+')\n')
        f.write('[gimmick:ThemeChooser](Change theme)')
    
def is_md_file(path):
    # Todo: Add more supported markdown file endings.
    # Todo: Check if file is ascii/txt
    return os.path.isfile(path) and path.endswith('.md')

def is_md_dir(path, recursive=False):
    """True if folder includes at least one .md-file. 
    Recursive flag: searches subfolders and returns True at least one .md-file is found
    """
    assert os.path.isdir(path), 'input is not a directory'
    if recursive:
        for root, dirs, files in os.walk(path):
            for f in files:
                if is_md_file(os.path.join(root,f)):
                    return True
    else:
        for f in os.listdir(path):
            if is_md_file(os.path.join(path,f)):
                return True
    return False

def input_bool(question):
    negative = ['n','0','f']
    # positive is everything else, even blank
    while True:
        try:
            s = input(question + ' [Y/n] >>> ')
        except Exception as e:
            print('Error: '+e)
        if not s:
            return True
        s = s[0].lower()
        return (s not in negative)

def input_string(question):
    while True:
        try:
            s = input(question + ' >>> ')
        except Exception as e:
            print('Error: '+e)
        else:
            return s

def download(url, filename):
    """Download file from URL. Save as filename"""
    try:
        response = urllib.request.urlopen(url)
        with urllib.request.urlopen(url, timeout=10) as response, open(filename, 'wb') as outFile:
            shutil.copyfileobj(response, outFile)
    except Exception as e:
        print(e)

def list_md_files(dir, ignore=None):
    # Todo: Pass ignored files as argument
    if ignore is None:
        ignore = included_md_files + mdwiki_filenames
    files = os.listdir(dir)
    mdfiles = []
    for f in files:
        if is_md_file(f) and f not in ignore:
            mdfiles.append(f)
    return mdfiles

def titlify(dir):
    """Make title from file/dir name"""
    return dir.title().replace('_',' ')

def infoprint(msg):
    # Todo: add if verbose, then print
    print('[Info] '+msg)
         

def main(): 
    print(banner)

    # Check if mdwiki html files exists
    mdwikiExists = False   
    for f in mdwiki_filenames:
        if os.path.isfile(f):
            mdwikiExists = True
    if not mdwikiExists:
        zipName = 'mdwiki.zip'       
        if not os.path.isfile(zipName):
            print('Warning: MDWiki html file not found. Fetching files from repository...')
            download(url,zipName)

        # Unzip files from Github. Ends up in 'tmp/mdwiki-[version]/mdwiki.html'
        with zipfile.ZipFile(zipName,'r') as z:
            z.extractall('tmp')      
        unzippedDir = os.listdir('tmp')[0]        
        assert isinstance(unzippedDir,str), 'Unexpected file type in folder tmp'
        shutil.move(os.path.join('tmp',unzippedDir,'mdwiki.html'),'index.html')

        # Delete leftover files
        shutil.rmtree('tmp')
        os.remove(zipName)

    # Check if index.md exists
    if not os.path.isfile('index.md'):
        infoprint('Creating root index file.')
        create_index('.',wiki_title, included_md_files)

    # Check if config.json exists
    if not os.path.isfile('config.json'):
        infoprint('Creating default config file. Please review settings.')
        create_config()
    
    # Create navigation file
    if not os.path.isfile('navigation.md'):
        writeBuffer = []
        for root, alldirs, files in os.walk('.'):
            for d in alldirs:                
                dirpath = os.path.join(root,d)
                if not is_md_dir(dirpath, recursive=True):
                    # ignore all folders without md files
                    continue
                depth = len(dirpath.split(os.sep))-1
                title = titlify(d)
                dirfiles = os.listdir(dirpath)

                # For all dirs in root folder, ask to add to nav panel
                if depth == 1:
                    if input_bool('Add directory '+d+' as Menu item in Nav panel?'):
                        # if not input_bool('Is name "'+title+'" OK?'):
                        #    title = input_string('Enter name')
                        writeBuffer.append('['+title+']('+d+'/index.md)')
                        # if input_bool('Add directories in '+d+' to Nav panel as drop down?'):
                        #    level2List.append(d)
                        #    # Store the level 1 dir that wants level 2 dirs as drop down in list

                # Create index.md after depth checks to include user defined titles
                if not os.path.isfile(os.path.join(root,d,'index.md')):
                    infoprint('Creating index file in '+d)
                    create_index(dirpath, title) # Todo: add ignored files 

                # Todo: Check if writebuffer is sorted for directories            
                
                # Todo: Add logic for adding level 2 directories to Nav panel
                # if depth == 2 and parent(d) in level2List: # use split(os.sep) to find parent

        rootFiles = list_md_files('.') # Check if ignored files are added
        for f in rootFiles:
            if input_bool('Add '+f+' as Link in Nav panel?'):
                title = os.path.splitext(f)[0].title()
                if not input_bool('Is name "'+title+'" OK?'):
                    title = input_string('Enter name')
                writeBuffer.append('['+title+']('+f+')')
        infoprint('Creating navigation file.')
        create_navigation(writeBuffer)  

if __name__ == '__main__':
	main()