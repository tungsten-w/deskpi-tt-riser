PY ?= .venv/bin/python
BLENDER ?= blender

.PHONY: all stl images clean

all: stl images

# checks + every STL + numbered print sets
stl:
	$(PY) cad/riser.py

# renders (Blender, CPU) + labels
images: stl
	$(PY) cad/previews.py
	$(BLENDER) -b -P cad/render_previews.py
	$(PY) cad/mounting_models.py
	$(BLENDER) -b -P cad/render_mounting.py
	$(PY) cad/annotate_mounting.py

clean:
	rm -rf build
