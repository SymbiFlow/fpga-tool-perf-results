#!/bin/bash
# Copyright (C) 2021  The SymbiFlow Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

source env/bin/activate
yapf -i $(find . -maxdepth 1 -name "*py") setup.py
test $(git status --porcelain | wc -l) -eq 0 || { git diff; false;  }
