# Makefile
# 
#     Contains dependency logic for preprocessing and optimizing resources 
# used by the main Stamped website. Also contains logic for collecting and 
# deploying assets to our cloud infrastructure (e.g., dev and prod).
# 
# @author:    Stamped (dev@stamped.com)
# @copyright: (c) 2011-2012 Stamped.com

override PROJECT_BASE_DIR	= .
override PROJECT_BASE_LIB	= $(PROJECT_BASE_DIR)/.make

LESS_CSS_DIRS				= assets/css assets/css/libs
LESS_CSS_SOURCE_SUFFIX		= less
LESS_CSS_TARGET_SUFFIX		= css
LESS_CSS_PROG				= /stamped/node/node_modules/less/bin/lessc
LESS_CSS_SOURCES			= $(strip \
	$(foreach DIR,$(LESS_CSS_DIRS),$(wildcard $(DIR)/*.$(LESS_CSS_SOURCE_SUFFIX))))
LESS_CSS_TARGETS			= $(LESS_CSS_SOURCES:%.$(LESS_CSS_SOURCE_SUFFIX)=%.$(LESS_CSS_TARGET_SUFFIX))

TEMPLATE_DIRS				= templates
TEMPLATE_SUFFIX				= template.html
TEMPLATE_DEST				= $(strip $(call FIRST,$(TEMPLATE_DIRS)))/templates.generated.html
TEMPLATE_PROG				= ./process_templates.py
TEMPLATES 					= $(strip \
	$(foreach DIR,$(TEMPLATE_DIRS),$(wildcard $(DIR)/*.$(TEMPLATE_SUFFIX))))

DEPENDENCIES				= $(TEMPLATES) $(TEMPLATE_PROG) \
	assets/js/libs/mustache.js core/templatetags/stamped_tags.py

ALL_TARGETS					= $(TEMPLATE_DEST) $(LESS_CSS_TARGETS)

define ADD_TARGET_PATTERN
$1/%.$(LESS_CSS_TARGET_SUFFIX): $1/%.$(LESS_CSS_SOURCE_SUFFIX)
	@$$(CECHO) "$(LESS_CSS_PROG) '$$(BOLD_COLOR)$$(FR_COLOR_RED)$$<$$(END_COLOR)' > '$$(BOLD_COLOR)$$(FR_COLOR_GREEN)$$@$$(END_COLOR)'."
	@$(LESS_CSS_PROG) $$< > $$@
	@echo
endef

all: $(ALL_TARGETS)

.PHONY: $(TEMPLATE_DEST) all clean help

$(TEMPLATE_DEST): $(DEPENDENCIES)
	$(TEMPLATE_PROG) -o $(TEMPLATE_DEST)
	@$(CECHO) "Created '$(BOLD_COLOR)$(FR_COLOR_RED)$(TEMPLATE_DEST)$(END_COLOR)'."
	@echo

$(foreach DIR,$(LESS_CSS_DIRS),$(eval $(call ADD_TARGET_PATTERN,$(DIR))))

clean:
	-$(RM) -f $(ALL_TARGETS)
	@echo

help::
	@$(CECHO) "$(FR_COLOR_RED)Usage:$(END_COLOR) make [target1 ...]"
	@echo "   * the default target is 'all'"
	@echo

# Sanity-check PROJECT_BASE_DIR and PROJECT_BASE_LIB
$(if $(shell [ -d $(PROJECT_BASE_LIB) ] && echo "exists"),, 									\
   $(shell "Could not find PROJECT_BASE_LIB '$(PROJECT_BASE_LIB)'") 							\
   $(shell "You need to point PROJECT_BASE_DIR to the directory containing the .make library") 	\
   $(error "Invalid PROJECT_BASE_LIB"))

include $(PROJECT_BASE_LIB)/defines.mk

