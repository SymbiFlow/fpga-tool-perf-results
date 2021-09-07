# Copyright (C) 2021  The Symbiflow Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

SHELL=bash

PYTHON:=python3

PYTHON_SRCS=$(shell find . -maxdepth 1 -name "*py")

IN_ENV = if [ -e env/bin/activate ]; then . env/bin/activate; fi;
env:
	git submodule update --init --recursive
	virtualenv --python=$(PYTHON) env
	$(IN_ENV) pip install --no-cache-dir --upgrade -r requirements.txt

fetch:
	mkdir -p meta
	$(IN_ENV) python fetch_meta.py nightly 1138 _ meta --pool-size $$(nproc)

build:
	mkdir -p build
	$(IN_ENV) python gen.py meta -o build
	touch build/.nojekyll

format: ${PYTHON_SRCS}
	$(IN_ENV) yapf -i ${PYTHON_SRCS} setup.py

clean:
	rm -rf env

.PHONY: clean env fetch build format
