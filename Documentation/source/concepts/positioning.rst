.. highlight:: python

***********
Positioning
***********

Positioning objects on screen is the whole point of vanilla. This document explains the models, syntax and more. First, some terminology:

**view**
    Almost every object in vanilla represents a "view." A view is something that appears on screen: a button, a text editor, an image container, a slider, etc.

**superview**
    Every view is positioned within a "superview." If the superview moves, the view moves.

**subview**
    A view added to another view is a "subview."

**window**
    Windows contain a special superview that is positioned edge to edge of the non-title bar area of the window.

There are two ways to position views in vanilla:

**Specifying numerical coordinates.**
    This model, named "frame layout", allows you to specify the x and y coordinates and the width and height of views. These values manually adust the frame of the view within the superview. This model offers the most control, but can be cumbersome and the precision makes it difficult to revise complex interface layouts.

**Specifying relative positions.**
    This model, known as "auto layout", allows you to describe where controls should be positioned relative to the superview and other views. This model is more verbose, but it is (typically) faster to implement both simple and complex interafces and it makes revisions significantly easier in complex interface layouts.

These models can be mixed and matched within an interface and even within a single superview.

The model that you want to use for positioning a view is indicated with the first argument, named ``posSize``, when constructing the view. To indicate that you want to use frame layout, you give a tuple of numbers. To indicate that you want to use auto layout, you use the string ``"auto"`` and provide rules in a method of the view object. ::

    w.button1((10, 10, 100, 20), "Frame Layout")
    w.button2("auto", "Auto Layout")

============
Frame Layout
============

Frame layout is specified with a tuple of four numbers:

1. x position within the superview
2. y position within the superview
3. width
4. height

The ``(0, 0)`` coordinate is the top left corner of the superview.

Positions relative to the bottom or right of the superview are indicated with negative numbers or zero for the x, y, width and/or height. For example, ``(-100, 20, 0, 20)`` indicates that the x position is 100 units from the right and the width should align with the right.

--------
Examples
--------

**Basic window**::

    w = vanilla.Window((200, 200), minSize=(100, 100))
    w.editor = vanilla.TextEditor((15, 15, -15, -43), "Hello World!")
    w.button = vanilla.Button((15, -35, -15, 20), "Done")
    w.open()

===========
Auto Layout
===========

Auto layout is specified with a series of rules that are added after all subviews have been added to the superview. Auto layout is incredibly powerful, but incredibly complex. The information below is written to cover the interface layouts that are typically created with vanilla. For complete information, read Apple's `Auto Layout Guide`_ and documentation on `NSLayoutConstraint`_.

.. _Auto Layout Guide: https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/AutolayoutPG/index.html#//apple_ref/doc/uid/TP40010853-CH7-SW1
.. _NSLayoutConstraint: https://developer.apple.com/documentation/uikit/nslayoutconstraint?language=objc

-----
Rules
-----

Auto layout rules specify the relation of one view to another. These rules are added with the superview's ``addAutoPosSizeRules`` method after the views themselves have been added to the superview. ::

    w = vanilla.Window((200, 200))
    w.button1 = vanilla.Button("auto", "Button 1")
    w.button2 = vanilla.Button("auto", "Button 2")
    rules = [
        # see below for documentation
    ]
    w.addAutoPosSizeRules(rules)

Rules can be defined as strings formatted in Apple's `Visual Format Language`_ or they can be defined as dictionaries with key/value pairs defining view relationships. The dictionary rule form is for advanced edge cases and is defined in detail in the ``addAutoPosSizeRules`` method documentation. Most interface can be specified with the string rule form, so that form is used for all of the examples that follow.

An optional ``metrics`` dictionary can be passed to the ``addAutoPosSizeRules`` method. These allow the string rules to reference constant values, such as spacing values or control sizes, by name. Examples of this are below.

.. _Visual Format Language: https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/AutolayoutPG/VisualFormatLanguage.html#//apple_ref/doc/uid/TP40010853-CH27-SW1

String Rules
^^^^^^^^^^^^

**Orientations**

+--------+--------------------+
| ``H:`` | A horizontal rule. |
+--------+--------------------+
| ``V:`` | A vertical rule.   |
+--------+--------------------+

**View References**

+------------+-----------------------------------------------------------------+
| ``|``      | Edge of the superview.                                          |
+------------+-----------------------------------------------------------------+
| ``[name]`` | An attribute name you used to assign the view to the superview. |
+------------+-----------------------------------------------------------------+

**Relations**

+--------+------------------------+
| ``==`` | Equal.                 |
+--------+------------------------+
| ``>=`` | Greater than or equal. |
+--------+------------------------+
| ``<=`` | Less than or equal.    |
+--------+------------------------+

**Metrics**

+-----------------------+---------------------------------------------+
| ``-``                 | Standard space.                             |
+-----------------------+---------------------------------------------+
| number (int or float) | A specific number of points.                |
+-----------------------+---------------------------------------------+
| metric name (string)  | A metric defined in the metrics dictionary. |
+-----------------------+---------------------------------------------+

--------
Examples
--------

The following examples use this code, replacing the ``rules`` and ``metrics`` as indicated. ::

    w = vanilla.Window((200, 200), minSize=(100, 100))
    w.button = vanilla.Button("auto", "Hello")
    rules = []
    metrics = {}
    w.addAutoPosSizeRules(rules, metrics)
    w.open()

This code will add a button to a window, but it doesn't say anything about where the button should be placed or how big it should be.

Place the button with no space around it::

    rules = [
        "|[button]|"
    ]

Place the button with standard space around it::

    rules = [
        "|-[button]-|"
    ]

Place the button with specific space around it::

    rules = [
        "|-50-[button]-20-|"
    ]

Place the button with a metric defined space around it::

    rules = [
        "|-padding-[button]-padding-|"
    ]
    metrics = {
        "padding" : 33
    }

In each of these, the width of the button has been flexible. Define a specific width::

    rules = [
        "|-[button(75)]-|"
    ]

Define a minimum width::

    rules = [
        "|-[button(>=75)]-|"
    ]

Define a maximum width::

    rules = [
        "|-[button(<=100)]-|"
    ]

Define minimum and maximum widths::

    rules = [
        "|-[button(>=75,<=200)]-|"
    ]

The previous examples all specified horizontal rules. To indicate the direction of a rule, start the rule with ``H:`` for horizontal and ``V:`` for vertical. If an orientation isn't specified, as in the examples above, the orientation will be horizontal. ::

    rules = [
        # Horizontal
        "H:|-[button]-|",
        # Vertical
        "V:|-[button]-|"
    ]

All of the options shown for specifying values in horizontal orientation also work for specifying values in vertical orientation.

That covers the basics of placing one view in a superview. Placing multiple views uses the same syntax. The following examples use this code, replacing ``rules`` and ``metrics`` as indicated. ::

    w = vanilla.Window((200, 200), minSize=(100, 100))
    w.button1 = vanilla.Button("auto", "Hello")
    w.button2 = vanilla.Button("auto", "World")
    rules = []
    metrics = {}
    w.addAutoPosSizeRules(rules, metrics)
    w.open()

Place the buttons next to each other::

    rules = [
        # Horizontal
        "H:|-[button1]-[button2]-|",
        # Vertical
        "V:|-[button1]-|",
        "V:|-[button2]-|"
    ]

Place the buttons on top of each other::

    rules = [
        # Horizontal
        "H:|-[button1]-|",
        "H:|-[button2]-|",
        # Vertical
        "V:|-[button1]-[button2]-|",
    ]

Views can be referenced by other views within rules. To make the buttons have the same width::

    rules = [
        # Horizontal
        "H:|-[button1]-[button2(==button1)]-|",
        # Vertical
        "V:|-[button1]-|",
        "V:|-[button2]-|"
    ]

**Basic window**::

    w = vanilla.Window((200, 200), minSize=(100, 100))
    w.editor = vanilla.TextEditor("auto", "Hello World!")
    w.button = vanilla.Button("auto", "Done")
    rules = [
        # Horizontal
        "H:|-border-[editor]-border-|",
        "H:|-border-[button]-border-|",
        # Vertical
        "V:|-border-[editor(>=100)]-space-[button]-border-|"
    ]
    metrics = {
        "border" : 15,
        "space" : 8
    }
    w.addAutoPosSizeRules(rules, metrics)
    w.open()

**Stack of views, all with the same width**::

    w = vanilla.Window((200, 200), minSize=(100, 100))
    w.button1 = vanilla.Button("auto", "Button 1")
    w.button2 = vanilla.Button("auto", "Button 2")
    w.editor = vanilla.TextEditor("auto", "Hello World!")
    w.button3 = vanilla.Button("auto", "Button 3")
    w.button4 = vanilla.Button("auto", "Button 4")
    rules = [
        # Horizontal
        "H:|-border-[button1]-border-|",
        "H:|-border-[button2]-border-|",
        "H:|-border-[editor]-border-|",
        "H:|-border-[button3]-border-|",
        "H:|-border-[button4]-border-|",
        # Vertical
        "V:|-border-[button1]-space-[button2]-space-[editor(>=100)]-space-[button3]-space-[button4]-border-|"
    ]
    metrics = {
        "border" : 15,
        "space" : 8
    }
    w.addAutoPosSizeRules(rules, metrics)
    w.open()

**Stack of views, with different widths**::

    w = vanilla.Window((200, 200), minSize=(100, 100))
    w.button1 = vanilla.Button("auto", "Button 1")
    w.button2 = vanilla.Button("auto", "Button 2")
    w.button3 = vanilla.Button("auto", "Button 3")
    w.button4 = vanilla.Button("auto", "Button 4")
    rules = [
        # Horizontal
        "H:|-border-[button1]-border-|",
        "H:|-border-[button2]-space-[button3(==button2)]-border-|",
        "H:|-border-[button4]-border-|",
        # Vertical
        "V:|-border-[button1]-space-[button2]-space-[button4]-border-|",
        "V:|-border-[button1]-space-[button3]-space-[button4]-border-|"
    ]
    metrics = {
        "border" : 15,
        "space" : 8
    }
    w.addAutoPosSizeRules(rules, metrics)
    w.open()

**Flexible views**::

    w = vanilla.Window((200, 200), minSize=(100, 100))
    w.editor1 = vanilla.TextEditor("auto", "Hello World!")
    w.editor2 = vanilla.TextEditor("auto", "Hello World!")
    w.editor3 = vanilla.TextEditor("auto", "Hello World!")
    w.editor4 = vanilla.TextEditor("auto", "Hello World!")
    rules = [
        # Horizontal
        "H:|-border-[editor1]-space-[editor2(==editor1)]-border-|",
        "H:|-border-[editor3]-space-[editor4(==editor3)]-border-|",
        # Vertical
        "V:|-border-[editor1]-space-[editor3(==editor1)]-border-|",
        "V:|-border-[editor2]-space-[editor4(==editor2)]-border-|",
    ]
    metrics = {
        "border" : 15,
        "space" : 8
    }
    w.addAutoPosSizeRules(rules, metrics)
    w.open()

**Flexible spaces**::

    w = vanilla.Window((200, 200), minSize=(100, 100))
    w.flex1 = vanilla.Group("auto")
    w.flex2 = vanilla.Group("auto")
    w.flex3 = vanilla.Group("auto")
    w.button1 = vanilla.Button("auto", "Button 1")
    w.button2 = vanilla.Button("auto", "Button 2")
    w.button3 = vanilla.Button("auto", "Button 3")
    rules = [
        # Horizontal
        "H:|-[flex1(>=border)]-[button1]-[flex2(==flex1)]-|",
        "H:|-border-[button2(==100)]-[flex3(>=space)]-[button3(==button2)]-border-|",
        # Vertical
        "V:|-border-[button1]-space-[button2]-border-|",
        "V:|-border-[button1]-space-[button3]-border-|",
    ]
    metrics = {
        "border" : 15,
        "space" : 8
    }
    w.addAutoPosSizeRules(rules, metrics)
    w.open()

**Nested views**::

    w = vanilla.Window((200, 200), minSize=(100, 100))
    w.editor1 = vanilla.TextEditor("auto", "Hello World!")
    w.editor2 = vanilla.TextEditor("auto", "Hello World!")
    w.nest = vanilla.Group("auto")
    w.nest.editor = vanilla.TextEditor("auto", "Hello World!")
    w.nest.button = vanilla.Button("auto", "Button")
    windowRules = [
        # Horizontal
        "H:|-border-[editor1(>=100)]-space-[editor2(==editor1)]-space-[nest(==100)]-border-|",
        # Vertical
        "V:|-border-[editor1]-border-|",
        "V:|-border-[editor2]-border-|",
        "V:|-border-[nest]-border-|"
    ]
    nestRules = [
        # Horizontal
        "H:|[editor]|",
        "H:|[button]|",
        # Vertical
        "V:|[editor]-space-[button]|"
    ]
    metrics = {
        "border" : 15,
        "space" : 8
    }
    w.addAutoPosSizeRules(windowRules, metrics)
    w.nest.addAutoPosSizeRules(nestRules, metrics)
    w.open()

**Table of views**:

.. todo::
    - need to finish ``GridGroup`` for this
    - https://github.com/typemytype/batchRoboFontExtension (ttfautohint section)
