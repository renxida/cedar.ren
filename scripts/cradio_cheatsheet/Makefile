.PHONY: build validate all clean

all: validate build

validate:
	@uv run validate.py

build:
	@uv run build.py

clean:
	@rm -f /Users/cedar/cedar.ren/pages/cradio_android/v2-technical-manual.html
	@rm -f /Users/cedar/cedar.ren/pages/cradio_android/v3-tech-manual-dark.html
	@echo "removed generated files"
