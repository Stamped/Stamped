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

ASSET_VERSION_NUMBER        = 1.1.13
GENERATED_ASSET_SUFFIX		= .generated.$(ASSET_VERSION_NUMBER)
ASSET_VERSION_SUFFIX		= .$(ASSET_VERSION_NUMBER)
GENERATED_LINE_LENGTH		= 512

LESS_CSS_DIRS               = assets/css assets/css/libs assets/css/ie assets/css/mobile
LESS_CSS_SOURCE_SUFFIX      = less
LESS_CSS_TARGET_SUFFIX      = css
LESS_CSS_PROG_EC2           = /stamped/node/node_modules/less/bin/lessc
LESS_CSS_PROG               = $(if $(call EXISTS,$(LESS_CSS_PROG_EC2)),$(LESS_CSS_PROG_EC2),lessc)
LESS_CSS_SOURCES            = $(strip \
    $(foreach DIR,$(LESS_CSS_DIRS),$(wildcard $(DIR)/*.$(LESS_CSS_SOURCE_SUFFIX))))
LESS_CSS_TARGETS            = $(LESS_CSS_SOURCES:%.$(LESS_CSS_SOURCE_SUFFIX)=%.$(LESS_CSS_TARGET_SUFFIX))

GENERATED_BASE_DIR			= assets/generated
GENERATED_JS_BASE_DIR		= $(GENERATED_BASE_DIR)/js
GENERATED_CSS_BASE_DIR		= $(GENERATED_BASE_DIR)/css
JS_BASE_DIR					= assets/js
CSS_BASE_DIR				= assets/css
HTML_BASE_DIR				= html
HTML_SUFFIX					= html
TEMPLATE_BASE_DIR		    = templates
HTML_PAGES					= base profile index map about jobs retina
TEMPLATE_PROG				= bin/process_templates.py

GET_JS_DEPENDENCIES			= $(foreach FILE,$(shell grep '^[ \t]*script:[ \t]*' $1 | sed 's/[ \t]*script:[ \t]*\([\w.\/-]*\)[ \t]*/\1/g' | tr '\n' ' '),$(JS_BASE_DIR)/$(FILE))
GET_CSS_DEPENDENCIES		= $(foreach FILE,$(shell grep '^[ \t]*stylesheet:[ \t]*' $1 | sed 's/[ \t]*stylesheet:[ \t]*\([\w.\/-]*\)[ \t]*/\1/g' | tr '\n' ' '),$(CSS_BASE_DIR)/$(FILE))
GET_TEMPLATE_DEPENDENCIES	= $(foreach FILE,$(shell grep '^[ \t]*template:[ \t]*' $1 | sed 's/[ \t]*template:[ \t]*\([\w.\/-]*\)[ \t]*/\1/g' | tr '\n' ' '),$(TEMPLATE_BASE_DIR)/$(FILE))

JS_TARGETS					= $(foreach PAGE,$(HTML_PAGES),$(GENERATED_JS_BASE_DIR)/$(PAGE)$(GENERATED_ASSET_SUFFIX).js)
CSS_TARGETS					= $(foreach PAGE,$(HTML_PAGES),$(GENERATED_CSS_BASE_DIR)/$(PAGE)$(GENERATED_ASSET_SUFFIX).css)
TEMPLATE_TARGETS			= $(foreach PAGE,$(HTML_PAGES),$(TEMPLATE_BASE_DIR)/$(PAGE).generated.html)

#TEMPLATE_DIRS				= templates
#TEMPLATE_SUFFIX				= template.html
#TEMPLATE_DEST				= $(strip $(call FIRST,$(TEMPLATE_DIRS)))/templates.generated.html
TEMPLATES 					= $(strip \
	$(foreach DIR,$(TEMPLATE_DIRS),$(wildcard $(DIR)/*.$(TEMPLATE_SUFFIX))))

DEPENDENCIES				= $(TEMPLATES) $(TEMPLATE_PROG) $(wildcard core/templatetags/*.py)
ALL_TARGETS					= $(LESS_CSS_TARGETS) $(JS_TARGETS) $(TEMPLATE_TARGETS) css_targets $(CSS_TARGETS)

define ADD_LESS_CSS_TARGET
$1/%.$(LESS_CSS_TARGET_SUFFIX): $1/%.$(LESS_CSS_SOURCE_SUFFIX)
	@$$(CECHO) "$(LESS_CSS_PROG) $$(BOLD_COLOR)$$(FR_COLOR_RED)$$<$$(END_COLOR) > $$(BOLD_COLOR)$$(FR_COLOR_GREEN)$$@$$(END_COLOR)"
	@$(LESS_CSS_PROG) $$< > $$@
	@echo
endef

define ADD_JS_TARGET
$(GENERATED_JS_BASE_DIR)/$1$(GENERATED_ASSET_SUFFIX).js: $(HTML_BASE_DIR)/$1.$(HTML_SUFFIX) $(call GET_JS_DEPENDENCIES,$(HTML_BASE_DIR)/$1.$(HTML_SUFFIX))
	@mkdir -p $(GENERATED_JS_BASE_DIR)
	@$$(CECHO) "cat $$(BOLD_COLOR)$$(FR_COLOR_RED)$$(if $$(call ISNULL,$$(strip $$(call REST,$$^))),/dev/null,$$(call REST,$$^))$$(END_COLOR) | java -jar bin/compressor.jar --type js --line-break $(GENERATED_LINE_LENGTH) > '$$(BOLD_COLOR)$$(FR_COLOR_GREEN)$$@$$(END_COLOR)'"
	@cat $$(if $$(call ISNULL,$$(strip $$(call REST,$$^))),/dev/null,$$(call REST,$$^)) | java -jar bin/compressor.jar --type js --nomunge --line-break $(GENERATED_LINE_LENGTH) > $$@
	@echo
endef

define ADD_CSS_TARGET
$(GENERATED_CSS_BASE_DIR)/$1$(GENERATED_ASSET_SUFFIX).css: $(HTML_BASE_DIR)/$1.$(HTML_SUFFIX) css_targets $(call GET_CSS_DEPENDENCIES,$(HTML_BASE_DIR)/$1.$(HTML_SUFFIX))
	@mkdir -p $(GENERATED_CSS_BASE_DIR)
	cat $$(call REST,$$(call REST,$$^)) | java -jar bin/compressor.jar --type css --line-break $(GENERATED_LINE_LENGTH) > $$@
	@echo
endef

define ADD_TEMPLATE_TARGET
$(TEMPLATE_BASE_DIR)/$1.generated.html: $(HTML_BASE_DIR)/$1.$(HTML_SUFFIX) $(call GET_TEMPLATE_DEPENDENCIES,$(HTML_BASE_DIR)/$1.$(HTML_SUFFIX))
	@$$(CECHO) "$(TEMPLATE_PROG) $$(foreach FILE,$$(call REST,$$^),-t $$(BOLD_COLOR)$$(FR_COLOR_RED)$$(notdir $$(FILE))$$(END_COLOR)) -o $$(BOLD_COLOR)$$(FR_COLOR_GREEN)$$@$$(END_COLOR)"
	@$(TEMPLATE_PROG) $$(foreach FILE,$$(call REST,$$^),-t $$(notdir $$(FILE))) -o $$@
	@echo
endef

all: $(ALL_TARGETS)

.PHONY: all clean help update_version deploy css_targets

$(foreach DIR,$(LESS_CSS_DIRS),$(eval $(call ADD_LESS_CSS_TARGET,$(DIR))))
$(foreach PAGE,$(HTML_PAGES),  $(eval $(call ADD_JS_TARGET,$(PAGE))))
$(foreach PAGE,$(HTML_PAGES),  $(eval $(call ADD_TEMPLATE_TARGET,$(PAGE))))
$(foreach PAGE,$(HTML_PAGES),  $(eval $(call ADD_CSS_TARGET,$(PAGE))))

css_targets: $(LESS_CSS_TARGETS);

deploy: $(ALL_TARGETS)
	cd bin && python deploy_assets.py

update_version:
	@echo $(ASSET_VERSION_NUMBER)
	cd bin && python deploy_version.py

version:
	@echo $(ASSET_VERSION_NUMBER)

clean:
	$(RM) -rf $(GENERATED_BASE_DIR)
	$(RM) -f  $(ALL_TARGETS)
	@echo

help::
	@$(CECHO) "$(FR_COLOR_RED)Usage:$(END_COLOR) make [target1 ...]"
	@echo "   * the default target is 'all'"
	@echo

