#!/bin/bash

if [ -n "${BITBUCKET_OWNER}" ]; then
    return
fi

# START INSTALLER MAGIC ! DO NOT EDIT !
BITBUCKET_OWNER="bitbucket"
# END INSTALLER MAGIC ! DO NOT EDIT !

export BITBUCKET_OWNER
