#!/usr/bin/env bash
ENNY_URL=http://127.0.0.1:5001
for i in $(cat NDX); do
    curl $ENNY_URL/api/v1.0/collector/collect/$i
    sleep 13
done
