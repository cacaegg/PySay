SAYFILES=builtin.say usbxcli.say profile.say testcase.say testcase_demo.say
TRANSLATOR=racket ../translator/translator.rkt

all: $(SAYFILES) builtin.pys usbxcli.pys profile.pys testcase.pys testcase_demo.pys

builtin.pys: builtin.say
	$(TRANSLATOR) < builtin.say > builtin.pys

usbxcli.pys: usbxcli.say
	$(TRANSLATOR) < usbxcli.say > usbxcli.pys

profile.pys: profile.say
	$(TRANSLATOR) < profile.say > profile.pys

testcase.pys: testcase.say
	$(TRANSLATOR) < testcase.say > testcase.pys

testcase_demo.pys: testcase_demo.say
	$(TRANSLATOR) < testcase_demo.say > testcase_demo.pys
