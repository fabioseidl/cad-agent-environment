# Convenience targets. Everything delegates to .agents/tools/cad.
CAD := .agents/tools/cad

.PHONY: help image doctor test example clean

help:
	@echo "make image    build the CAD Docker image"
	@echo "make doctor   verify the toolchain"
	@echo "make test     run the smoke tests in the container"
	@echo "make example  build the example project"
	@echo "make clean    remove generated projects/*/output"
	@echo ""
	@echo "Day to day, call the CLI directly: $(CAD) build <project>"

image:
	CAD_BUILD=1 $(CAD) doctor

doctor:
	$(CAD) doctor

test:
	$(CAD) run tests/test_cadkit.py

example:
	$(CAD) build example-wall-bracket

clean:
	rm -rf projects/*/output
