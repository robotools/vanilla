import os
from types import FunctionType
import inspect
import shutil
import glob
import re
from AppKit import NSObject
import vanilla
import textile
from xmlWriter import XMLWriter

sourceDirectory = os.path.join(os.path.dirname(__file__), 'source')
sourceImagesDirectory = os.path.join(sourceDirectory, 'images')
compiledDirectory = os.path.join(os.path.dirname(__file__), 'compiled')
compiledImagesDirectory = os.path.join(compiledDirectory, 'images')

_allSortedObjectNames = dir(vanilla)
# filter down to only public class names
_allSortedObjectNames = [i for i in _allSortedObjectNames
            if 'Base' not in i
            and not i.startswith('_')
            and i[0].upper() == i[0]
            and i != 'VanillaError']
_allSortedObjectNames.sort()
_sortedObjectNames = [i for i in _allSortedObjectNames
            if not i.endswith('ListCell')]
_sortedObjectNames += [i for i in _allSortedObjectNames
            if i.endswith('ListCell')]

def addHead(writer):
    writer.begintag('head')
    writer.newline()
    writer.simpletag('link', href="default.css", type="text/css", rel="stylesheet")
    writer.newline()
    writer.endtag('head')
    writer.newline()
    
_navigationSections = [
    'About',
    'Download',
    'Documentation',
    'Object Reference',
    'Examples'
    ]

_navigationSubsections = {
    'Documentation' : [],
    'Object Reference' : _sortedObjectNames,
    'Examples' : []
    }

def addNavigation(writer, currentSection=None, currentSubsection=None):
    writer.begintag('div', __class='nav')
    writer.newline()
    # add the top of the shell
    writer.simpletag('img', src='images/nav_shell_top.png')
    writer.newline()
    # add the sections
    writer.begintag('ul', __class='nav_ul')
    writer.newline()
    alternateRowColor = False
    for section in _navigationSections:
        if section == currentSection and currentSubsection is None:
            if section in _navigationSubsections:
                writer.begintag('li', __class='nav_li_section_sub_sel')
            else:
                writer.begintag('li', __class='nav_li_section_sel')
            writer.write(section)
        else:
            cssClass = 'nav_li_section'
            if alternateRowColor:
                cssClass += '_alt'
            if section in _navigationSubsections:
                if currentSection == section:
                    cssClass += '_sub_on'
                else:
                    cssClass += '_sub_off'
            writer.begintag('li', __class=cssClass)
            htmlName = section.replace(' ', '')
            if htmlName == 'About':
                htmlName = 'index'
            htmlName = '%s.html' % htmlName
            writer.begintag('a', href=htmlName, __class='nav_a')
            writer.write(section)
            writer.endtag('a')
        writer.endtag('li')
        writer.newline()
        alternateRowColor = not alternateRowColor
        if currentSection == section:
            for subsection in _navigationSubsections.get(section, []):
                if subsection == currentSubsection:
                    writer.begintag('li', __class='nav_li_subsection_sel')
                    writer.write(subsection)
                else:
                    if alternateRowColor:
                        writer.begintag('li', __class='nav_li_subsection_alt')
                    else:
                        writer.begintag('li', __class='nav_li_subsection')
                    htmlName = '%s_%s.html' % (section.replace(' ', ''), subsection)
                    writer.begintag('a', href=htmlName, __class='nav_a')
                    writer.write(subsection)
                    writer.endtag('a')
                writer.endtag('li')
                writer.newline()
                alternateRowColor = not alternateRowColor
    writer.endtag('ul')
    writer.newline()
    # add the bottom of the shell
    writer.simpletag('img', src='images/nav_shell_bottom.png')
    writer.newline()
    writer.endtag('div')
    writer.newline()

def _lstrip(docString):
    lines = docString.expandtabs().splitlines()
    if len(lines) < 2:
        return docString
    allWhitespace = []
    for line in lines[1:]:
        if not line.strip():
            continue
        whitespace = line[:-len(line.lstrip())]
        allWhitespace.append(whitespace)
    minWhitespace = min(allWhitespace)
    minCount = len(minWhitespace)
    strippedLines = []
    for line in lines:
        if line.startswith(minWhitespace):
            line = line[minCount:]
        strippedLines.append(line)
    return '\n'.join(strippedLines)

def extractMethodDoc(func, className):
    funcName = func.__name__
    if hasattr(func, 'callable'):
        # hack around objc
        func = func.callable
    # extract the arguments and the values
    arg_names, extra_args, extra_kwds, arg_defaults = inspect.getargspec(func)
    # work the defaults and arg names together
    if arg_defaults:
        args = arg_names[:-len(arg_defaults)]
        for name, value in zip(arg_names[-len(arg_defaults):], arg_defaults):
            if isinstance(value, str):
                value = '&#34;%s&#34;' % value
            else:
                value = str(value)
            argString = '%s=_(objRef_argument_defaults)%s_' % (name, value)
            args.append(argString)
    else:
        args = arg_names
    if 'self' in args:
        args.remove('self')
    docString = inspect.getdoc(func)
    if docString is None:
        docString = ''
    docString = _lstrip(docString)
    # use the class name if the method name is __init__
    if funcName == '__init__':
        funcName = className
    # compile the full doc
    if args:
        doc = 'h5. <a name="%s">*%s*</a><em class="objRef_arguments">(%s)</em>\n\n%s' % (funcName, funcName, ', '.join(args), docString)
    else:
        doc = 'h5. <a name="%s">*%s*</a>_(objRef_arguments)()_\n\n%s' % (funcName, funcName, docString)
    doc = textile.textile(doc)
    # convert it to html and return it
    return funcName, doc


# methods that do not need to be documented.
methodFilter = [
    ('Box', 'enable'),
    
    ('Button', 'get'),
    ('Button', 'set'),
    ('Button', 'toggle'),
    
    ('ComboBox', 'bind'),
    ('ComboBox', 'getTitle'),
    ('ComboBox', 'setTitle'),

    ('Drawer', 'enable'),
    ('Drawer', 'move'),
    ('Drawer', 'show'),
    ('Drawer', 'getPosSize'),
    ('Drawer', 'setPosSize'),
    ('Drawer', 'resize'),
    
    ('EditText', 'getTitle'),
    ('EditText', 'setTitle'),
    
    ('Group', 'enable'),
    
    ('HelpButton', 'get'),
    ('HelpButton', 'getTitle'),
    ('HelpButton', 'set'),
    ('HelpButton', 'setTitle'),
    
    ('HorizontalLine', 'enable'),
    
    ('ImageButton', 'get'),
    ('ImageButton', 'set'),
    ('ImageButton', 'toggle'),
    
    ('LevelIndicator', 'bind'),
    
    ('List', 'append'),
    ('List', 'remove'),
    ('List', 'index'),
    ('List', 'insert'),
    ('List', 'extend'),
    
    ('PopUpButton', 'bind'),
    ('PopUpButton', 'getTitle'),
    ('PopUpButton', 'setTitle'),
    ('PopUpButton', 'toggle'),
    
    ('ProgressBar', 'enable'),
    
    ('ProgressSpinner', 'enable'),
    
    ('RadioGroup', 'bind'),
    ('RadioGroup', 'getTitle'),
    ('RadioGroup', 'setTitle'),
    
    ('ScrollView', 'enable'),
    
    ('SearchBox', 'bind'),
    ('SearchBox', 'getTitle'),
    ('SearchBox', 'setTitle'),
    
    ('Sheet', 'center'),
    ('Sheet', 'move'),
    ('Sheet', 'getTitle'),
    ('Sheet', 'setTitle'),
    ('Sheet', 'addToolbar'),
    ('Sheet', 'hide'),
    ('Sheet', 'isVisible'),
    ('Sheet', 'show'),
    
    ('Slider', 'bind'),
    ('Slider', 'getTitle'),
    ('Slider', 'setTitle'),
    
    ('SplitView', 'enable'),
    
    ('SquareButton', 'get'),
    ('SquareButton', 'set'),
    ('SquareButton', 'toggle'),
    
    ('Tabs', 'enable'),
    
    ('TextBox', 'bind'),
    ('TextBox', 'enable'),
    ('TextBox', 'getTitle'),
    ('TextBox', 'setTitle'),
    
    ('VerticalLine', 'enable'),

    ('CheckBoxListCell', 'getNSCell'),
    ('LevelIndicatorListCell', 'getNSCell'),
    ('SliderListCell', 'getNSCell'),
    ]

def docObjects():

    for className in _sortedObjectNames:
        print '>', className
        # make the path for the html
        htmlPath = 'ObjectReference_%s.html' % className
        htmlPath = os.path.join(compiledDirectory, htmlPath)
        # start up the writer
        writer = XMLWriter(htmlPath, indentwhite='', encoding='utf-8')
        # start the html
        writer.begintag('html', xmlns="http://www.w3.org/1999/xhtml")
        writer.newline()
        # write the head
        addHead(writer)
        # start the body
        writer.begintag('body')
        writer.newline()
        # add the navigation
        addNavigation(writer, currentSection='Object Reference', currentSubsection=className)
        # start the body block
        writer.begintag('div', __class='bodyBlock')
        writer.newline()
        # load the class
        cls = getattr(vanilla, className)
        # the list cell controls are functions, not classes.
        # we need to know this later.
        isFunction = isinstance(cls, FunctionType)
        # add the class name
        writer.begintag('div', __class='objRef_nameBlock')
        writer.newline()
        writer.begintag('h3')
        writer.write(className)
        writer.endtag('h3')
        writer.newline()
        # class level documentation
        docString = cls.__doc__
        if docString and not isFunction:
            docString = _lstrip(docString)
            docString = textile.textile(docString)
            writer.writeraw(docString)
            writer.newline()
        writer.endtag('div')
        writer.newline()
        # force __init__ to doc
        writer.begintag('h4')
        writer.write('Constructor')
        writer.endtag('h4')
        writer.newline()
        writer.begintag('div', __class='objRef_initBlock')
        writer.newline()
        
        if isFunction:
            writer.writeraw(extractMethodDoc(cls, className)[1])
        else:
            writer.writeraw(extractMethodDoc(getattr(cls, '__init__'), className)[1])
        writer.newline()
        writer.endtag('div')
        writer.newline()
        # handle the methods
        # read all the methods and store the doc
        methods = {}
        for attr in dir(cls):
            # ignore oddities
            if attr in ['bundleForClass']:
                continue
            # ignore private attrs
            # and NSObject attrs
            if '_' in attr:
                continue
            # filter out NSWindow methods
            if className in ['Window', 'Sheet', 'FloatingWindow']:
                if hasattr(NSObject, attr):
                    continue
            # filter out methods that we don't need to doc
            if (className, attr) in methodFilter:
                continue
            # get the method name and formatted doc
            methodName, methodDoc = extractMethodDoc(getattr(cls, attr), className)
            methods[methodName] = methodDoc
        sortedMethods = methods.keys()
        sortedMethods.sort()
        if sortedMethods:
            writer.begintag('h4')
            writer.write('Methods')
            writer.endtag('h4')
            writer.newline()
            # write a list of methods
            writer.begintag('ul', __class="objRef_methodNames")
            writer.newline()
            for methodName in sortedMethods:
                writer.begintag('li')
                writer.begintag('a', href='#%s'%methodName, __class='objRef_methodNames_a')
                writer.write(methodName)
                writer.endtag('a')
                writer.endtag('li')
                writer.newline()
            writer.endtag('ul')
            writer.newline()
            # write the method block
            writer.begintag('div', __class='objRef_methodBlock')
            writer.newline()
            alternateColor = False
            for methodName in sortedMethods:
                methodDoc = methods[methodName]
                if not alternateColor:
                    writer.begintag('div', __class='objRef_methodItem1')
                else:
                    writer.begintag('div', __class='objRef_methodItem2')
                alternateColor = not alternateColor
                writer.newline()
                writer.writeraw(methodDoc)
                writer.newline()
                writer.endtag('div')
                writer.newline()
            writer.endtag('div')
            writer.newline()
        # close the body block
        writer.endtag('div')
        writer.newline()
        # close the body and the html
        writer.endtag('body')
        writer.newline()
        writer.endtag('html')
        writer.newline()
        writer.close()
        # replace the __class hacks
        f = open(htmlPath, 'rb')
        html = f.read()
        f.close()
        html = html.replace('__class', 'class')
        f = open(htmlPath, 'wb')
        f.write(html)
        f.close()

_fileName2SectionName = {
        'ObjectReference' : 'Object Reference'
        }

def textile2html(srcPath):
    f = open(srcPath, 'rb')
    text = f.read()
    f.close()
    #
    fileName = os.path.splitext(os.path.basename(srcPath))[0]
    htmlPath = os.path.join(compiledDirectory, fileName+'.html')
    #
    # start up the writer
    writer = XMLWriter(htmlPath, indentwhite='', encoding='utf-8')
    # start the html
    writer.begintag('html', xmlns="http://www.w3.org/1999/xhtml")
    writer.newline()
    # write the head
    addHead(writer)
    # start the body
    writer.begintag('body')
    writer.newline()
    # add the navigation
    currentSection = os.path.splitext(fileName)[0]
    if currentSection == 'index':
        currentSection = 'About'
    currentSection = _fileName2SectionName.get(currentSection, currentSection)
    addNavigation(writer, currentSection=currentSection)
    # start the body block
    writer.begintag('div', __class='bodyBlock')
    writer.newline()
    # add the textiled text
    textiledText = textile.textile(text, encoding='utf-8')
    writer.writeraw(textiledText)
    writer.newline()
    # close the body block
    writer.endtag('div')
    writer.newline()
    # close the body and the html
    writer.endtag('body')
    writer.newline()
    writer.endtag('html')
    writer.newline()
    writer.close()
    # replace the __class hacks
    f = open(htmlPath, 'rb')
    html = f.read()
    f.close()
    html = html.replace('__class', 'class')
    f = open(htmlPath, 'wb')
    f.write(html)
    f.close()


if os.path.exists(compiledDirectory):
#    raise NotImplementedError, 'directory already exists'
    shutil.rmtree(compiledDirectory)
os.mkdir(compiledDirectory)
os.mkdir(compiledImagesDirectory)

# copy the css
print 'copying style sheet...'
for srcPath in glob.glob(os.path.join(sourceDirectory, '*.css')):
    dstPath = os.path.join(compiledDirectory, os.path.basename(srcPath))
    shutil.copyfile(srcPath, dstPath)

# copy the images
print 'copying images...'
for srcPath in glob.glob(os.path.join(sourceImagesDirectory, '*.png')):
    dstPath = os.path.join(compiledImagesDirectory, os.path.basename(srcPath))
    shutil.copyfile(srcPath, dstPath)

# create the html for the textile documents
print 'generating html for textile pages...'
for srcPath in glob.glob(os.path.join(sourceDirectory, '*.textile')):
    textile2html(srcPath)

# document the objects
print 'generating html for object reference...'
docObjects()

