"""RT - Recipe Tool: pack, install and automate projects with plain-text recipes."""

try:
    from .buildnum import num as BUILD
except ImportError:  # not generated (running from a source checkout without build.sh)
    BUILD = "dev"

UPDATE_URL = "https://github.com/ojotuno/rt/releases/download/lastest/rt.rt"
