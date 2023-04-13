#!/bin/bash
source .venv/bin/activate && zappa undeploy dev ; zappa deploy dev
