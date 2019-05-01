.. highlight:: python

***********
Positioning
***********

----------------
View Terminology
----------------

- view
- superview
- subview
- window

------
Models
------

- "auto"
- (x, y, w, h)
- these can be mixed in same view

================================
Automatic Positioning and Sizing
================================

- "auto"
- this is incredibly powerful, but can be very complex.
- This is not a full documentation of all the options. This is targeted at the basic kinds of layouts vanilla is typically used for. Refer to Apple's documentation for that.
- https://developer.apple.com/documentation/uikit/nslayoutconstraint?language=objc
- https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/AutolayoutPG/index.html#//apple_ref/doc/uid/TP40010853-CH7-SW1
- there are often > 1 ways to accomplish a single layout.

-----
Rules
-----

- Rules specify relationships to other views.
- Add rules to superview with superview.addAutoPosSizeRules.
- Many controls have a preset height or width, so you don't need to specify these.
- Rules are defined as:
-- string
-- dict
- In strings, there can be metrics.
-- metrics


String Syntax
^^^^^^^^^^^^^

**Orientations**

====== ==================
``H:`` A horizontal rule.
``V:`` A vertical rule.
====== ==================

**View References**

========== ===============================================================
``| ``     Edge of the superview.
``[name]`` An attribute name you used to assign the view to the superview.
========== ===============================================================

**Relations**

====== ======================
``==`` Equal.
``>=`` Greater than or equal.
``<=`` Less than or equal.
====== ======================

**Metrics**

===================== ===========================================
``-``                 Standard space.
number (int or float) A specific number of points.
metric name (string)  A metric defined in the metrics dictionary.
===================== ===========================================

Examples

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

The previous examples all specified horizontal rules. To indicate the direction of a rule, start the rule with ``H:`` for horizontal and ``V:`` for vertical. If an orientation isn't specied, as in the examples above, the orientation will be horizontal.

	rules = [
		# Horizontal
		"H:|-[button]-|",
		# Vertical
		"V:|-[button]-|"
	]

All of the options shown for specifying values in horizontal orientation also work for specifying values in vertical orientation.

That covers the basics of placing one view in a superview. Placing multiple views uses the same syntax. The following examples use this code, replacing ``rules`` and ``metrics`` as indicated.

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

Examples
""""""""

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

**Table of views**::

- need to finish GridGroup for this.
- https://github.com/typemytype/batchRoboFontExtension (ttfautohint section)


==================================
Frame Based Positioning and Sizing
==================================

- (0, 0) location
- (l, t, w, b)
- negative value meaning for w, h
- simple examples