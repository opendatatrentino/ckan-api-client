#!/bin/bash

# Perform "inline" cleanup of a dataset, using a temporary file

TEMPFILE="$( tempfile )"

if [ -z "$1" ]; then
    echo "Usage: $0 <files..>"
    exit 1
fi

JQ_QUERY="{author,author_email,extras,groups,id,license_id,maintainer,"
JQ_QUERY+="maintainer_email,name,notes,owner_org,private,relationships,"
JQ_QUERY+="resources: [.resources[] | {url,url_type,format,description,"
JQ_QUERY+="name,resource_type}],state,tags,title,type,url}"

for INPUT in "$@"; do
    cat "$INPUT" | jq --sort-keys "$JQ_QUERY" > "$TEMPFILE"
    cat "$TEMPFILE" > "$INPUT"
done

rm "$TEMPFILE"
