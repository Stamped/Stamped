# Makefile
# 
#     Contains dependency logic for preprocessing and optimizing resources 
# used by the main Stamped website. Also contains logic for collecting and 
# deploying assets to our cloud infrastructure (e.g., dev and prod).
# 
# @author:    Travis Fischer (travis@stamped.com)
# @copyright: (c) 2011-2012 Stamped.com

override PROJECT_BASE_DIR	= .
override PROJECT_BASE_LIB	= $(PROJECT_BASE_DIR)/.make

# Sanity-check PROJECT_BASE_DIR and PROJECT_BASE_LIB
$(if $(shell [ -d $(PROJECT_BASE_LIB) ] && echo "exists"),,                                     \
   $(shell "Could not find PROJECT_BASE_LIB '$(PROJECT_BASE_LIB)'")                             \
   $(shell "You need to point PROJECT_BASE_DIR to the directory containing the .make library")  \
   $(error "Invalid PROJECT_BASE_LIB"))

include $(PROJECT_BASE_LIB)/defines.mk

LESS_CSS_DIRS               = assets/css assets/css/libs
LESS_CSS_SOURCE_SUFFIX      = less
LESS_CSS_TARGET_SUFFIX      = css
LESS_CSS_PROG_EC2           = /stamped/node/node_modules/less/bin/lessc
LESS_CSS_PROG               = $(if $(call EXISTS,$(LESS_CSS_PROG_EC2)),$(LESS_CSS_PROG_EC2),lessc)
LESS_CSS_SOURCES            = $(strip \
    $(foreach DIR,$(LESS_CSS_DIRS),$(wildcard $(DIR)/*.$(LESS_CSS_SOURCE_SUFFIX))))
LESS_CSS_TARGETS            = $(LESS_CSS_SOURCES:%.$(LESS_CSS_SOURCE_SUFFIX)=%.$(LESS_CSS_TARGET_SUFFIX))

JS_BASE_DIR					= assets/js
CSS_BASE_DIR				= assets/css
HTML_BASE_DIR				= html
HTML_SUFFIX					= html
HTML_PAGES					= profile map
GET_JS_DEPENDENCIES			= $(foreach FILE,$(shell grep '^[ \t]*script:[ \t]*' $1 | sed 's/[ \t]*script:[ \t]*\([\w.\/-]*\)[ \t]*/\1/g' | tr '\n' ' '),$(JS_BASE_DIR)/$(FILE))
GET_CSS_DEPENDENCIES		= $(foreach FILE,$(shell grep '^[ \t]*stylesheet:[ \t]*' $1 | sed 's/[ \t]*stylesheet:[ \t]*\([\w.\/-]*\)[ \t]*/\1/g' | tr '\n' ' '),$(CSS_BASE_DIR)/$(FILE))
JS_TARGETS					= $(foreach PAGE,$(HTML_PAGES),$(JS_BASE_DIR)/$(PAGE).generated.js)
CSS_TARGETS					= $(foreach PAGE,$(HTML_PAGES),$(CSS_BASE_DIR)/$(PAGE).generated.css)

TEMPLATE_DIRS				= templates
TEMPLATE_SUFFIX				= template.html
TEMPLATE_DEST				= $(strip $(call FIRST,$(TEMPLATE_DIRS)))/templates.generated.html
TEMPLATE_PROG				= bin/process_templates.py
TEMPLATES 					= $(strip \
	$(foreach DIR,$(TEMPLATE_DIRS),$(wildcard $(DIR)/*.$(TEMPLATE_SUFFIX))))

DEPENDENCIES				= $(TEMPLATES) $(TEMPLATE_PROG) $(wildcard core/templatetags/*.py)
ALL_TARGETS					= $(TEMPLATE_DEST) $(LESS_CSS_TARGETS) $(JS_TARGETS)

define ADD_LESS_CSS_TARGET
$1/%.$(LESS_CSS_TARGET_SUFFIX): $1/%.$(LESS_CSS_SOURCE_SUFFIX)
	@$$(CECHO) "$(LESS_CSS_PROG) '$$(BOLD_COLOR)$$(FR_COLOR_RED)$$<$$(END_COLOR)' > '$$(BOLD_COLOR)$$(FR_COLOR_GREEN)$$@$$(END_COLOR)'."
	@$(LESS_CSS_PROG) $$< > $$@
	@echo
endef

define ADD_JS_TARGET
$(JS_BASE_DIR)/$1.generated.js: $(HTML_BASE_DIR)/$1.$(HTML_SUFFIX) $(call GET_JS_DEPENDENCIES,$(HTML_BASE_DIR)/$1.$(HTML_SUFFIX))
	@$$(CECHO) "cat $$(BOLD_COLOR)$$(FR_COLOR_RED)$$(call REST,$$^)$$(END_COLOR) | java -jar bin/compressor.jar --type js --line-break 120 > '$$(BOLD_COLOR)$$(FR_COLOR_GREEN)$$@$$(END_COLOR)'."
	@cat $$(call REST,$$^) | java -jar bin/compressor.jar --type js --nomunge --line-break 120 > $$@
	@echo
endef

define ADD_CSS_TARGET
$(CSS_BASE_DIR)/$1.generated.css: $(HTML_BASE_DIR)/$1.$(HTML_SUFFIX) $(call GET_CSS_DEPENDENCIES,$(HTML_BASE_DIR)/$1.$(HTML_SUFFIX))
	cat $$(call REST,$$^) | java -jar bin/compressor.jar --type css --line-break 120 > $$@
	@echo
endef

all: $(ALL_TARGETS)

.PHONY: $(TEMPLATE_DEST) all clean help

$(TEMPLATE_DEST): $(DEPENDENCIES)
	$(TEMPLATE_PROG) -o $(TEMPLATE_DEST)
	@$(CECHO) "Created '$(BOLD_COLOR)$(FR_COLOR_RED)$(TEMPLATE_DEST)$(END_COLOR)'."
	@echo

$(foreach DIR,$(LESS_CSS_DIRS),$(eval $(call ADD_LESS_CSS_TARGET,$(DIR))))

$(foreach PAGE,$(HTML_PAGES),$(eval $(call ADD_JS_TARGET,$(PAGE))))

#$(foreach PAGE,$(HTML_PAGES),$(eval $(call ADD_CSS_TARGET,$(PAGE))))

clean:
	$(RM) -f $(ALL_TARGETS)
	@echo

help::
	@$(CECHO) "$(FR_COLOR_RED)Usage:$(END_COLOR) make [target1 ...]"
	@echo "   * the default target is 'all'"
	@echo

